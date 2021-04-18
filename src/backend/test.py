from artwork_similarity import *
import pandas as pd
import json

PATHS = json.load(open("configuration.cfg"))["PATHS"]

sim = DepictsSimilarity(depth=4)  # depth=3|2|1
#sim = SizeSimilarity()
#sim = DominantColorSimilarity()
#sim = ArtistSimilarity()
#sim = ImageMSESimilarity()


# Cargamos los wd_paintingIDS de los cuadros
paintingIDS = pd.read_csv(PATHS['ARTWORKS_DATA'])['wd:paintingID'].unique()

# Recuperamos las similitudes parciales con los wd como argumento
print(sim.getSimilarity(paintingIDS[1], paintingIDS[3]))
