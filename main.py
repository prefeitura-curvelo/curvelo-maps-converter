#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import base64
import pandas as pd
import logging
import hashlib
import geopandas
import sys
import os
from unidecode import unidecode
from dotenv import dotenv_values

logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = dotenv_values(".env")
api_token = config["CKAN_API_KEY"]
ckan_api_url = config["CKAN_API_URL"]

LAYERS = {
    "Macrozoneamento.shp": "fe906a2a-a40f-4992-bcf3-bfb10935ecc6", 
    "Perimetro_Rural.shp": "f6c22bde-d66c-4580-aa58-f120246299a1",
    "Limite_PerUrbano.shp": "f015aaf9-d26b-491c-878a-14fdf8522074",
    "Lote_08_2024.shp": "d20b34a8-c322-409d-b2f9-a7715438af01",
    "Hidro_Curvelo_IDE_SISEMA.shp": "02620151-92f5-42cd-b115-3c44bbcab20e",
    "Pontos_Iluminacao.shp": "0f6c5345-5954-4136-8a4d-e4eca3f6325d",
    "ImoveisMunicipio_08_2024.shp": "f6a9270f-607e-4ed1-bd3e-82260f33ccd4",
    "Logradouros_08_2024.shp": "fd1a784d-7ad4-4fee-b414-18a6c2bd0eb1",
    "Hierarquia_Viaria_PD.shp": "d151752f-5e03-4c46-bfbe-2a04ccade2fa",
    "Edificacoes_08_2024.shp": "f3d859f3-2661-4e5a-9e4b-23c0f253a8ae",
    "Inscricoes_cadastrais_08_20224.shp": "371e00e2-a7d6-4b98-aacc-846c9e57faef"
}

def upsert_resource(api_token, filepath, resource_id=''):
    if resource_id != '':
        resource_api = f"{ckan_api_url}/api/action/resource_patch"
        request_data = {
            "id": resource_id
        }
    
    headers = {
      "Authorization": api_token
    }
    
    resultado = requests.post(resource_api,
                              headers = headers,
                              data = request_data,
                              files = [('upload', open(filepath, 'rb'))]
                             )
    resposta_dict = json.loads(resultado.content)
    return resposta_dict

def convert_shape_to_geojson(shapefile):
    d = geopandas.read_file(shapefile)
    
    new_projection = d.to_crs("EPSG:4326")
    new_filename = shapefile.split('/')[-1].replace('shp', 'geojson')
    new_projection.to_file(new_filename, driver="GeoJSON")
    return new_filename


# O diretório onde os arquivos .shp estão localizados
dirpath = sys.argv[1]

for filename, resource_id in layers.items():
    filepath = os.path.join(dirpath, filename)
    new_file = convert_shape_to_geojson(filepath)
    upsert_resource(api_token, new_file, resource_id=resource_id)
