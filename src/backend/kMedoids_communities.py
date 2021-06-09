import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from setup import PATHS, PARAMS
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score
from users_similarity import JaccardUserSimilarity
from cluster_visualization import clusterInfographic
from cluster_caracterization import clustersInformation


users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
params = {'mode'    :PARAMS['k_MOST_SIMILAR'],
          'weights' : {'Depicts'        :   21, 
                       'Size'           :   5, 
                       'DominantColor'  :   7, 
                       'Artist'         :   17, 
                       'MSE'            :   50}}

sim = JaccardUserSimilarity(mode=params['mode'], weights=[*params['weights'].values()])
def usersDistance(u1, u2):
    return 1 - sim.getSimilarity(u1[0], u2[0], polarity='positive')


scores = []
min_k = 6
max_k = 15
k_values = np.arange(max_k - min_k + 1) + min_k
for k_centers in k_values:
    km = KMedoids(n_clusters=k_centers, metric=usersDistance, random_state=PARAMS['RANDOM_STATE']).fit(users)
    score = silhouette_score(X=users, labels=km.labels_, metric=usersDistance)
    if score > max(scores, default = -1):
        best_labels = km.labels_
    scores.append(score)


metadata={'Method' : 'k-medoids',
          'Params' : params}
info = clustersInformation(users.reshape(-1,), best_labels, metadata, "dbscan_" + str([*params['weights'].values()]))
clusterInfographic(info, "kmed_" + str([*params['weights'].values()]))