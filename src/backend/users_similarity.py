import pandas as pd
import numpy as np
import operator
from artwork_similarity import *

PATHS = json.load(open("configuration.cfg"))["PATHS"]

emotionsData = pd.read_csv(PATHS['EMOTIONS_DATA'])
artWorksData = pd.read_csv(PATHS['ARTWORKS_DATA'])

# Devuelve el conjunto de todos los cuadros que tienen una polaridad positiva para una persona
def myFavouriteArtworks(userId, polarity):
    return np.array(emotionsData[emotionsData['userId'] == userId][emotionsData['Polarity'] == polarity]['artworkId'])

# Dado un id de un cuadro devuelve su qualificador wd
def idArtWorkToWD(idArtwork):
    return np.array(artWorksData[artWorksData['ID'] == idArtwork]['wd:paintingID'])[0]

# Dado un wd de un cuadro devuelve su identificador id
def wdArtWorkToId(wdArtwork):
    return np.array(artWorksData[artWorksData['wd:paintingID'] == wdArtwork]['ID'])

# Devuelve el conjunto de los cuadros con polaridad positiva mas los 5 cuadros mas similares. Sin repetidos.
def similarArtworks(userId):
    positiveArtworks = myFavouriteArtworks(userId)
    simlistWd = []
    for pstArt in positiveArtworks:
        simlist = MostSimilarArtworks(idArtWorkToWD(pstArt))
        aux = list(map(lambda x: x[1], simlist))
        simlistWd = np.concatenate((simlistWd, aux), axis=0)
    allArtWorks = np.unique(list(map(lambda x: wdArtWorkToId(x), simlistWd)))
    allArtWorks = np.concatenate((allArtWorks, positiveArtworks), axis=0)
    return np.array(allArtWorks)


################################################################################
############################## Jaccard Similarity ##############################
################################################################################

def jaccardSimilarityCoefficientScore(userId1, userId2, polarity='positive'):
    """
    Devuelve el indice de similitud jaccard entre los conjuntos (dadas dos personas) de cuadros que les gustan y sus similares
    
    PARÁMETROS
        userId1, userId2    IDs de los usuarios
        polarity            polaridad de los cuadros con que se mide la similitud
    DEVUELVE
    """
    artWorks1 = similarArtworks(userId1, polarity)
    artWorks2 = similarArtworks(userId2, polarity)
    intersection = set(artWorks1).intersection(set(artWorks2))
    listIntersection = list(intersection)
    union = set(artWorks1).union(set(artWorks2))
    listUnion = list(union)
    return  (len(intersection)) / (len(union))


################################################################################
############################ Average 1v1 Similarity ############################
################################################################################

def averagePairSimilarity(userId1, userId2, polarity='positive'):
    """
    Devuelve la similitud media de los cuadros que le gustan a ambos usuarios enfrentados uno a uno
    
    PARÁMETROS
        userId1, userId2    IDs de los usuarios
        polarity            polaridad de los cuadros con que se mide la similitud
    DEVUELVE
    """
    aw1 = myFavouriteArtworks(userId1, polarity)
    aw2 = myFavouriteArtworks(userId2, polarity)
    similarities = []
    for a1 in aw1: 
        for a2 in aw2:
            similarities.append(ArtworkSimilarity(idArtWorkToWD(a1), idArtWorkToWD(a2)))
    return np.average(np.array(similarities))