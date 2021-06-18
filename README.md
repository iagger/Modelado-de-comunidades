# Modelado de Comunidades

## Requirements 

`pip install -r requirements.txt`

## Tutorial inicio API
###### Para arrancar y probar la ApiRest con todo nivel de detalle:

    - Arrancar servidor con: python src/backend/api_main.py
    
    - Abrir un terminal desde la carpeta contenedora del fichero "index.html" e introducir: python -m http.server 8000  
    
    - En el navegador, ir al enlace: http://localhost:8000/index.html


###### Para arrancar y probar la ApiRest a nivel de visualización básica de los resultados:

    - Arrancar servidor con: src/backend/api_main.py

    - Para visualizar y lanzar las APIs se puede utilizar swagger o postman, por facilidad de uso e integración se recomienda postman.
    - Ruta local para acceder al servidor:

        Tipo GET  ->  http://localhost:8080/(nombre de la api)
    
    - En headers/params/body añadir los parámetros necesarios para hacer la consulta.
    

## Formación de comunidades

    Ejecutar src/backend/communities_detection.py
    Opcion --help para ver parámetros
