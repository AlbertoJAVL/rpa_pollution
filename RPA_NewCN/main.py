from ApiCyberHubOrdenes import get_orden_servicio, ajusteCerrado
from os import environ, path, remove, listdir, system
from funcionalidad import generacionCN
from tele import send_msg
from shutil import rmtree
from logueo import login
from time import sleep

import socket
import re
import os



ultimo_usuario = None
driver = None




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
        global ultimo_usuario, driver

        while True:
            # Eliminacion de Temporales
            delTemporales()

            ## Llamada al servicio para validar si existen cuentas
            apiResponse2 = get_orden_servicio()

            host = socket.gethostname()
            ip = socket.gethostbyname(host)

            
            print(apiResponse2)
            

            ### Si existen cuentas empieza proceso de validacion de sesion anterior 
            try:

                print(f'🔴 Usuario de la sesion actual: {ultimo_usuario}')
                print(apiResponse2)

                #### Se instancian los valores
                datosProceso = apiResponse2['cuenta']
                usuario      = datosProceso['usuario']
                password     = datosProceso['pass']
                cuenta       = datosProceso['cuenta']
                id           = datosProceso['id']
                plantillaCN  = datosProceso['casoNegocio']
                print('################################################################')
                plantillaCN  = plantillaCN.replace('MOTIVO CLIENTE:', 'MOTIVOCLIENTE:')
                plantillaCN  = plantillaCN.replace('Motivo Cliente:', 'MOTIVOCLIENTE:')
                print(repr(plantillaCN))
                sleep(10)


                print(f"➡️ Procesando cuenta: {cuenta} con usuario: {usuario}")

                try:
                    ###### Se intenta cerrar chrome por medio del driver
                    driver.quit()
                except: pass

                ##### Se Inicia la sesion para cuando resulto un usuario distinto
                driver, status_logue, status_actualizacion = login(usuario, password)
                if status_logue == False:
                    if 'Claves Invalidas' in status_actualizacion: 
                        response = ajusteCerrado(id, '-', f'Error: {status_actualizacion}')
                        send_msg(f'ERROR Claves Invalidad Cuenta: {cuenta} Usuario: {usuario} Password: {password}')
                    else: response = ajusteCerrado(id, '-', 'Generado')
                    print(response)
                    try: driver.quit()
                    except: pass
                    ultimo_usuario = None
                    driver = None
                    return False

                ##### Se actualiza el usuario en la sesion anterior
                ultimo_usuario = usuario
                print(f"🟢 Sesion iniciada con el usuario: {usuario}")
                
                #### Con la sesion iniciada se pasa a generar el CN
                texto = plantillaCN.replace('\r', '\n')
                
                # print(texto)

                # 2) Campos a extraer
                campos = ['CATEGORIA', 'MOTIVO', 'SUBMOTIVO', 'SOLUCION', 'MOTIVOCLIENTE', 'COMENTARIO']

                # Patrón corregido sin \b problemático y con nombres de campo exactos
                patron_todos = r'''(?m)(CATEGORIA|MOTIVO|SUBMOTIVO|SOLUCION|MOTIVOCLIENTE|COMENTARIO)\s*:\s*
                                (?:
                                    "([^"]*)"           # grupo 2: entre comillas
                                    | \(([^)]*)\)       # grupo 3: entre paréntesis
                                    | \*?([^\n]+?)      # grupo 4: suelto
                                )
                                \s*(?=\n|$)'''

                matches = re.findall(patron_todos, texto, flags=re.IGNORECASE | re.VERBOSE)

                resultados = {c: '' for c in campos}
                for nombre, g1, g2, g3 in matches:
                    valor = (g1 or g2 or g3 or '').strip()
                    resultados[nombre.upper()] = valor

                for k in campos:
                    print(f'{k}: {resultados[k]}')

                resultados['CATEGORIA'] = resultados['CATEGORIA'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()
                resultados['MOTIVO'] = resultados['MOTIVO'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()
                resultados['SUBMOTIVO'] = resultados['SUBMOTIVO'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()
                resultados['SOLUCION'] = resultados['SOLUCION'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()
                resultados['COMENTARIO'] = resultados['COMENTARIO'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()
                resultados['MOTIVOCLIENTE'] = resultados['MOTIVOCLIENTE'].replace('_', '').replace('-', '').replace(';', '').replace('"', '').strip()

                contadorIntentosGeneracionCN = 0
                contadorIntentosCuenta = 0
                fGeneracionCN = True
                while fGeneracionCN:

                    contadorIntentosGeneracionCN += 1
                    print(f'###################### INTENTO FUNCION GENERACION CN: {contadorIntentosGeneracionCN} ######################')

                    resultado, cnGenerado, statusFinal = generacionCN(driver, cuenta, resultados['CATEGORIA'], resultados['MOTIVO'], resultados['SUBMOTIVO'], resultados['SOLUCION'], resultados['COMENTARIO'], resultados['MOTIVOCLIENTE'])
                    if resultado == False and cnGenerado == 'Generado':
                        driver.save_screenshot(f'error_{cuenta}.png')
                        driver.quit()
                        if contadorIntentosGeneracionCN == 3:
                        
                            response = ajusteCerrado(id, '-', statusFinal)
                            print(response)
                            send_msg(f'ERROR: {statusFinal}\nCuenta: {cuenta}')
                            ultimo_usuario = None
                            driver = None
                            return False

                        else:

                            driver, status_logue, status_actualizacion = login(usuario, password)
                            if status_logue == False:

                                if 'Claves Invalidas' in status_actualizacion: 
                                    response = ajusteCerrado(id, '-', f'Error: {status_actualizacion}')
                                    send_msg(f'ERROR Claves Invalidad Cuenta: {cuenta} Usuario: {usuario} Password: {password}')
                                else: response = ajusteCerrado(id, '-', 'Generado')

                                print(response)
                                ultimo_usuario = None
                                driver = None
                                return False

                        print(ultimo_usuario)
                        sleep(10)
                        # return False
                    elif resultado == False and ('Error' in cnGenerado or 'Inconsistencia' in cnGenerado):
                        driver.quit()
                        response = ajusteCerrado(id, '-', cnGenerado)
                        print(response)
                        send_msg(f'ERROR: {cnGenerado}\nCuenta: {cuenta}')
                        ultimo_usuario = None
                        driver = None
                        return False
                    else: 
                        response = ajusteCerrado(id, cnGenerado, 'Completado')
                        print(response)
                        fGeneracionCN = False
                        print('#########################################')
                        print('#########################################')
                        print('#########################################')
                        print('#########################################')
                        print('#########################################')
                        driver.quit()

            except Exception as e: 
                ultimo_usuario = None
                driver = None
                print(e)
                return False
    
    except Exception as e: 
        ultimo_usuario = None
        driver = None
        print(e)
        return False

while True == True:

    print('#############################')
    print('#############################')
    print('#############################')

    # os.system(f"taskkill /f /im chrome.exe")
    # os.system(f"taskkill /f /im chrome.exe")
    # os.system(f"taskkill /f /im chrome.exe")

    apiResponse = get_orden_servicio()
    
    
    if apiResponse != 400:
        id = apiResponse['cuenta']['id']
        response = ajusteCerrado(id, '-', 'Generado')

        resultado = workflow()
        if resultado == False: pass
            # system("taskkill /f /im chrome.exe")
            # system("taskkill /f /im chrome.exe")
            # system("taskkill /f /im chrome.exe")
    else: 
        print('Esperando Cuentas ')
        sleep(10)
        os.system('cls')
