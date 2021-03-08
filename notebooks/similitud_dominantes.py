import cv2 as cv
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import imageio as imio
from collections import Counter
from sklearn.cluster import KMeans
import colorsys
import math

artworksCSV = pd.read_csv('../data/originales/Prado_artworks_wikidata.csv')

def show_img_compar(img_1, img_2 ):
    f, ax = plt.subplots(1, 2, figsize=(10,10))
    ax[0].imshow(img_1)
    ax[1].imshow(img_2)
    ax[0].axis('off') #hide the axis
    ax[1].axis('off')
    f.tight_layout()
    plt.show()


def color_percentage(cluster):
    n_pixels = len(cluster.labels_)
    counter = Counter(cluster.labels_)  # count how many pixels per cluster
    perc = {}
    # Crea el vector de % dividiendo el numero de pixels de un cluster con el total
    for i in counter:
        perc[i] = np.round(counter[i] / n_pixels, 2)
    perc = dict(sorted(perc.items()))
    return perc


def compare_hsv(color):
    with open('/Users/Vadym/Desktop/DatosPrado/Prado_artworks_wikidata.csv') as data:
        reader = csv.DictReader(data, delimiter=',')
        for row in reader:
            img = imio.imread(row['Image URL'])

            # Hace Kmeans
            clt = KMeans(n_clusters=3)
            clt_1 = clt.fit(img.reshape(-1, 3))

            # Crea el array de porcentajes de color
            perc = color_percentage(clt_1)

            max_color_key = max(perc, key=perc.get)
            max_color_rgb = clt_1.cluster_centers_[max_color_key]
            max_color_hsv = colorsys.rgb_to_hsv(max_color_rgb[0], max_color_rgb[1], max_color_rgb[2])

            dh = abs(color[0] - max_color_hsv[0])
            ds = abs(color[1] - max_color_hsv[1])
            dv = abs(color[2] - max_color_hsv[2])
            distance = math.sqrt(dh * dh + ds * ds + dv * dv)
            print('Distancia con ' + row['Title'] + ' es ' + str(distance))
            print('Similitud de la coloración del ' + str(round(100 - (distance*100), 2)) + '%')

def dominantColor(entity):
    # Lee imagen
    url = artworksCSV.loc[artworksCSV['wd:paintingID'] == entity]['Image URL'].to_list()[0]
    img = imio.imread(url)

    # Hace Kmeans
    clt = KMeans(n_clusters=3)
    clt_1 = clt.fit(img.reshape(-1, 3))

    # Crea el array de porcentajes de color
    perc = color_percentage(clt_1)

    # Indice del color dominante
    max_color_key = max(perc, key=perc.get)

    # Valores RGB del color dominante
    max_color_rgb = clt_1.cluster_centers_[max_color_key]

    # RGB to HSV
    return colorsys.rgb_to_hsv(max_color_rgb[0], max_color_rgb[1], max_color_rgb[2])

def hsvSimilarity(entity1, entity2):
    a = dominantColor(entity1)
    b = dominantColor(entity2)
    dh = min(abs(a[0]-b[0]), 360-abs(a[0]-b[0])) / 180.0
    ds = abs(a[1] - b[1])
    dv = abs(a[2] - b[2]) / 255.
    distance = math.sqrt(dh * dh + ds * ds + dv * dv)
    return round(1. - (distance), 2)

""" # Lee imagen
img = imio.imread('https://uploads0.wikiart.org/images/francisco-goya/saturn-devouring-one-of-his-children-1823.jpg!Large.jpg')

# Hace Kmeans
clt = KMeans(n_clusters=3)
clt_1 = clt.fit(img.reshape(-1, 3))

# Crea el array de porcentajes de color
perc = color_percentage(clt_1)

# % de colores y valores RGB
print(perc)
print(clt_1.cluster_centers_)

# Indice del color dominante
max_color_key = max(perc, key=perc.get)

# Valores RGB del color dominante
max_color_rgb = clt_1.cluster_centers_[max_color_key]

# RGB to HSV
max_color_hsv = colorsys.rgb_to_hsv(max_color_rgb[0], max_color_rgb[1], max_color_rgb[2])

# Compare with every other artwork
compare_hsv(max_color_hsv) """