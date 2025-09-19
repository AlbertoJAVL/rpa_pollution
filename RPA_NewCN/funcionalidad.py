from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, date, timedelta
from time import sleep


import  pyautogui  as pg
import re

def cargandoElemento(driver, elemento, atributo, valorAtributo, path = False, valContador = 60):

    cargando = True
    contador = 0

    while cargando:

        sleep(1)
        try: 

            html = driver.execute_script("return document.documentElement.outerHTML;")
            if 'The server you are trying to access is either busy or experiencing difficulties. ' in html: return False, 'Error Servidor Ocupado'

            contador += 1
            if contador in [10,20,30,40,50,60]: print('Validando posible warning')
            alert = Alert(driver)
            alert_txt = alert.text
            print(f'♦ {alert_txt} ♦')
            if ('FTTH' in alert_txt.upper() 
                or 'El caso de negocio tiene los siguientes campos requeridos sin completar:' in alert_txt
                or 'Es necesario actualizar' in alert_txt
                or 'campo Referido no esta permitido' in alert_txt
                or 'No se ha recibido el certificado' in alert_txt
                or 'FALLA GENERAL' in alert_txt.upper()): 
                alert.accept()
                print('Alert Cerrado')

                if 'No se ha recibido el certificado' in alert_txt: return False, 'Error Certificado Wifi'
            elif 'Esta tipificación requiere un Motivo de Cliente válido' in alert_txt: 
                alert.accept()
                print('Alert Cerrado')
                return False, 'Error Agregar motivo cliente'
            else: return False, f'Inconsistencia Siebel: {alert_txt}'
        
        except:
            try:
                if contador in [10,20,30,40,50,60]: print('Esperando a que el elemento cargue')
                if path == False: 
                    driver.find_element(By.XPATH, f"//{elemento}[@{atributo}='{valorAtributo}']").click()
                    return True, ''
                else: 
                    driver.find_element(By.XPATH, path).click()
                    return True, ''
                
            except:
                if contador in [10,20,30,40,50,60]: print('Pantalla Cargando')
                if contador == valContador: return False, 'Error Pantalla NO Carga'

def obtencionColumna(driver, nombreColumna, path):

    buscandoColumna = True
    contador = 1

    while buscandoColumna:

        try:
            pathF = path.replace('{contador}', str(contador))
            nameColumna = driver.find_element(By.XPATH, pathF)
            nameColumna = driver.execute_script("return arguments[0].textContent;", nameColumna)

            if nombreColumna in nameColumna: return str(contador)
            else:
                contador += 1
                if contador == 100: return False

        except: 
            contador += 1
            if contador == 100: return False

def home(driver): driver.find_element(By.XPATH, "//a[@title='Pantalla Única de Consulta']").click()
def home2(driver): driver.find_element(By.XPATH, "//a[@title='Página inicial']").click()

# Función de apertura para generar validaciones


def validacionSubEstado(driver, os, respuestaEncuesta):

    try:

        columna = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[{contador}]/div'
        columna2 = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[{contador}]/input[2]'

        print('→ Validacion Sub Estado/Tipo')

        # Pantalla Consulta (Click)
        lupa_busqueda_os, _ = cargandoElemento(driver, 'a', 'title', 'Ordenes de Servicio')
        if lupa_busqueda_os == False: return 'Error Pantalla NO Carga'
        
        # Buscando Elemento
        print('→ Cargando Pantalla busqueda OS')
        lupa_busqueda_os = cargandoElemento(driver, 'button', 'title', 'Ordenes de servicio Applet de lista:Consulta')
        if lupa_busqueda_os == False: return 'Error Pantalla NO Carga'
        sleep(5)

        # Ingreso OS
        print('→ Obteniendo posicion columna busqueda No Orden')
        posicion = obtencionColumna(driver, 'Nº de orden', columna)
        if posicion == False: return 'Error Pantalla NO Carga'
        sleep(3)

        # driver.find_element(By.XPATH, columna.replace('{contador}', posicion)).click()
        try: input_busqueda_os = driver.find_element(By.XPATH, columna2.replace('{contador}', posicion))
        except:
            try: input_busqueda_os = driver.find_element(By.XPATH, columna2.replace('/input[2]', '/input').replace('{contador}', posicion))
            except: return 'Error Estructura Elementos'
        input_busqueda_os.send_keys(os)
        input_busqueda_os.send_keys(Keys.RETURN)
        print('→ OS Ingresada OK!')

        print('→ Cargando OS ←')
        sleep(15)

        if 'NO CONTESTA' in respuestaEncuesta.upper() or 'SI' in respuestaEncuesta.upper(): posicion = obtencionColumna(driver, 'Sub-Estado', columna)
        else: posicion = obtencionColumna(driver, 'Tipo', columna)

        if posicion == False: return 'Error Pantalla NO Carga'
        sleep(3)

        input_Validado = driver.find_element(By.XPATH, columna2.replace('{contador}', posicion).replace('/input[2]', ''))
        input_Validado = driver.execute_script("return arguments[0].textContent;", input_Validado)
        print(f'Validador: {input_Validado}')

        if 'NO CONTESTA' in respuestaEncuesta.upper():
            if 'OK Automatico' in input_Validado: return True
            else: return False
        
        elif 'SI' in respuestaEncuesta.upper():
            if 'ok cliente' in input_Validado: return True
            else: return False
        
        else: return input_Validado
    except Exception as e: 
        print(f'ERROR EN FUNCION INICIO. ERROR: {e}')
        return 'FCierreOS'

def generacionOS(driver, cuenta, tipoOSOrginal, comentario):

    try: 
                        
        pathOpcMenuOS = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/form/span/div/div[1]/div[2]/span[1]/span/ul/li[{contador}]/a'
        pathColumnasBOS = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[{contador}]/div'
        pathInputBOS = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[{contador}]'
        pathOpcFechaAgendar = '/html/body/div[33]/div[2]/div/div/div/form/div/div[1]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[{contador}]/td[2]'
        pathOpcFechaAgendar2 = '/html/body/div[33]/div[2]/div/div/div/form/div/div[1]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[{contador}]/td[3]'
                              #/html/body/div[33]/div[2]/div/div/div/form/div/div[1]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[2]

        print('→ Buscando Cuenta')

        # Pantalla Cuentas (Click)
        # driver.find_element(By.XPATH, "//a[@title='Pantalla Única de Consulta']").click()
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'a', 'title', 'Pantalla Única de Consulta')
        if lupa_busqueda_cuenta == False: return False, '', resultadoCarga
        
        # Buscando Elemento
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'title', 'Pantalla Única de Consulta Applet de formulario:Consulta')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        sleep(5)


        # Ingreso Cuenta
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Numero Cuenta')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        input_busqueda_cuenta = driver.find_element(By.XPATH, '//input[contains(@aria-label, "Numero Cuenta")]')
        input_busqueda_cuenta.send_keys(cuenta)
        input_busqueda_cuenta.send_keys(Keys.RETURN)
        print('♦ Cuenta Ingresada ♦')

        # Cargando Cuenta
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Perfil de Pago')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        print('♥ Cuenta OK! ♥')
        sleep(10)

        # Trouble Call (Click boton)
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'title', 'Ítems de Facturación Applet de lista:Generar Trouble Call')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga


        # Validando alert text para obtencion de os
        obtencionOS = True
        contador = 0
        while obtencionOS:
            try:
                sleep(5)
                contador += 1
                print('Obteniendo numero de OS Trouble Call')
                alert = driver.switch_to.alert
                textoAlert = alert.text

                if 'YA EXISTE UNA ORDEN PARA MODIFICAR' in textoAlert.upper(): return False, '','Error Orden Previa Generada'

                patron = re.compile(r"ORDEN NO\.?\s*([\d-]+)", re.IGNORECASE)
                match = patron.search(textoAlert.upper())

                if match:
                    osGenerada = match.group(1)
                    print(f'♦ Orden Trouble Generada: {osGenerada} ♦')
                    obtencionOS = False
                    alert.accept()
                else: return False, '','Error Generacion Trouble Call'

            except:
                if contador == 50: return False, '','Error Generacion Trouble Call'

        # Nueva Consulta OS
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'title', 'Ordenes de Servicio Menú')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        sleep(5)

        posicionNuevaConsulta = obtencionColumna(driver, 'Nueva consulta              [Alt+Q]', pathOpcMenuOS)
        if posicionNuevaConsulta == False: return False, '','Error Estructura Elementos'

        driver.find_element(By.XPATH, pathOpcMenuOS.replace('{contador}', posicionNuevaConsulta)).click()
        sleep(8)

        # Busqueda de OS Generada
        posicionNumeroOrden = obtencionColumna(driver, 'Número de Orden', pathColumnasBOS)
        if posicionNumeroOrden == False: return False, '','Error Estructura Elementos'

        posicionEstado = obtencionColumna(driver, 'Estado', pathColumnasBOS)
        if posicionEstado == False: return False, '','Error Estructura Elementos'

        resultado, resultadoCarga = cargandoElemento(driver, '','','', pathInputBOS.replace('{contador}', posicionNumeroOrden) + '/input[2]')
        if resultado == False:
            resultado, resultadoCarga = cargandoElemento(driver, '','','', pathInputBOS.replace('{contador}', posicionNumeroOrden) + '/input')
            if resultado == False: return False, '',resultadoCarga
        
        # Ingreso de OS
        try: inputBNOS = driver.find_element(By.XPATH, pathInputBOS.replace('{contador}', posicionNumeroOrden) + '/input[2]')
        except:
            try: inputBNOS = driver.find_element(By.XPATH, pathInputBOS.replace('{contador}', posicionNumeroOrden) + '/input')
            except: return False, '','Error Estructura Elementos'

        inputBNOS.send_keys(osGenerada)
        inputBNOS.send_keys(Keys.RETURN)

        # Esperando a que OS aparezca y profundizacion
        resultado, resultadoCarga = cargandoElemento(driver, '','','', pathInputBOS.replace('{contador}', posicionEstado))
        if resultado == False: 
            return False, '',resultadoCarga

        resultado, resultadoCarga = cargandoElemento(driver, '','','', pathInputBOS.replace('{contador}', posicionNumeroOrden) + '/a')
        if resultado == False: return False, '',resultadoCarga

        # Carga de pantalla OS
        # lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Tipo de orden')
        # if lupa_busqueda_cuenta == False: return resultadoCarga

        # Obtenicion de Clave del Vendedor
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Vendedor')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        # valVendedor = driver.find_element(By.XPATH, "//input[@aria-label='Vendedor']")
        # valVendedor = valVendedor.get_attribute('value')

        # Cambio de No. VTS
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'No. VTS')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        noVTS = driver.find_element(By.XPATH, "//input[@aria-label='No. VTS']")
        noVTS.clear()
        noVTS.send_keys('C001')

        # Clave de Tecnico Principal
        # lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Clave del Tecnico Principal')
        # if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        # claveTecnicoPrincipal = driver.find_element(By.XPATH, "//input[@aria-label='Clave del Tecnico Principal']")
        # sleep(1.5)
        # claveTecnicoPrincipal.clear()
        # claveTecnicoPrincipal.send_keys(valVendedor)

        # Tipo Orden
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Tipo de orden')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        tipoOrden = driver.find_element(By.XPATH, "//input[@aria-label='Tipo de orden']")
        tipoOrden.send_keys(Keys.F2)

        resultado, resultadoCarga = cargandoElemento(driver, 'button','title','Seleccionar tipo de pedido Applet de lista:Consulta')
        if resultado == False: return False, '',resultadoCarga

        resultado, resultadoCarga = cargandoElemento(driver, 'input','aria-label','Tipo de pedido')
        if resultado == False: return False, '',resultadoCarga

        tipoOrden = driver.find_element(By.XPATH, "//input[@aria-label='Tipo de pedido']")
        tipoOrden.send_keys('"Trouble Call"')
        tipoOrden.send_keys(Keys.RETURN)

        resultado, resultadoCarga = cargandoElemento(driver, 'button','aria-label','Seleccionar tipo de pedido Applet de lista:Aceptar')
        if resultado == False: return False, '',resultadoCarga

        # Motivo de la Orden
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Motivo de la orden')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        motivoOrden = driver.find_element(By.XPATH, "//input[@aria-label='Motivo de la orden']")
        motivoOrden.clear()
        if 'TROUBLE' in tipoOSOrginal.upper(): motivoOrden.send_keys('Falla Reiterada TC')
        else: motivoOrden.send_keys('Complemento Inst Residencial')
        motivoOrden.send_keys(Keys.RETURN)

        # Referido
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Referido')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        referido = driver.find_element(By.XPATH, "//input[@aria-label='Referido']")
        referido.clear()

        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'textarea', 'aria-labelledby', 'Comments_Label_1')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Referido')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        referido.send_keys('Tecnico')
        referido.send_keys(Keys.RETURN)

        # Comentario
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'textarea', 'aria-labelledby', 'Comments_Label_1')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        sleep(2)
        comentarioinput = driver.find_element(By.XPATH, "//textarea[@aria-labelledby='Comments_Label_1']")
        comentarioinput.send_keys(comentario)

        # Programar OS
        # driver.find_element(By.XPATH, "//button[@aria-label='Orden de servicio Applet de formulario:Programar']").click()
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'aria-label', 'Orden de servicio Applet de formulario:Programar')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        
        # Carga de pantalla OS despues de Programacion
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Motivo de Cancelacion')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga

        #Horario de Atencion
        # Motivo de la Orden
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Horario de Atención')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        print('Horario')
        sleep(5)

        horarioAtencion = driver.find_element(By.XPATH, "//input[@aria-label='Horario de Atención']")
        horarioAtencion.send_keys('Vespertino Trouble Call 14-18')
        horarioAtencion.send_keys(Keys.RETURN)
        sleep(5)
        print('Horario atencion')

        sleep(5)

        # Programar OS
        # driver.find_element(By.XPATH, "//button[@aria-label='Orden de servicio Applet de formulario:Fecha de Atención']").click()
        
        try:
            lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'aria-label', 'Orden de servicio Applet de formulario:Fecha de Atención')
            if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
            sleep(15)

        
            fechaHoy = datetime.now().replace(hour=0, minute=0, second=0)
            print(fechaHoy)
            # fechaHoy = fechaHoy.strftime('%d/%m/%Y %H:%M:%S') 

        except Exception as e:
            print(e)

        buscandoFecha = True
        contador = 1
        while buscandoFecha:
            try:
                contador += 1
                
                pathF = pathOpcFechaAgendar.replace('{contador}', str(contador))
                nameFecha = driver.find_element(By.XPATH, pathF)

                nameFecha = nameFecha.get_attribute('title')
                print(nameFecha)
                nameFecha = datetime.strptime(nameFecha, '%d/%m/%Y %H:%M:%S')
                print(nameFecha)

                if nameFecha > fechaHoy: 
                    driver.find_element(By.XPATH, pathF).click()
                    buscandoFecha = False
                        # return True, osGenerada, ''
                else:
                    if contador == 25: 
                        print('contador 1')
                        sleep(15)
                        return False, '','Error Sin Fechas Disponibles'

            except Exception as e:

                try: 
                    try:
                        pathF = pathOpcFechaAgendar2.replace('{contador}', str(contador))
                        nameFecha = driver.find_element(By.XPATH, pathF)
                    except: return False, '', 'Error Estructura Elementos'

                    nameFecha = nameFecha.get_attribute('title')
                    print(nameFecha)
                    nameFecha = datetime.strptime(nameFecha, '%d/%m/%Y %H:%M:%S')
                    print(nameFecha)

                    if nameFecha > fechaHoy: 
                        driver.find_element(By.XPATH, pathF).click()
                        buscandoFecha = False
                            # return True, osGenerada, ''
                    else:
                        if contador == 25: 
                            print('contador 1')
                            return False, '','Error Sin Fechas Disponibles'
                except:
                    print(e)
                    if contador == 25: 
                        print('contador 1')
                        sleep(15)
                        # return True, osGenerada, ''
                        return False, '','Error Estructura Elementos'
                
        print('Entro bien')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'aria-label', 'Fecha/Hora de atención Applet de lista:Ok')
        if lupa_busqueda_cuenta == False: return False, '',resultadoCarga
        
        return True, osGenerada, ''

    except Exception as e: 
        print(e)
        sleep(40)
        return True, osGenerada, ''
  
def cierreOS(driver, os, tipoOrden, respuestaEncuesta):

    try:
                    #/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[3]/div

        columna = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[{contador}]/div'
                  #/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[3]
        columna2 = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[{contador}]/input'
                  #/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[3]/input
        
        print('→ Cierre OS')

        # Pantalla Consulta (Click)
        # driver.find_element(By.XPATH, "//a[@title='Ordenes de Servicio']").click()
        # lupa_busqueda_os, _ = cargandoElemento(driver, 'a', 'title', 'Página inicial')
        # if lupa_busqueda_os == False: return False, 'Error Pantalla NO Carga'
        lupa_busqueda_os, _ = cargandoElemento(driver, 'a', 'title', 'Ordenes de Servicio')
        if lupa_busqueda_os == False: return False, 'Error Pantalla NO Carga'
        
        # Buscando Elemento
        print('→ Cargando Pantalla busqueda OS')
        lupa_busqueda_os, _ = cargandoElemento(driver, 'button', 'title', 'Ordenes de servicio Applet de lista:Consulta')
        if lupa_busqueda_os == False: return False, 'Error Pantalla NO Carga'
        sleep(5)

        # Ingreso OS
        print('→ Obteniendo posicion columna busqueda No Orden')
        posicion = obtencionColumna(driver, 'Nº de orden', columna)
        if posicion == False: return False, 'Error Pantalla NO Carga'
        sleep(7)

        # driver.find_element(By.XPATH, columna.replace('{contador}', posicion)).click()
        try: input_busqueda_os = driver.find_element(By.XPATH, columna2.replace('/input', '/input[2]').replace('{contador}', posicion))
        except:
            try: input_busqueda_os = driver.find_element(By.XPATH, columna2.replace('{contador}', posicion))
            except: return False, 'Error Estructura Elementos'
        input_busqueda_os.send_keys(os)
        input_busqueda_os.send_keys(Keys.RETURN)
        print('→ OS Ingresada OK!')

        print('→ Cargando OS ←')
        lupa_busqueda_os, _ = cargandoElemento(driver, '', '', '', f'//a[contains(text(), "{os}")]')
        if lupa_busqueda_os == False: return False, 'Error Pantalla NO Carga'
        # sleep(100000)
        lupa_busqueda_os, _ = cargandoElemento(driver, 'input', 'aria-label', 'Sub-Estado')
        if lupa_busqueda_os == False: return False, 'Error Pantalla NO Carga'
        sleep(3)

        driver.find_element(By.XPATH, "//input[@aria-label='Sub-Estado']").click()
        sleep(2)
        input_subestado = driver.find_element(By.XPATH, "//input[@aria-label='Sub-Estado']")
            
        sleep(2)
        input_subestado.clear()
        sleep(2)
        if 'Cancelar' in tipoOrden: input_subestado.send_keys("Fallida")
        else: 
            if 'NO CONTESTA' in respuestaEncuesta.upper(): input_subestado.send_keys("OK Automatico")
            else: input_subestado.send_keys("ok cliente")
        input_subestado.send_keys(Keys.RETURN)
        print('♦ Campo Sub Estado ♦')

        # driver.find_element(By.XPATH, "//input[@aria-label='Estado']").click()
        lupa_busqueda_os, _ = cargandoElemento(driver, 'input', 'aria-label', 'Estado')
        if lupa_busqueda_os == False: return False, _
        sleep(4)
        driver.find_element(By.XPATH, "//button[@aria-label='Orden de servicio Applet de formulario:Guardar']").click()

        # resultado = validacionSubEstado(driver, os,respuestaEncuesta)
        # if resultado == True: pass
        # else: cierreOS(driver, os,tipoOrden,respuestaEncuesta)

        return True, 'Completado'

    except Exception as e: 
        print(f'ERROR EN FUNCION INICIO. ERROR: {e}')
        return False, 'FCierreOS'
    

def generacionCN(driver, cuenta, categoria, motivo, submotivo, solucion, comentario, motivoCliente):

    try:

        pathEstado = '/html/body/div[1]/div/div[5]/div/div[8]/ul[1]/li[{contador}]/div'
        pathColumnasBusCuenta = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[{contador}]/div'
        pathInputBusCuenta = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[1]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[{contador}]'
        pathColumnasGenCN = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[3]/div[2]/div[3]/div/form/span/div/div[3]/div/div/div[3]/div[2]/div/table/thead/tr/th[{contador}]/div'
        pathInputGenCN = '/html/body/div[1]/div/div[5]/div/div[8]/div[2]/div[1]/div/div[3]/div[2]/div[3]/div/form/span/div/div[3]/div/div/div[3]/div[3]/div/div[2]/table/tbody/tr[2]/td[{contador}]'
        
        print('#################### INICIANDO FUNCION GENERACION CN ####################')

        # Pantalla Cuentas (Click)
        print('→ Accediendo a pantalla Cuentas')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'a', 'title', 'Cuentas')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('Pantalla Cuentas OK!')
        
        # Buscando Elemento
        print('→ Accediendo a boton lupa busqueda')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'title', 'Cuentas Applet de lista:Consulta')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('Lupa de busqueda OK!')
        sleep(5)

        # Busqueda Columna Cuenta
        print('→  Obteniendo posicion Nro. Cuenta')
        posicionCuenta = obtencionColumna(driver, 'Nro. Cuenta', pathColumnasBusCuenta)
        if posicionCuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Error Estructura Elementos', ''
            else: return False, resultadoCarga, resultadoCarga
        print('Posicion obtenida OK!')

        # Ingreso Cuenta
        print('→ Accediendo a campo Cuenta')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','', pathInputBusCuenta.replace('{contador}', posicionCuenta))
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('Campo OK!')
        sleep(1)

        print('→ Ingresando Cuenta')
        try: input_busqueda_cuenta = driver.find_element(By.XPATH, pathInputBusCuenta.replace('{contador}', posicionCuenta) + '/input[2]')
        except:
            try: input_busqueda_cuenta = driver.find_element(By.XPATH, pathInputBusCuenta.replace('{contador}', posicionCuenta) + '/input')
            except: return False, 'Error Estructura Elementos', ''

        input_busqueda_cuenta.send_keys(cuenta)
        input_busqueda_cuenta.send_keys(Keys.RETURN)
        print('♦ Cuenta Ingresada ♦')

        # Cargando Cuenta
        print('→ Esperando a que la cuenta cargue')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '', '', '', f'//a[contains(text(), "{cuenta}")]')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Error Cuenta NO Valida'
            else: return False, resultadoCarga, resultadoCarga
        print('♥ Cargando cuenta OK! ♥')
        sleep(5)

        print('→ Profundizando en cuenta')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Cliente Desde')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('♥ Cuenta OK! ♥')
        sleep(10)

        # Crecion CN (Click)
        print('→ Accediento a btn generacion CN')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'title', 'Casos de negocio Applet de lista:Nuevo')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('BTN OK!')
        
        print('→ Validando aparicion formulario')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Cliente Desde')
        if lupa_busqueda_cuenta == False: 
            if resultadoCarga == 'Error Pantalla NO Carga': return False, 'Generado', 'Generado'
            else: return False, resultadoCarga, resultadoCarga
        print('Formulario OK!')

        sleep(5)
        print('→ Leyendo encabezados de formulario')

        posicionCNGenerado = obtencionColumna(driver, 'Caso de negocio', pathColumnasGenCN)
        if posicionCNGenerado == False: return False, 'Error Pantalla NO Carga', ''

        posicionCategoria = obtencionColumna(driver, 'Categoría', pathColumnasGenCN)
        if posicionCategoria == False: return False, 'Error Estructura Elemento', ''

        posicionMotivos = obtencionColumna(driver, 'Motivos', pathColumnasGenCN)
        if posicionMotivos == False: return False, 'Error Estructura Elemento', ''
        
        posicionSubmotivo = obtencionColumna(driver, 'Submotivo', pathColumnasGenCN)
        if posicionSubmotivo == False: return False, 'Error Estructura Elemento', ''
        
        posicionSolucion = obtencionColumna(driver, 'Solución', pathColumnasGenCN)
        if posicionSolucion == False: return False, 'Error Estructura Elemento', ''
        
        posicionComentarios = obtencionColumna(driver, 'Comentarios', pathColumnasGenCN)
        if posicionComentarios == False: return False, 'Error Estructura Elemento', ''

        if 'SIN MOTIVO' not in motivoCliente.upper():
            posicionMotivoCliente = obtencionColumna(driver, 'Motivo Cliente', pathColumnasGenCN)
            if posicionMotivoCliente == False: return False, 'Error Estructura Elemento', ''

        print('Posicion de componentes de formulario OK!')


        # Busqueda Campo Categoria
        print('→ Accediendo a campo categoria')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','', pathInputGenCN.replace('{contador}', posicionCategoria))
        if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga

        print('→ Ingresando Categoria')
        try: input_categoria = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionCategoria) + '/input[2]')
        except: 
            try: input_categoria = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionCategoria) + '/input')
            except: return False, 'Error Estructura Elemento', ''
        
        input_categoria.send_keys(categoria)
        input_categoria.send_keys(Keys.RETURN)
        print('♦ Categoria Ingresada ♦')

        # Busqueda Campo Motivo
        print('→ Accediendo a campo Motivo')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','', pathInputGenCN.replace('{contador}', posicionMotivos))
        if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga

        print('→ Ingresando Motivo')
        try: input_motivo = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionMotivos) + '/input[2]')
        except: 
            try: input_motivo = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionMotivos) + '/input')
            except: return False, 'Error Estructura Elemento', ''

        input_motivo.send_keys(motivo)
        input_motivo.send_keys(Keys.RETURN)
        print('♦ Motivo Ingresado ♦')

        # Busqueda Campo Submotivo
        print('→ Accediendo a Submotivo')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','',pathInputGenCN.replace('{contador}', posicionSubmotivo))
        if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga

        print('→ Ingresando Submotivo')
        try: input_submotivo = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionSubmotivo) + '/input[2]')
        except: 
            try: input_submotivo = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionSubmotivo) + '/input')
            except: return False, 'Error Estructura Elemento', ''

        input_submotivo.send_keys(submotivo)
        input_submotivo.send_keys(Keys.RETURN)
        print('♦ Submotivo Ingresado ♦')

        # Busqueda Campo Solucion
        print('→ Accediendo a Solucion')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','',pathInputGenCN.replace('{contador}', posicionSolucion))
        if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga
        
        print('→ Ingresando Solucion')
        try: input_solucion = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionSolucion) + '/input[2]')
        except: 
            try: input_solucion = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionSolucion) + '/input')
            except: return False, 'Error Estructura Elemento', ''

        input_solucion.send_keys(solucion)
        input_solucion.send_keys(Keys.RETURN)
        print('♦ Solución Ingresada ♦')

        # Busqueda Campo Comentario
        print('→ Accediendo a Comentario')
        resultado, resultadoCarga = cargandoElemento(driver, '','','', pathInputGenCN.replace('{contador}', posicionComentarios))
        if resultado == False: return False, resultadoCarga, resultadoCarga

        print('→ Ingresando comentario')
        try: input_comentario = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionComentarios) + '/textarea')
        except: return False, 'Error Estructura Elemento', ''

        input_comentario.send_keys(comentario)
        print('♦ Comentario Ingresado ♦')

        # Busqueda Campo Motivo Cliente
        if 'SIN MOTIVO' not in motivoCliente.upper():
            print('→ Accedoemdo a Motivo Cliente')
            lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','',pathInputGenCN.replace('{contador}', posicionSolucion))
            if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga
            
            lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, '','','',pathInputGenCN.replace('{contador}', posicionMotivoCliente))
            if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga
            
            print('→ Ingresando Motivo cliente')
            try: input_motivo_cliente = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionMotivoCliente) + '/input[2]')
            except: 
                try: input_motivo_cliente = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionMotivoCliente) + '/input')
                except: return False, 'Error Estructura Elemento', ''

            input_motivo_cliente.send_keys(motivoCliente)
            input_motivo_cliente.send_keys(Keys.RETURN)
            print('♦ Motivo Cliente Ingresado ♦')
            sleep(20)

        try:

            print('→ Obteniendo CN Generado')
            noCN = driver.find_element(By.XPATH, pathInputGenCN.replace('{contador}', posicionCNGenerado) + '/a')
            noCN = noCN.text
            print(f'♦ CN Generado: {noCN} ♦')

            driver.find_element(By.XPATH, f'//a[contains(text(), "{noCN}")]').click()
            print(f'♦ Acceso al CN: {noCN} OK!♦')

        except: return False, 'Error Acceso CN', ''

        print('→ Cargando Pantalla CN ←')
        resultado, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Motivo del cierre', valContador=35)
        if resultado == False:

            if 'Inconsistencia Siebel' in resultadoCarga or 'Error' in resultadoCarga: return False, resultadoCarga, resultadoCarga
            else:
                driver.back()
                lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Cliente Desde')
                if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga

                driver.forward()
                resultado, resultadoCarga = cargandoElemento(driver, 'input', 'aria-label', 'Motivo del cierre', valContador=35)
                if resultado == False: 
                    return False, resultadoCarga, resultadoCarga
            
        # Busqueda Campo Motivo Cierre
        try:
            print('→ Ingresando Motivo cierre')
            driver.find_element(By.XPATH, "//input[@aria-label='Motivo del cierre']").click()
            input_motivo_cierre = driver.find_element(By.XPATH, "//input[@aria-label='Motivo del cierre']")
            input_motivo_cierre.send_keys("RAC INFORMA Y SOLUCIONA")
            print('♦ Campo Motivo Cierre ♦')
        except: return False, 'Error Campo Motivo Cierre', ''

        try:
            print('→ Ingresando Estado')
            # Busqueda Campo Estado
            driver.find_element(By.XPATH, "//input[@aria-label='Estado']").click()
            # sleep(10000)
            sleep(3)
            driver.find_element(By.XPATH, "//span[@id='s_1_1_143_0_icon']").click()
            sleep(3)
            posicion = obtencionColumna(driver, 'Cerrado', pathEstado)
            if posicion == False: return False, 'Error Pantalla NO Carga', ''
            # sleep(10000)
            driver.find_element(By.XPATH, pathEstado.replace('{contador}', posicion)).click()
            print('♦ Campo Estado OK! ♦')
        
        except: return False, 'Error Campo Estado', ''

        print('→ Guardando CN')
        lupa_busqueda_cuenta, resultadoCarga = cargandoElemento(driver, 'button', 'aria-label', 'Caso de negocio Applet de formulario:Guardar')
        if lupa_busqueda_cuenta == False: return False, resultadoCarga, resultadoCarga
        print('CN Guardado y Cerrado OK!')

        return True, noCN, ''

    except Exception as e: 
        print(f'ERROR EN FUNCION INICIO. ERROR: {e}')
        if 'Alert Text:' in str(e): return False, f'Inconsistencia Siebel: {str(e)}', f'Inconsistencia Siebel: {str(e)}'
        return False, 'Generado', 'Generado'
  