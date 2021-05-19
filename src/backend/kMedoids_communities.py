import logging
import numpy as np
import pandas as pd
from setup import PATHS, PARAMS
from sklearn_extra.cluster import KMedoids
from cluster_information import clusterInfographic
from users_similarity import JaccardUserSimilarity


##logging.basicConfig(filename="data/log/KMedoidsResults.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s -> %(message)s')

users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
k_centers = PARAMS['KMEDOIDS_CENTERS']
mode = PARAMS['k_MOST_SIMILAR']
weights = [20, # Depicts
           20, # Size
           20, # DominantColor
           20, # Artist
           20] # MSE

sim = JaccardUserSimilarity(mode=mode, weights=weights)
def usersDistance(u1, u2):
    return 1 - sim.getSimilarity(u1[0], u2[0])

##logging.info("Run DBSCAN with PARAMS [mode = " + str(mode) + ", weights = " + str(weights) + "]")

km = KMedoids(n_clusters=k_centers, metric=usersDistance, random_state=PARAMS['RANDOM_STATE']).fit(users)

labels = km.labels_

##logging.debug("Labels [" + str(labels) + "]")

clusterInfographic(users.reshape(-1,), labels, ("kmed" + str(k_centers) + "_" + str(weights)), usersDistance)