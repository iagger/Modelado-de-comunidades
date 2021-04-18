from sanic import Sanic
from sanic.response import json as sanjson
import csv
from artwork_similarity import *

# Se instancia la aplicación Sanic
app = Sanic(name='api-rest')

# Restful API para listar todos los cuadros
@app.get('/listArtworks')
async def index(request):
    try:
        arts = []
        data = open('../data/originales/Prado_artworks_wikidata.csv')
        reader = csv.DictReader(data, delimiter=',')
        for row in reader:
            x = {
                "Title": row['Title'],
                "Artist": row['Artist'],
                "Category": row['Category'],
                "Image": row['Image URL']
            }
            arts.append(x)
        return sanjson(arts)
    except:
        return sanjson({"Message": "Artworks not found"}, status=400)

# Restful API para listar los 5 cuadros más similares al que recibe
@app.get('/similarArtworks')
async def index(request):
    try:
        id = request.headers["id"]
        artworks = MostSimilarArtworks(id, k=5, weights=[])
        sims = []
        data = open('../data/originales/Prado_artworks_wikidata.csv')
        reader = csv.DictReader(data, delimiter=',')
        for i in artworks:
            for row in reader:
                if row['wd:paintingID'] == i[1]:
                    x = {
                        "Title": row['Title'],
                        "Similarity": i[0],
                        "Category": row['Category'],
                        "Artist": row['Artist'],
                        "Image": row['Image URL']
                    }
                    sims.append(x)
                    data.seek(0)
                    break
        for row in reader:
            if row['wd:paintingID'] == id:
                art = {
                    "Selected artwork": id,
                    "Title": row['Title'],
                    "Category": row['Category'],
                    "Artist": row['Artist'],
                    "Image": row['Image URL'],
                    "Similar artworks":
                        sims
                }
        return sanjson(art)
    except:
        return sanjson({"Message": "Artwork ID not found"}, status=400)


