#----------Selenium--------------------#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains


#---------- UTILERIAS --------------------#
from utileria import *
import ApiCyberHubOrdenes as api

# ----------SYSTEM -------------------
from time import sleep
import win32clipboard as cp

#-----------OTRAS--------------------
from json.decoder import JSONDecodeError

ERROR = "HA OCURRIDO UN ERROR EN LA FUNCION "
SIEBEL = 'https://crm.izzi.mx/siebel/app/ecommunications/esn'

def start_webdriver():
    '''
    Esta funcion inicializa el webdriver (Chrome)
    
    out: 
        - driver: instancia de google chrome
    '''
    try:
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1024,768')
        driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome(
        #                         executable_path =r"C:\Rpa_CX_Bots_Proxmox\Rpa_Ajustes_CV\driver_chrome\\chromedriver.exe",
        #                         options=options
        #                         )
        sleep(3)
        print('▬ Webdriver abierto correctamente')
        return driver
    except Exception as e:
        description_error('01','start_webdriver',e)

def login(usuario, contraseña):
    '''
    Funcion que hace el logeo en SIEBEL
    args:
        - user (str): usuario de siebel
        - pass (str): contraseña de siebel

    out:
        - driver(obj): instancia del navegador
        - stutus (bool): True si el incio de sesion fue correcto, False en caso contrario
    '''
    driver  = start_webdriver()
    driver.maximize_window()
    # sleep(10000)
    try:

        driver.get(SIEBEL)
        
        act = webdriver.ActionChains(driver)
        sleep(5)
        #En caso de que el explorador tenga conflicto con el protocolo de seguridad
        if  "Privacy" in driver.title or "privacidad" in driver.title or "Privacidad" in driver.title:
            print('♀ Error de privacidad')
            sleep(3)
            elem = driver.find_element(By.ID, "details-button").click()
            sleep(2)
            act.key_down(Keys.TAB)
            sleep(2)
            elem = driver.find_element(By.ID, "proceed-link").click()
            sleep(3)
            print('♀ Error de privacidad CERRADO')

            sleep(5)

        #Busca que el titulo de la pesataña sea el correcto

        # Escenario S1
        if "Siebel Communications" in driver.title:
            #USER
            elem = driver.find_element(By.NAME,"SWEUserName")
            elem.clear()
            elem.send_keys(usuario)
            sleep(1)

            #PASSWORD
            elem = driver.find_element(By.NAME,"SWEPassword")
            elem.clear()
            elem.send_keys(contraseña)
            sleep(1)

            #LOGIN (click)
            driver.find_element(By.ID,"s_swepi_22").click()
            sleep(5)
            
            #Validacion de credencailaes correctas
            try:
                status_bar  = driver.find_element(By.ID,"statusBar")
                act.click(status_bar)
                act.double_click(status_bar).perform()
                texto = my_copy(driver)
                if 'incorrecta' in texto:
                    print('CLAVES INVALIDAS')
                    driver.close()
                    driver.quit()
                    return False, False
            except:
                text_box(f'INICIO DE SESION EXITOSO: evazquezgu', '▬')
        else:
            text_box('NO SE PUDO ENCONTRAR LA PESTAÑA DE SIEBEL')
            driver.close()
            driver.quit()
            return False, False
        
        return driver, True
    
    except Exception as e:
        description_error('02','login_siebel',e)
        driver.close()
        driver.quit()
        return False, False



