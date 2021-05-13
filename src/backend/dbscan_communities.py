import logging
import numpy as np
import pandas as pd
from setup import PATHS, PARAMS
from sklearn.cluster import dbscan
from users_similarity import JaccardUserSimilarity

logging.basicConfig(filename="data/log/dbscanResults.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s -> %(message)s')

users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
eps = PARAMS['DBSCAN_EPS']
minClusterSize = PARAMS['DBSCAN_SAMPLES']
mode = PARAMS['k_MOST_SIMILAR']
weights = [60, # Depicts
           10, # Size
           10, # DominantColor
           10, # Artist
           10] # MSE

sim = JaccardUserSimilarity(mode=mode, weights=weights)
def usersDistance(u1, u2):
    return 1 - sim.getSimilarity(u1[0], u2[0]) # polarity = 'positive' & 'negative'

logging.info("Run DBSCAN with PARAMS [eps = " + str(eps) + ", minClusterSize = " + str(minClusterSize) + ", mode = " + str(mode) + ", weights = " + str(weights) + "]")

labels = dbscan(X=users, eps=eps, min_samples=minClusterSize, metric=usersDistance, n_jobs=-1)[1]

logging.debug("Labels [" + str(labels) + "]")