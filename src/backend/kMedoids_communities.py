import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from setup import PATHS, PARAMS
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score
from cluster_information import clusterInfographic
from users_similarity import JaccardUserSimilarity


users = np.array(pd.read_csv(PATHS['USERS_DATA'])['userId']).reshape(-1,1)
mode = PARAMS['k_MOST_SIMILAR']
weights = [30, # Depicts
           21, # Size
           4, # DominantColor
           24, # Artist
           21] # MSE

sim = JaccardUserSimilarity(mode=mode, weights=weights)
def usersDistance(u1, u2):
    return 1 - ((sim.getSimilarity(u1[0], u2[0], polarity='positive') + sim.getSimilarity(u1[0], u2[0], polarity='negative')) / 2)


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

plt.figure()
plt.plot(k_values, scores)
plt.show()
plt.close()
print(best_labels)

clusterInfographic(users.reshape(-1,), best_labels, ("kmed" + str(k_centers) + "_" + str(weights)), usersDistance)