import ast
import logging
import numpy as np
import pandas as pd
from setup import PATHS
from genal import GeneticAlgorithm
from artwork_similarity import ArtworkSimilarity, checkWeights

# Cargamos los conjuntos de datos relacionados con las respuestas de ususarios con respecto a la similitud
answers = pd.read_json(PATHS["SIMILARITY_ANSWERS"])[['userId', 'image1', 'image2', 'similarity']]
asked = pd.read_csv(PATHS["ASKED_USERS"])[['userCategory', 'userId']]
artworks = pd.read_csv(PATHS["ARTWORKS_DATA"])['wd:paintingID'].to_list()

# Extraemos las listas de profesionales y amateurs
asked['userCategory'] = asked['userCategory'].apply(lambda x : ast.literal_eval(x))
asked['userCategory'] = asked['userCategory'].apply(lambda x : x[0] if len(x) else None)
professionals = asked.loc[asked['userCategory'] == 'Professional']['userId'].to_list()
amateurs = asked.loc[asked['userCategory'] == 'Amateur']['userId'].to_list()

# Filtramos las respuestas de similitud por usuarios profesionales
answers = answers.loc[answers.userId.isin(professionals)] #| answers.userId.isin(amateurs)]

# Filtramos por los cuadros presentes en nuestro dataset
answers = answers.loc[answers.image1.isin(artworks) & answers.image2.isin(artworks)] 

logging.basicConfig(filename="data/log/weightSearchProfessionals.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s -> %(message)s')

def fitness(x):
    error = .0
    N = 0
    for _, row in answers.iterrows():
        estimatedSim = ArtworkSimilarity(row['image1'], row['image2'], x) * 5
        error += abs(row['similarity'] - estimatedSim)
        N += 1
    logging.info("Weights " + str(checkWeights(x, len(x))) + " got error " + str(error/N))
    return error/N

partials = 5
bounds = np.array([[1,10]]*partials)
params = {'iterations' : 100,
        'popSize' : 100,
        'crossoverProb' : 0.4,
        'mutationProb' : 0.15,
        'elitePerc' : 0.02,
        'crossoverMethod' : 'onePoint'  }

gen = GeneticAlgorithm(fitness, partials, bounds, params)
gen.run()

results = gen.getResults()
best_ch = checkWeights(results['chromosome'], partials)
best_sc = results['value']

logging.info("Search ended with WEIGHTS " + str(best_ch) + " and score " + str(best_sc))