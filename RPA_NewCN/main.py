from ApiCyberHubOrdenes import get_orden_servicio, ajusteCerrado
from os import environ, path, remove, listdir, system
from funcionalidad import generacionCN
from shutil import rmtree
from logueo import login
from time import sleep

import socket
import re

# datos = [
#     {
#     'cuenta':'46985756',
#     'usuario':'mvillalobos',
#     'contraseña':'SMI.89.rc108'
#     },
#     {
#     'cuenta':'46976595',
#     'usuario':'mvillalobos',
#     'contraseña':'SMI.89.rc108'
#     },
#     {
#     'cuenta':'46976404',
#     'usuario':'dmartinezf',
#     'contraseña':'F3t6*!e]2vOBc	'
#     },
#     {
#     'cuenta':'35490965',
#     'usuario':'rpanotdone5.service',
#     'contraseña':'yj08ySVJZf9U0rz/'
#     },
#     {
#     'cuenta':'28071421',
#     'usuario':'rpanotdone4.service',
#     'contraseña':'iNly6oWabKLMKNW/'
#     },
#     {
#     'cuenta':'36992847',
#     'usuario':'rpanotdone5.service',
#     'contraseña':'yj08ySVJZf9U0rz/'
#     },
#     {
#     'cuenta':'24459672',
#     'usuario':'mvillalobos',
#     'contraseña':'SMI.89.rc108'
#     },
# ]

# print(datos[0]['usuario'])

# def loginprueba(usuario, password):
#     print(f'sesion iniciada con usuario: {usuario}')

# ultimo_usuario = None

# def main(datos):

#     global ultimo_usuario

#     while len(datos) > 0:
#         print(f'Usuario actual de la sesion: {ultimo_usuario}')
#         sleep(1)
#         info = datos[0]
#         print(info)
#         del datos[0]

#         cuenta = info['cuenta']
#         usuario = info['usuario']
#         constraseña = info['contraseña']

#         print(f"➡️ Procesando cuenta: {cuenta} con usuario: {usuario}")

#         if usuario != ultimo_usuario:
#             try:
#                 print('Intando hacer close y quit de la sesion anterior')
#             except: pass
#             loginprueba(usuario, constraseña)
#             ultimo_usuario = usuario

#         else: print("🟢 Reutilizando sesión actual de Chrome")
        
#         print('aqui va la funcion de generacion del cn')
# main(datos)


def delTemporales():

    temp_folder = environ['TEMP']

    try:

        temp_files = listdir(temp_folder)

        for temp_file in temp_files:
            temp_file_path = path.join(temp_folder, temp_file)

            try:
                if path.isfile(temp_file_path): remove(temp_file_path)
                elif path.isdir(temp_file_path): rmtree(temp_file_path)

            except: pass

        print('Eliminacion temporales OK!')

    except Exception as e: print('Se produjo un error al eliminar los temporales')

def workflow():
    try:
        # Se instancia el usuario global sobre el que se estara validando la sesion anterior
        global ultimo_usuario

        while True:
            # Eliminacion de Temporales
            delTemporales()

            ## Llamada al servicio para validar si existen cuentas
            apiResponse = get_orden_servicio()

            host = socket.gethostname()
            ip = socket.gethostbyname(host)

            

            

            ### Si existen cuentas empieza proceso de validacion de sesion anterior 
            if info != 'SIN INFO':

                print(f'🔴 Usuario de la sesion actual: {ultimo_usuario}')
                print(info)

                #### Se instancian los valores
                datosProceso = apiResponse['cuenta']
                usuario      = datosProceso['usuario']
                password     = datosProceso['pass']
                cuenta       = datosProceso['cuenta']
                id           = datosProceso['id']
                plantillaCN  = datosProceso['casoNegocio']

                print(f"➡️ Procesando cuenta: {cuenta} con usuario: {usuario}")

                #### Validacion de la sesion anterior
                if usuario != ultimo_usuario:
                    try:
                        ###### Se intenta cerrar chrome por medio del driver
                        driver.close()
                        driver.quit()
                    except: 
                        ###### Se cierra chrome en caso de que no se pueda por driver
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")
                        system("taskkill /f /im chrome.exe")

                    ##### Se Inicia la sesion para cuando resulto un usuario distinto
                    driver, status_logue = login(usuario, password)
                    if status_logue == False:
                        response = ajusteCerrado(id, '-', 'Pendiente')
                        print(response)
                        ultimo_usuario = None
                        return False

                    ##### Se actualiza el usuario en la sesion anterior
                    ultimo_usuario = usuario
                    print(f"🟢 Sesion iniciada con el usuario: {usuario}")

                #### En caso de que sea el mismo usuario anterior
                else: print("🟢 Reutilizando sesión actual de Chrome")

                #### Con la sesion iniciada se pasa a generar el CN
                campos = ['CATEGORIA', 'MOTIVO', 'SUBMOTIVO', 'SOLUCION','COMENTARIO']
                resultados = {}

                # Extraer cada campo con regex
                for campo in campos:
                    match = re.search(rf'{campo}:\s*(.+)', plantillaCN)
                    resultados[campo] = match.group(1).strip() if match else ''

                # Mostrar resultados
                for k, v in resultados.items():
                    print(f'{k}: {v}')


                resultado, cnGenerado = generacionCN(driver, cuenta, resultados['CATEGORIA'], resultados['MOTIVO'], resultados['SUBMOTIVO'], resultados['SOLUCION'], resultados['COMENTARIO'])
                if resultado == False:
                    response = ajusteCerrado(id, '-', cnGenerado)
                    print(response)
                    driver.close()
                    driver.quit()
                    ultimo_usuario = None
                    return False
                else: 
                    response = ajusteCerrado(id, cnGenerado, 'Completado')
                    print(response)
            else:
                ultimo_usuario = None
                sleep(15)
    
    except: return False

while True == True:

    apiResponse = get_orden_servicio()
    info = apiResponse[0]
    
    if info != 'SIN INFO':
        print('Agregar aqui el servicio de reprocesamiento')

        resultado = workflow()
        if resultado == False:
            system("taskkill /f /im chrome.exe")
            system("taskkill /f /im chrome.exe")
            system("taskkill /f /im chrome.exe")
    else: 
        print('Esperando Cuentas ')
        sleep(10)
