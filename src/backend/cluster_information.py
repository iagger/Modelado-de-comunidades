import matplotlib.pyplot as plt
import numpy as np
import imageio as imio
from users_similarity import myFavouriteArtworks
from collections import Counter
from math import ceil
import pandas as pd
from setup import PATHS
from matplotlib.backends.backend_pdf import PdfPages

users = pd.read_csv(PATHS['USERS_DATA'])
artworks = pd.read_csv(PATHS['ARTWORKS_DATA'])

users.replace('<12', '0-12', inplace=True)
users.replace('>70', '70+', inplace=True)

someColors = ['r', 'g', 'b', 'y', 'k', 'orange', 'c']

def showImagesHorizontally(image_url, image_labels, fig_title="", rows=2):
    rowSize = ceil(len(image_url)/rows)
    fig, ax = plt.subplots(rows, rowSize)
    fig.suptitle(fig_title, fontsize=20)
    for i in range(len(image_url)):
        image = imio.imread(image_url[i])
        ax[i//rowSize][i%rowSize].imshow(image)
        ax[i//rowSize][i%rowSize].set_title(image_labels[i], fontsize=8)
        ax[i//rowSize][i%rowSize].axis('off')
    return fig

def separateClusters(objects, labels):
    clusters = dict()
    for c in np.unique(labels):
        pos = np.where(labels == c)
        if len(pos):
            clusters[c] = objects[pos]
    return clusters

def buildDistanceMatrix(distFun, userList):
    N = len(userList)
    distMatrix = np.zeros((N,N))
    for i in range(N):
        for j in range(i,N):
            dist = distFun(userList[i], userList[j])
            distMatrix[i][j] = dist
            distMatrix[j][i] = dist
    return distMatrix

def relabelClusters(labels):
    uniques = np.unique(labels)
    labelMap = dict(zip(uniques, np.arange(len(uniques))))
    mapper = np.vectorize(lambda l : labelMap[l])
    return mapper(labels.copy())

def clusterInfographic(objects, labels, title, distanceFun):

    pp = PdfPages('data/clustering/' + title.replace(' ','') + '.pdf')

    labels = relabelClusters(labels)

    for cluster, clusterUsers in separateClusters(objects, labels).items():

        
        # Prepare cluster information
        clusterIndices = []
        for i, row in users.iterrows():
            if row['userId'] in clusterUsers:
                clusterIndices.append(i)
        clusterDemoData = users.iloc[clusterIndices]

        positiveArtworks = []
        negativeArtworks = []
        for u in clusterUsers:
            positiveArtworks += list(myFavouriteArtworks(userId=u, polarity='positive'))
            negativeArtworks += list(myFavouriteArtworks(userId=u, polarity='negative'))

        topArtworksID = [i[0] for i in Counter(positiveArtworks).most_common(6)]
        bottomArtworksID = [i[0] for i in Counter(negativeArtworks).most_common(6)]
        topArtworksImage, topArtworksTitle = [], []
        bottomArtworksImage, bottomArtworksTitle = [], []
        for i, row in artworks.iterrows():
            if row['ID'] in topArtworksID:
                topArtworksImage.append(row['Image URL'])
                topArtworksTitle.append(row['Title'])
            if row['ID'] in bottomArtworksID:
                bottomArtworksImage.append(row['Image URL'])
                bottomArtworksTitle.append(row['Title'])

        distMatrix = buildDistanceMatrix(distanceFun, clusterUsers.reshape(-1,1))

        # Demographic information
        demoColumns = ["country", "age", "gender"]
        demoFig, demoAx = plt.subplots(1, len(demoColumns))
        demoFig.suptitle('Cluster ' + str(cluster) + ' demographic information (Size = ' + str(clusterDemoData.shape[0]) + ')', fontsize=16)
        for i, column in enumerate(clusterDemoData[demoColumns]):
            clusterDemoData[column].value_counts().plot(kind="bar", ax=demoAx[i], figsize=(10,6), color=someColors[i]).set_title(column.upper())
        demoFig.savefig(pp, format='pdf')

        try:
            # TOP ARTWORKS
            topFig = showImagesHorizontally(topArtworksImage, topArtworksTitle, "TOP artworks in cluster " + str(cluster))
            topFig.savefig(pp, format='pdf')

            # BOTTOM ARTWORKS
            bottomFig = showImagesHorizontally(bottomArtworksImage, bottomArtworksTitle, "BOTTOM artworks in cluster " + str(cluster))
            bottomFig.savefig(pp, format='pdf')

            # Heatmap
            heatmapFig = plt.figure("Cluster " + str(cluster) + " heat map")
            plt.imshow(distMatrix, cmap='hot', interpolation='nearest')
            heatmapFig.savefig(pp, format='pdf')

            plt.close('all')
        except:
            print("ERROR: Couldnt draw cluster " + str(i))
            print(' TOP ' + str(len(topArtworksTitle)))
            print(' BOTTOM ' + str(len(bottomArtworksImage)))
            plt.close('all')
    
    pp.close()
    