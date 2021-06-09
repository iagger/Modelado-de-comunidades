import logging
import numpy as np
import pandas as pd
from setup import PATHS, PARAMS
from sklearn.cluster import dbscan
from users_similarity import JaccardUserSimilarity
from cluster_visualization import clusterInfographic
from cluster_caracterization import clustersInformation

users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
params = {'eps' : PARAMS['DBSCAN_EPS'],
          'min_samples' : PARAMS['DBSCAN_SAMPLES'],
          'mode'    :PARAMS['k_MOST_SIMILAR'],
          'weights' : {'Depicts'        :   0, 
                       'Size'           :   0, 
                       'DominantColor'  :   0, 
                       'Artist'         :   0, 
                       'MSE'            :   100}}

sim = JaccardUserSimilarity(mode=params['mode'], weights=[*params['weights'].values()])
def usersDistance(u1, u2):
    return 1 - sim.getSimilarity(u1[0], u2[0], polarity = 'positive')

labels = dbscan(X=users, eps=params['eps'], min_samples=params['min_samples'], metric=usersDistance, n_jobs=-1)[1]

metadata={'Method' : 'DBSCAN',
          'Params' : params}
info = clustersInformation(users.reshape(-1,), labels, metadata, "dbscan_" + str([*params['weights'].values()]))
clusterInfographic(info, "dbscan_" + str([*params['weights'].values()]))