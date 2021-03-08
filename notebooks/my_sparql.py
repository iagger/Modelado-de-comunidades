import re
import json
from os import path
import pandas as pd
import ast
from collections import OrderedDict
from json.decoder import JSONDecodeError
from SPARQLWrapper import SPARQLWrapper, JSON
from IPython.display import display 
      
def sparqlQuery(query=None):
    if not query==None:
        wrapper = SPARQLWrapper("https://query.wikidata.org/sparql")
        wrapper.setQuery(query)
        wrapper.setReturnFormat(JSON)
        return wrapper.query().convert()
    
def resultAsDict(result=None):
    if result == None:
        return {}
    var = result['head']['vars']
    if (len(var) > 2):
        raise ValueError('More than 2 results vars')
    dic = {}
    for item in result['results']['bindings']:
        dic.update({ extractEntityFromWikidataURL(item[var[0]]['value']) : item[var[1]]['value'] })
    return dic

def resultAsList(result=None):
    if result == None:
        return {}
    var = result['head']['vars']
    if (len(var) > 1):
        raise ValueError('More than 1 results vars')
    l = []
    for item in result['results']['bindings']:
        l.append(extractEntityFromWikidataURL(item[var[0]]['value']))
    return l

def resultAsDataframe(result=None):
    if result == None:
        return None
    df = pd.DataFrame(columns=result['head']['vars'])
    for item in result['results']['bindings']:
        df = df.append(dict(map(lambda kv: (kv[0], kv[1]['value']), item.items())), True)
    return df

def extractEntityFromWikidataURL(url):
    if (not bool(re.match("http://www.wikidata.org/entity/Q[0-9]*", url))):
        return url
    return url[url.rindex("/")+1:]

class CachedSuperclassRetreiver:
    
    def __init__(self, cacheFile='superclass_cache.csv', maxCacheSize=100):
        self._cacheFile_ = cacheFile
        self._maxCacheSize_ = maxCacheSize
        self.__newlyCached__ = 0
        try:
            self._queryCache_ = pd.read_csv(self._cacheFile_)
        except Exception:
            self._queryCache_ = pd.DataFrame(columns=['Entity', 'Super'])

    def superclassOf(self, entity=None):
        if entity == None:
            return None
        else:
            cacheQuery = self._queryCache_.loc[self._queryCache_['Entity']==entity]['Super'].to_list()
            if len(cacheQuery):
                if type(cacheQuery[0]) != list:
                    return ast.literal_eval(cacheQuery[0])
                return cacheQuery[0]
            else:
                data = sparqlQuery("SELECT DISTINCT ?instance WHERE {" \
                        "   wd:" + entity + " wdt:P279|wdt:P31 ?instance." \
                        "   SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". }" \
                        "}" \
                        "LIMIT 100")

                data = resultAsList(data)

                self._queryCache_.loc[len(self._queryCache_.index)] = [entity, data]
                self.__newlyCached__ += 1
                return data

    def close(self):
        if self.__newlyCached__:
            self._queryCache_.to_csv(self._cacheFile_, index=False)

               
            
        