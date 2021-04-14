from sanic import Sanic
from sanic.response import json as sanjson
import json
import csv

app = Sanic(name='api-rest')

@app.get('/home')
async def index(request):
    arts = []
    with open('/Users/Vadym/Desktop/DatosPrado/Prado_artworks_wikidata.csv') as data:
        reader = csv.DictReader(data, delimiter=',')
        for row in reader:
            x = {
                "Title": row['Title'],
                "Artist": row['Artist'],
                "Category": row['Category']
            }
            arts.append(x)
    return sanjson(arts)

app.run(host='0.0.0.0', port=8080, debug=True)

