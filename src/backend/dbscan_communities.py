import logging
import numpy as np
import pandas as pd
from setup import PATHS, PARAMS
from sklearn.cluster import dbscan
from sklearn.metrics import silhouette_score
from users_similarity import JaccardUserSimilarity
from genal import GeneticAlgorithm
from artwork_similarity import Partial_Similarities



users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
eps = .2
mode = 5
weights = [.4,  # Depicts
           .15, # Size
           .15, # DominantColor
           .15, # Artist
           .15] # MSE

sim = JaccardUserSimilarity(mode=mode, weights=weights)
def usersDistance(u1, u2):
    return 1 - sim.getSimilarity(u1[0], u2[0])

labels = dbscan(X=users, eps=eps, metric=usersDistance, n_jobs=-1)[1]

print(labels)
