
#----------Selenium--------------------#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert

# ----------SYSTEM -------------------
from time import sleep
import win32clipboard as cp


ERROR = "HA OCURRIDO UN ERROR EN LA UTILERIA "

def text_box(string, character = '*'):
    '''
    Funcion que imprime un string en una caja

    args:<
        - string (str): cadena a setear
        - character (str): carcater que enmarca el texto
            - default: *
    '''

    len_string = len(string) + 4

    print(character*len_string)
    print(character + ' ' + string + ' ' +character )
    print(character*len_string)

def my_copy(driver):
    '''
    Funcion que teclea 'ctrl + c' para copiar un texto previamente seleccionado y lo asigna a una variable

    args:
        - driver: instancia del navegador

    out:
        - texto: str
    '''
    act = webdriver.ActionChains(driver)
    act.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()

    try:
        sleep(2)
        cp.OpenClipboard()
        sleep(2)
        texto = cp.GetClipboardData()
        cp.EmptyClipboard()
        cp.CloseClipboard()
        if texto and texto != ' ' and texto !='vacio':
            print(f'• Texto copiado: {texto}')
        else:
            return False
        return texto
    except Exception as e:
        mensaje = f"{ERROR} my_copy. ERROR ENCONTRADO {e}"
        print(mensaje)
        return False

def my_copy_by_xpath(driver, xpath , name = None):
    '''
    Funcion que se posiciona en un xpath o name y copia el contenio de la caja

    args:
        - driver: instancia del navegador
        - xpath
        - name
        - id

    out:
        - texto: str
    '''
    act = webdriver.ActionChains(driver)
    try:
        if name != None:
            item  = driver.find_element(By.NAME, name)
        else:
            item  = driver.find_element(By.XPATH, xpath)
        act.click(item)
        act.double_click(item).perform()
        texto = my_copy(driver)

        return texto
    except Exception as e:
        mensaje = f"{ERROR} my_copy_by_xpath. ERROR ENCONTRADO {e}"
        print(mensaje)
        return ''

def description_error(numero_error, nombre_funcion, error = 'No identificado', id = None, name = None, xpath =None):
    '''
    Funcion que manda el tipo de error con su descripcion

    args:
        - numero_error (int): identificador del error
        - nombre_funcion (str): nombre de la funcion donde se tiene el error
        - error (exception): error que lanza el except de la funcion

    '''

    if 'open_item_selenium_wait' in nombre_funcion:
        mensaje = f'CYBER-900: HA OCURRIDO UN ERROR EN LA FUNCION: {str(nombre_funcion)}'
        text_box(mensaje)
        print('Revisar lo siguiente:')
        print(f'Id: {id}')
        print(f'Name: {name}')
        print(f'Xpath: {xpath}')
        print('ERROR ENCONTRADO: \n ')
        print(f'Error: {error}')
        print('▒'*len(mensaje))
        sleep(10)

    else:
        mensaje = f'CYBER-{str(numero_error)}: HA OCURRIDO UN ERROR EN LA FUNCION: {str(nombre_funcion)}.'
        text_box(mensaje)
        print('ERROR ENCONTRADO: \n ')
        print(error)
        print('▒'*len(mensaje))
        sleep(10)

def open_item_selenium_wait(driver, id = None, name = None, xpath = None, clase = None, time  = 45):
    '''
    Funcion que da clics en un item según el metodo de apertura encontrado. Con espera definida

    args:
        - driver
        - Minimo uno de los siguientes:
            - id (str)
            - name
            - xpath
            - clase
    out:
        bool: True si pudo localizar y abirir el elemento indicado

    '''

    wait = WebDriverWait(driver, time)
    act = webdriver.ActionChains(driver)
    sleep(2)
    try:
        if id ==None:
            a = 2/0 #Buscar un excepcion
        #print('Busqueda por ID')
        wait.until(EC.element_to_be_clickable((By.ID, id))).click()
        return True
    except Exception as e:
        #print(e)
        try:
            if name != None:
                    #print('Busqueda por NAME')
                    wait.until(EC.element_to_be_clickable((By.NAME, name))).click()
                    return True
            if xpath != None:
                    #print('Busqueda por XPATH')
                    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                    return True
            if clase != None:
                    #print('Busqueda por CLASS_NAME')
                    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, clase))).click()
                    return True
        except Exception as e:
            print(f'No se pudo abrir el item especificado')
            description_error('06','open_item_selenium_wait',e, id = id, name = name , xpath = xpath)
            return False

def AlertaSaldoVencido(driver):
    sleep(3)
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print('SI hubo alerta')
        sleep(3)
    except Exception as e:
        print('NO hubo alerta')

def my_send_keys(driver, key, repeticiones = 1):
    '''
    Funcion que teclea en pantalla
    '''
    act = webdriver.ActionChains(driver)
    for i in range(repeticiones):
        act.send_keys(exec(key))

