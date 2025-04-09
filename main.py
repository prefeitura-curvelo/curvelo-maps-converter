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
maps_folder_path = config["MAPS_FOLDER_PATH"]

LAYERS = {
    "Educacao.shp": "f8222461-79a5-436d-8b56-62f3751e10c7",
    "Escolas.shp": "0345399c-8b61-4753-9973-84ac1079f94c",
    "Area_Institucional_Loteamentos.shp": "8ce2a816-b319-4301-b114-9f51277188b8",
    "Macrozoneamento.shp": "fe906a2a-a40f-4992-bcf3-bfb10935ecc6",
    "Alvaras_Urbanisticos.shp": "41974147-e4e4-44f7-9ad9-e95ce6b75403",
    "LC_176_2022.shp": "ec73a44b-a1ef-4d09-9eca-b04c272b033b",
    "Assistencia_Social_Administracao.shp": "d0b6741e-a6ae-425b-801c-b6361997c642",
    "Zonas_Fiscais.shp": "742ca91e-b959-46d8-aa47-449814875dfd",
    "APP.shp": "266fa1e1-fb06-4c3a-b25b-1b269551dabb",
    "Lotes.shp": "5fcfbc2d-27c8-4099-a83b-81bcfd457018",
    "Passeios.shp": "8f11730b-acca-4726-83a4-c0288ceb008f",
    "Quadras.shp": "76acb62d-f1d4-4efa-92a0-c171e56b0e19",
    "Trecho_Logradouro.shp": "65d8f7ac-cf7a-4e17-b490-b3d9e0b740dc",
    "Bairros.shp": "29a01453-46f7-40b6-b67a-ebb2b4b4d249",
    "Conjuntos_Habitacionais.shp": "cacfc1a8-6b2a-4887-ab5d-226c0e8c5b0c",
    "REURB.shp": "09bd2f53-35d2-4a1f-a0c8-b15a7f60cd15",
    "Area_Verde_Loteamentos.shp": "4be28723-e4be-4e23-90e5-2ce155104f9a",
    "Edificacao.shp": "d65f3c99-9850-4083-837a-0bd39eeb10c4",
    "Alvaras.shp": "96ac5838-ff63-4375-8b21-dbf752903649",
    "Limite_Municipio.shp": "30b43ca9-8353-439a-b88c-2f56c7784396",
    "Limite_PerUrbano.shp": "f015aaf9-d26b-491c-878a-14fdf8522074",
    "Limite_PerRural.shp": "8132bb0a-fcd4-4fdf-9d68-1d276eaafd62",
    "Hierarquia_Viaria.shp": "9557013e-5739-4758-bc01-d1c332cb86c8",
    "Inscricao_Cadastral.shp": "c20eca97-3287-4f62-a701-a81737b03a68",
    "Zoneamento.shp": "6fd54b96-71c0-4cdf-9db3-6f49c549a793",
    "Loteamento.shp": "dd1eb84e-dbec-4995-8504-d6e344dc656c",
    "Pontos_Saude.shp": "85acb4b0-9deb-4190-9afb-6b03d8aa967f",
    "Imoveis_Municipio.shp": "2a22b47f-0a83-42f1-9a62-7f687e87f8ac",
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


def convert_shape(shapefile, driver="GeoJSON"):
    drivers_extension = {
        "GeoJSON": "geojson",
        "CSV": "csv"
    }

    d = geopandas.read_file(shapefile)
    d = d.set_crs("EPSG:31983") 
    new_projection = d.to_crs("EPSG:4326")
    new_filename = shapefile.split('/')[-1].replace('shp', drivers_extension[driver])
    new_filepath = os.path.join("/tmp", new_filename)
    new_projection.to_file(new_filepath, driver=driver)
    return new_filepath

formats = {
        "geojson": lambda x: convert_shape(x, driver="GeoJSON"),
        "shp": lambda x: x,
        "csv": lambda x: convert_shape(x, driver="CSV")
}

for filename, resource_id in LAYERS.items():
    filepath = os.path.join(maps_folder_path, filename)
    for f in formats.keys():
        new_file = formats[f](filepath)
        upsert_resource(api_token, new_file, resource_id=resource_id)
