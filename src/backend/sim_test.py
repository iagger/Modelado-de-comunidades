from artwork_similarity import *
from users_similarity import *
import pandas as pd
import json

PATHS = json.load(open("configuration.cfg"))["PATHS"]

sim = DepictsSimilarity(depth=3)  # depth=3|2|1
#sim = SizeSimilarity()
#sim = DominantColorSimilarity()
#sim = ArtistSimilarity()
#sim = ImageMSESimilarity()


# Cargamos los wd_paintingIDS de los cuadros
paintingIDS = pd.read_csv(PATHS['ARTWORKS_DATA'])['wd:paintingID'].unique()

# Recuperamos las similitudes parciales con los wd como argumento
print(sim.getSimilarity(paintingIDS[3], paintingIDS[1])) # recompute=True para recalcular la similitud obviando el contenido de la cache

checkSimetry(sim, paintingIDS)

sim.close()