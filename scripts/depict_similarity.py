import math
import ast
import multiprocessing
import numpy as np
import pandas as pd
from collections import OrderedDict
from my_sparql import CachedSuperclassRetreiver, sparqlQuery, extractEntityFromWikidataURL, resultAsList
from joblib import Parallel, delayed
from sklearn.metrics.pairwise import cosine_similarity

cachedDepicts = pd.read_csv('../data/Prado_artworks_depicts.csv')
defaultRetreiver = CachedSuperclassRetreiver()

def retriveDepicts(painting=None):
    if painting == None:
        return None
    
    cached = cachedDepicts.loc[cachedDepicts['wd:paintingID'] == painting]['depicts'].to_list()
    if cached:
        return [*ast.literal_eval(cached[0])]

    data = sparqlQuery("SELECT DISTINCT ?depicts WHERE { " \
            "    wd:" + painting + " wdt:P180 ?depicts." \
            "    SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". }" \
            "}" \
            "LIMIT 100")

    return resultAsList(data)

def minPath(a, b):
    if sum(a) < sum(b) or (sum(a) == sum(b) and max(a) < max(b)):
        return a
    return b

def findLeastCommonSubsumer(depict_a, depict_b, max_depth=1, retreiver=CachedSuperclassRetreiver(cacheFile='..\data\superclass_cache.csv')):
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
                depths_a |= dict([(k, min(i+1, depths_a.get(k, math.inf))) for k in retreiver.superclassOf(sa)])
            for sb in [y for y in [*depths_b] if depths_b.get(y) == i]:
                depths_b |= dict([(k, min(i+1, depths_b.get(k, math.inf))) for k in retreiver.superclassOf(sb)])
    
    return (depict_a, depict_b), None, (-1, -1)

def depictSetSimilarityCos(A, B, max_depth = 1, retreiver=CachedSuperclassRetreiver(cacheFile='..\data\superclass_cache.csv')):
    A = set(A)
    B = set(B)
    intersection = A.intersection(B)
    exclusive_A = A.difference(B)
    exclusive_B = B.difference(A)
    a = OrderedDict({k : 1. for k in exclusive_A} | {k : 0. for k in exclusive_B} | {k : 1. for k in intersection})
    b = OrderedDict({k : 0. for k in exclusive_A} | {k : 1. for k in exclusive_B} | {k : 1. for k in intersection})
    trash = set()
    commons = {}
    
    for depicts, lcs, path in Parallel(n_jobs=multiprocessing.cpu_count())(delayed(findLeastCommonSubsumer)(da, db, max_depth, retreiver) for da in A for db in B):  
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

def artworkDepictSimilarity(painting_a, painting_b, max_depth):
    A = retriveDepicts(painting_a)
    B = retriveDepicts(painting_b)
    return depictSetSimilarityCos(A, B, max_depth, defaultRetreiver)