from cached_similarity import CachedSimilarity
import json

PATHS = json.load(open("configuration.cfg"))["PATHS"]

################################################################################
############################## Depicts Similarity ##############################
################################################################################

import math
import ast
import multiprocessing
import numpy as np
from collections import OrderedDict
from my_sparql import PropertyRetreiver
from joblib import Parallel, delayed
from sklearn.metrics.pairwise import cosine_similarity

def minPath(a, b):
    if sum(a) < sum(b) or (sum(a) == sum(b) and max(a) < max(b)):
        return a
    return b

def findLeastCommonSubsumer(entity_a, entity_b, ret, max_depth=1):  
    '''
    Busca el antepasado común más cercano de dos entidades en la profundidad máxima indicada

    PARÁMETROS
        entity_a, entity_b  entidades para las que se busca antepasado común
        ret                 recuperador de superclases del tipo my_sparql.PropertyRetriever
        max_depth           profundidad máxima de la búsqueda
    DEVUELVE
        entities    tupla con las entidades objeto de la búsqueda
        lcs         antepasado común más cercano. None si no se encuentra ninguo
        path        tupla que indica la distancia de cada entidad inicial al antepasado común. (-1, -1) si no se encuentra ninguo
    '''
    # Estructuras auxiliares para almacenar los antepasados encontrados y en que profundidad se hizo 
    depths_a = { entity_a : 0 }
    depths_b = { entity_b : 0 }

    for i in range(0, max_depth + 1):   
        # Si existe una intersección entre los conjuntos de antepasados encontrados
        intersection = set([*depths_a]) & set([*depths_b])  
        if len(intersection):
            # Devolvemos el antepasado con camino más corto de todos los comunes encontrados
            path = (math.inf, math.inf)
            lcs = None
            for common in list(intersection):
                new_path = minPath(path, (depths_a.get(common), depths_b.get(common)))
                if new_path != path:
                    lcs = common
                path = new_path
            return (entity_a, entity_b), lcs, path
        # Si no añadimos a las estructuras los antepasados de los elementos recuperados en la profundidad anterior
        else:
            for sa in [x for x in [*depths_a] if depths_a.get(x) == i]:
                depths_a |= dict([(k, min(i+1, depths_a.get(k, math.inf))) for k in ret.retrieveFor(sa)])
            for sb in [y for y in [*depths_b] if depths_b.get(y) == i]:
                depths_b |= dict([(k, min(i+1, depths_b.get(k, math.inf))) for k in ret.retrieveFor(sb)])
    
    return (entity_a, entity_b), None, (-1, -1)

class DepictsSimilarity(CachedSimilarity):

    def __init__(self, depth=1, cache_dir=PATHS['CACHE']):
        super().__init__('artworkSimilarity.depicts.depth' + str(depth), cache_dir)
        self.__superclassRetreiver__ = PropertyRetreiver(['P279', 'P31'])
        self.__depictsRetreiver__ = PropertyRetreiver(['P180'])
        self.__maxdepth__ = depth
    
    # overriding abstract method
    def computeSimilarity(self, A, B):
        A = set(self.__depictsRetreiver__.retrieveFor(A))
        B = set(self.__depictsRetreiver__.retrieveFor(B))
        intersection = A.intersection(B)
        exclusive_A = A.difference(B)
        exclusive_B = B.difference(A)

        # Creamos un diccionario de pesos para cada conjunto de depicts, poniendo peso 1. los presentes y 0. a los ausentes
        a = OrderedDict({k : 1. for k in exclusive_A} | {k : 0. for k in exclusive_B} | {k : 1. for k in intersection})
        b = OrderedDict({k : 0. for k in exclusive_A} | {k : 1. for k in exclusive_B} | {k : 1. for k in intersection})
        trash = set()
        commons = {}
        
        # Buscamos supercalses comunes para todos los depicts de A y B
        for depicts, lcs, path in Parallel(n_jobs=multiprocessing.cpu_count())(delayed(findLeastCommonSubsumer)(da, db, self.__superclassRetreiver__, self.__maxdepth__) for da in A for db in B):  
            if sum(path) > 0:
                trash.union({depicts[0], depicts[1]})
                commons[lcs] = path

        # Eliminamos de ambos diccionarios todos los depicts para los que hemos encontrado una superclase común   
        for t in trash:
            a.popitem(t)
            b.popitem(t)

        # Introducimos en ambos diccionarios los antepasados encontrados con peso inverso a la distancia que tenian con el depict original
        for lcs, path in commons.items():
            a[lcs] = 1 / path[0] if path[0] else 1
            b[lcs] = 1 / path[1] if path[1] else 1

        # Tomamos ambos vectores de pesos y calculamos la distancia del coseno entre ellos
        return cosine_similarity(np.array([[*a.values()]]), np.array([[*b.values()]]))[0][0]
    
    # overriding method to close both retreivers to
    def close(self):
        super().close()
        self.__superclassRetreiver__.close()
        self.__depictsRetreiver__.close()

################################################################################
############################### Size Similarity ################################
################################################################################

from my_sparql import PropertyRetreiver

class SizeSimilarity(CachedSimilarity):

    def __init__(self, cache_dir=PATHS['CACHE']):
        super().__init__('artworkSimilarity.picture.size', cache_dir)
        self.__heightRetriever__ = PropertyRetreiver(['P2048'])
        self.__widthRetriever__ = PropertyRetreiver(['P2049'])

    def __computeArea(self, Entity):
        width = self.__widthRetriever__.retrieveFor(Entity)
        height = self.__heightRetriever__.retrieveFor(Entity)
        if width == [] or height == []:
            return 0.
        return float(width[0]) * float(height[0])

    def computeSimilarity(self, A, B):
        area1 = self.__computeArea(A)
        area2 = self.__computeArea(B)
        return min(area1, area2) / max(area1, area2)

    def close(self):
        super().close()
        self.__heightRetriever__.close()
        self.__widthRetriever__.close()



################################################################################
########################## Dominant Color Similarity ###########################
################################################################################

import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import imageio as imio
from collections import Counter
from sklearn.cluster import KMeans
import colorsys
import math

class DominantColorSimilarity(CachedSimilarity):

    def __init__(self, artworks_CSV=PATHS['ARTWORKS_DATA'], cache_dir=PATHS['CACHE']):
        super().__init__('artworkSimilarity.picture.dominantColor', cache_dir)
        self.__pics__ = pd.read_csv(artworks_CSV)[['wd:paintingID', 'Image URL']] 

    def __colorPercentage(self, cluster):
        n_pixels = len(cluster.labels_)
        counter = Counter(cluster.labels_)  # count how many pixels per cluster
        perc = {}
        # Crea el vector de % dividiendo el numero de pixels de un cluster con el total
        for i in counter:
            perc[i] = np.round(counter[i] / n_pixels, 2)
        perc = dict(sorted(perc.items()))
        return perc


    def __dominantColor(self, entity):
        # Lee imagen
        url = self.__pics__.loc[self.__pics__['wd:paintingID'] == entity]['Image URL'].to_list()[0]
        img = imio.imread(url)
        # Hace Kmeans
        clt = KMeans(n_clusters=3)
        clt_1 = clt.fit(img.reshape(-1, 3))
        # Crea el array de porcentajes de color
        perc = self.__colorPercentage(clt_1)
        # Indice del color dominante
        max_color_key = max(perc, key=perc.get)
        # Valores RGB del color dominante
        max_color_rgb = clt_1.cluster_centers_[max_color_key]
        # RGB to HSV
        return colorsys.rgb_to_hsv(max_color_rgb[0], max_color_rgb[1], max_color_rgb[2])

    def computeSimilarity(self, A, B):
        a = self.__dominantColor(A)
        b = self.__dominantColor(B)
        dh = min(abs(a[0]-b[0]), 360-abs(a[0]-b[0])) / 180.0
        ds = abs(a[1] - b[1])
        dv = abs(a[2] - b[2]) / 255.
        distance = math.sqrt(dh * dh + ds * ds + dv * dv)
        return round(1. - (distance), 2)

################################################################################
############################## Artist Similarity ###############################
################################################################################

import pandas as pd

class ArtistSimilarity(CachedSimilarity):

    def __init__(self, artworks_CSV=PATHS['ARTWORKS_DATA'], cache_dir=PATHS['CACHE']):
        super().__init__('artworkSimilarity.artist', cache_dir)
        self.__artist__ = pd.read_csv(artworks_CSV)[['wd:paintingID', 'Artist', 'Category']] 

    def __getArtist(self, entity):
        return self.__artist__.loc[self.__artist__['wd:paintingID'] == entity]['Artist'].to_list()[0]
        
    def __getCategory(self, entity):    
        return self.__artist__.loc[self.__artist__['wd:paintingID'] == entity]['Category'].to_list()[0]

    def computeSimilarity(self, A, B):
        if self.__getArtist(A) == self.__getArtist(B):
            return 1.
        if self.__getCategory(A) == self.__getCategory(B):
            return .75
        return .0   

    def close(self):
        super().close()


################################################################################
############################### MSE Similarity #################################
################################################################################

import pandas as pd
from skimage import img_as_float
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import normalized_root_mse
from skimage.transform import resize
from skimage import io

class ImageMSESimilarity(CachedSimilarity):

    def __init__(self, artworks_CSV=PATHS['ARTWORKS_DATA'], cache_dir=PATHS['CACHE']):
        super().__init__('artworkSimilarity.picture.mse_sim', cache_dir)
        self.__pics__ = pd.read_csv(artworks_CSV)[['wd:paintingID', 'Image URL']] 

    def __mse_ssim(self, url1, url2):

        img1 = img_as_float((io.imread(url1)))
        img2 = img_as_float((io.imread(url2)))

        if (img1.shape != img2.shape):
            max0 = max(img1.shape[0], img2.shape[0])
            max1 = max(img1.shape[1], img2.shape[1])
            img2 = resize(img2, (max0, max1))
            img1 = resize(img1, (max0, max1))

        mse = normalized_root_mse(img1, img2, normalization='min-max')
        simiStruc = ssim(img1 , img2 , multichannel = True)

        indiceSimilitud = ((1 - mse) + simiStruc) / 2

        return indiceSimilitud

    
    def computeSimilarity(self, A, B):
        url1 = self.__pics__.loc[self.__pics__['wd:paintingID'] == A]['Image URL'].to_list()[0]
        url2 = self.__pics__.loc[self.__pics__['wd:paintingID'] == B]['Image URL'].to_list()[0]
        return self.__mse_ssim(url1, url2)


##########################################################################################
################################## Artwork Similarity ####################################
##########################################################################################

import heapq
import numpy as np
import pandas as pd

Partial_Similarities = [DepictsSimilarity(4),
                        SizeSimilarity(),
                        DominantColorSimilarity(),
                        ArtistSimilarity(),
                        ImageMSESimilarity()]

PradoArtworks = pd.read_csv(PATHS['ARTWORKS_DATA'])

def checkWeights(weights):
    if not len(weights) or np.greater(round(sum(weights)), round(1)):
        return np.ones(len(Partial_Similarities)) * (1 / len(Partial_Similarities))
    else:
        return np.array(weights)

def ArtworkSimilarity(A, B, weights=[]):
    weights = checkWeights(weights)
    partials = []
    for partial in Partial_Similarities:
        partials.append(partial.getSimilarity(A, B))
    return (np.array(partials) * weights).sum()

def MostSimilarArtworks(artwork, k=5, weights=[]):
    q = []
    for _, row in PradoArtworks.iterrows():
        if row['wd:paintingID'] != artwork:
            heapq.heappush(q, (ArtworkSimilarity(artwork, row['wd:paintingID'], weights), row['wd:paintingID']))
    return heapq.nlargest(k, q)