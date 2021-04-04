import pandas as pd
import numpy as np
import operator
from artwork_similarity import *

emotions = '../data/originales/Prado_emotions.csv'
emotionsData = pd.read_csv(emotions)

artWorks = '../data/originales/Prado_artworks_wikidata.csv'
artWorksData = pd.read_csv(artWorks)

# Devuelve el conjunto de todos los cuadros que tienen una polaridad positiva para una persona
def myFavouriteArtworks(userId, polarity):
    return np.array(emotionsData[emotionsData['userId'] == userId][emotionsData[polarity] == 'positive']['artworkId'])

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

# Devuelve el indice de similitud jaccard entre los conjuntos (dadas dos personas) de cuadros que les gustan y sus similares
def jaccardSimilarityCoefficientScore(userId1, userId2, polarity='positive'):
    artWorks1 = similarArtworks(userId1, polarity)
    artWorks2 = similarArtworks(userId2, polarity)
    intersection = set(artWorks1).intersection(set(artWorks2))
    listIntersection = list(intersection)
    union = set(artWorks1).union(set(artWorks2))
    listUnion = list(union)
    return  (len(intersection)) / (len(union))