import requests
import json
import os 
from json.decoder import JSONDecodeError
from time import sleep
import socket

hostname= socket.gethostname()
ip = socket.gethostbyname(hostname)

url = 'http://192.168.50.33/api/Pollution/getCuentaPollution'
urlOrden = 'http://192.168.50.33/api/Pollution/updateCuentaPollution'


def get_orden_servicio():
    try:
        response = requests.get(url) 
        if response.status_code == 200:
            reseponseApi = json.loads(response.text)
            print('API correcta')
            return reseponseApi

        elif response.status_code == 401:
            print("Unauthorized")
            return 400

        elif response.status_code == 404:
            print("Not Found")
            return 400

        elif response.status_code == 500:
            print("Internal Server Error")
            return 400

    except JSONDecodeError:
        return response.body_not_json

def update(datos, parametros):

    try:
        response = requests.post(urlOrden, params=parametros, json=datos, verify=False)
        if response.status_code == 200:
            responseApi = json.loads(response.text)
            print('Actualizado')
            return responseApi

        elif response.status_code == 401:
            print("Unauthorized")
            return 400

        elif response.status_code == 404:
            print("Not Found")
            return 400

        elif response.status_code == 500:
            print("Internal Server Error")
            return 400

    except JSONDecodeError:
            return response.body_not_json

def ajusteCerrado(id, casoNegocioGenerado, status):
    datos = {
        'id' : id,
        'casoNegocioGenerado' : casoNegocioGenerado,
        'status' : status
        }

    parametros = { 'id' : id }
    return update(datos, parametros)


# prueba = get_orden_servicio()
# print(prueba['cuenta']['id'])

# p = ajusteCerrado('70', '-', 'Generado')
# print(p)
