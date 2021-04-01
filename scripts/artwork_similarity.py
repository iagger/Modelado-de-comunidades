from fcache.cache import FileCache

class CachedSimilarity():

    def __init__(self, appname, cache_dir='../data'):
        self._cacheFile_ = FileCache('communities.artworkSimilarity.' + appname, flag='cs', app_cache_dir=cache_dir)

    def computeSimilarity(self, A, B):
        raise NotImplementedError("Each subclass must implement this method")

    def __findSimilarity(self, A, B):
        if A in self._cacheFile_ and B in self._cacheFile_[A].keys():
            return self._cacheFile_[A][B], (A, B)
        if B in self._cacheFile_ and A in self._cacheFile_[B].keys():
            return self._cacheFile_[B][A], (B, A)
        return None, None    

    def __lenDict(self, Entity):
        if Entity not in self._cacheFile_:
            self._cacheFile_[Entity] = dict()
        return len(self._cacheFile_[Entity])
    
    def __storeSim(self, A, B, sim):
        len_a = self.__lenDict(A)
        len_b = self.__lenDict(B)
        if len_a < len_b:
            self._cacheFile_[A] |= {B : sim}
        else:
            self._cacheFile_[B] |= {A : sim}

    def getSimilarity(self, A, B, recompute=False):
        sim, coord = self.__findSimilarity(A, B)
        if sim is None or recompute:
            sim = self.computeSimilarity(A, B)
            if coord is None:
                self.__storeSim(A, B, sim)
            else:
                self._cacheFile_[coord[0]] |= { coord[1] : sim }
        return sim

    def close(self):
        self._cacheFile_.sync()
        self._cacheFile_.close()



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

def findLeastCommonSubsumer(depict_a, depict_b, ret, max_depth=1):
    # Almacenamos las profundidades 
    depths_a = { depict_a : 0 }
    depths_b = { depict_b : 0 }

    for i in range(0, max_depth + 1):   # Para max_depth profundizaciones
        intersection = set([*depths_a]) & set([*depths_b])  # Si a y b comparten una o más superclases
        if len(intersection): # Devolvemos la que minimice el camino de a-b
            path = (math.inf, math.inf)
            lcs = None
            for common in list(intersection):
                new_path = minPath(path, (depths_a.get(common), depths_b.get(common)))
                if new_path != path:
                    lcs = common
                path = new_path
            return (depict_a, depict_b), lcs, path
        else:
            for sa in [x for x in [*depths_a] if depths_a.get(x) == i]:
                depths_a |= dict([(k, min(i+1, depths_a.get(k, math.inf))) for k in ret.retrieveFor(sa)])
            for sb in [y for y in [*depths_b] if depths_b.get(y) == i]:
                depths_b |= dict([(k, min(i+1, depths_b.get(k, math.inf))) for k in ret.retrieveFor(sb)])
    
    return (depict_a, depict_b), None, (-1, -1)

class DepictsSimilarity(CachedSimilarity):

    def __init__(self, depth=1, cache_dir='../data/cache'):
        super().__init__('depicts.depth' + str(depth), cache_dir)
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
        a = OrderedDict({k : 1. for k in exclusive_A} | {k : 0. for k in exclusive_B} | {k : 1. for k in intersection})
        b = OrderedDict({k : 0. for k in exclusive_A} | {k : 1. for k in exclusive_B} | {k : 1. for k in intersection})
        trash = set()
        commons = {}
        
        for depicts, lcs, path in Parallel(n_jobs=multiprocessing.cpu_count())(delayed(findLeastCommonSubsumer)(da, db, self.__superclassRetreiver__, self.__maxdepth__) for da in A for db in B):  
            if sum(path) > 0:
                trash.union({depicts[0], depicts[1]})
                commons[lcs] = path

        for t in trash:
            a.popitem(t)
            b.popitem(t)

        for lcs, path in commons.items():
            a[lcs] = 1 / path[0] if path[0] else 1
            b[lcs] = 1 / path[1] if path[1] else 1

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

    def __init__(self, cache_dir='../data/cache'):
        super().__init__('picture.size', cache_dir)
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

    def __init__(self, artworks_CSV='../data/originales/Prado_artworks_wikidata.csv', cache_dir='../data/cache'):
        super().__init__('picture.dominantColor', cache_dir)
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

    def __init__(self, artworks_CSV='../data/originales/Prado_artworks_wikidata.csv', cache_dir='../data/cache'):
        super().__init__('artist', cache_dir)
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

    def __init__(self, artworks_CSV='../data/originales/Prado_artworks_wikidata.csv', cache_dir='../data/cache'):
        super().__init__('picture.mse_sim', cache_dir)
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

