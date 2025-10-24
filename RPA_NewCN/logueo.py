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
        options.add_argument("--log-level=3")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--disable-default-apps")
        options.add_argument('--headless=new')  # ← Headless activado
        # Tamaño grande (alto generoso para evitar menús plegados)
        options.add_argument("--window-size=1920,2000")
        # Evita zoom/DPI del SO (Windows suele forzar 125%)
        options.add_argument("--high-dpi-support=1")
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": 1920,
            "height": 2000,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        # driver = webdriver.Chrome(
        #                         executable_path =r"C:\Rpa_CX_Bots_Proxmox\Rpa_Ajustes_CV\driver_chrome\\chromedriver.exe",
        #                         options=options
        #                         )
        sleep(3)
        print('▬ Webdriver abierto correctamente')
        return driver
    except Exception as e:
        description_error('01','start_webdriver',e)
        return False

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
    if driver == False: return False, False, 'Generado'
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
            sleep(15)
            
            #Validacion de credencailaes correctas
            try:
                status_bar  = driver.find_element(By.ID,"statusBar")
                errorCredenciales = driver.execute_script("return arguments[0].textContent;", status_bar)
                print(errorCredenciales)
                if 'incorrecta' in errorCredenciales:
                    print('CLAVES INVALIDAS')
                    driver.close()
                    driver.quit()
                    return False, False, 'Claves Invalidas'
            except:
                text_box(f'INICIO DE SESION EXITOSO: evazquezgu', '▬')
        else:
            text_box('NO SE PUDO ENCONTRAR LA PESTAÑA DE SIEBEL')
            driver.close()
            driver.quit()
            return False, False, ''
        
        return driver, True, ''
    
    except Exception as e:
        description_error('02','login_siebel',e)
        driver.close()
        driver.quit()
        return False, False, ''



