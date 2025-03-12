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

from unidecode import unidecode
from dotenv import dotenv_values

logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = dotenv_values(".env")
api_token = config["CKAN_API_KEY"]
ckan_api_url = config["CKAN_API_URL"]

def upsert_resource(api_token, resource_name, resource_url_name, package_id, filepath, resource_id=''):
    if resource_id != '':
        resource_api = f"{ckan_api_url}/api/action/resource_patch"
        request_data = {
            "id": resource_id
        }
    else:
        resource_api = f"{ckan_api_url}/api/action/resource_create"
        request_data = {
          "package_id": package_id,
          "name": resource_url_name,
          "title": resource_name
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

def convert_shape_to_geojson(shapefile)
    filename = shapefile
    d = geopandas.read_file(filename)
    
    new_projection = d.to_crs("EPSG:4326")
    new_filename = filename.split('/')[-1].replace('shp', 'geojson')
    new_projection.to_file(new_filename, driver="GeoJSON")
    return new_filename

filename = sys.argv[1]

new_file = convert_shape_to_geojson(filename)
# upsert_resource(api_token, resource_name, resource_url_name, package_id, new_file, resource_id='')
