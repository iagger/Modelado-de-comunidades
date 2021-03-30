from sklearn import datasets
import pandas as pd
import numpy as np
import requests
import helpers
import re
import json
from os import path
from collections import OrderedDict
from json.decoder import JSONDecodeError
from SPARQLWrapper import SPARQLWrapper, JSON
from math import sqrt
from my_sparql import sparqlQuery, extractEntityFromWikidataURL

artworks = pd.read_csv('../data/originales/Prado_artworks_wikidata.csv')

def artistSimilarity(entity1, entity2):
    if artworks.loc[artworks['wd:paintingID'] == entity1]['Artist'].to_list()[0] == artworks.loc[artworks['wd:paintingID'] == entity2]['Artist'].to_list()[0]:
        return 1.
    if artworks.loc[artworks['wd:paintingID'] == entity1]['Category'].to_list()[0] == artworks.loc[artworks['wd:paintingID'] == entity2]['Category'].to_list()[0]:
        return .5
    return .0

# Funcion devuelve el ancho de un cuadro
def getWidth(entity=None):
    widthQuery = sparqlQuery("SELECT ?width WHERE {" \
                " wd:" + entity + " wdt:P2049 ?width." \
                " SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". }" \
                "}")
    if len(widthQuery['results']['bindings']) == 0:
        print(entity,"\n")
    else:
        return widthQuery['results']['bindings'][0]['width']['value']

# Funcion devuelve el alto de un cuadro
def getHeight (entity=None):
    heightQuery = sparqlQuery ("SELECT ?height WHERE {" \
                " wd:" + entity + " wdt:P2048 ?height." \
                " SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". }" \
                "}")
    if len(heightQuery['results']['bindings']) == 0:
        print(entity,"\n")
    else:
        return heightQuery['results']['bindings'][0]['height']['value']

# Devuelve un area
def getArea(width, height):
    return width*height

# Devuelve el area de un cuadro dado una entidad
def paintingArea(entity):
    width = getWidth(entity)
    height = getHeight(entity)
    if width == None or height == None:
        return 0
    return getArea(float(width), float(height))

# Devuelve la similitud en porcentaje y sobre (1-0) de dos entidades a traves del area que ocupan las pinturas
def simalityAreaFromEntities(entity1, entity2):
    area1 = paintingArea(entity1)
    area2 = paintingArea(entity2)
    return min(area1, area2) / max(area1, area2)

# Devuelve la similitud en porcentaje y sobre (1-0) de dos urls a traves del area que ocupan las pinturas
def simalityAreaFromURLs(url1, url2):
    entity1 = extractEntityFromWikidataURL(url1)
    entity2 = extractEntityFromWikidataURL(url2)
    return simalityFromAreaEntities(entity1, entity2)