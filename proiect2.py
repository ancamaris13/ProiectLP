#service = Service(executable_path="./chromedriver")
#Test automatizat pentru https://www.saucedemo.com/
#Sursa de inspirație: https://selenium-python.readthedocs.io/

#Importuri necesare pentru Selenium și manipularea fișierelor/profilurilor temporare
from selenium import webdriver
from selenium.webdriver.common.by import By   #pentru localizarea elementelor HTML
from selenium.webdriver.chrome.service import Service  #pentru a porni ChromeDriver
from selenium.webdriver.chrome.options import Options  #pentru opțiuni personalizate la Chrome
from selenium.webdriver.support.ui import WebDriverWait  #pentru așteptări explicite
from selenium.webdriver.support import expected_conditions as EC  #pentru condiții de așteptare
from webdriver_manager.chrome import ChromeDriverManager  #instalează automat ultima versiune de ChromeDriver
import tempfile  #pentru a crea foldere temporare
import shutil  #pentru a șterge foldere temporare
import os  #pentru operații cu fișiere
import time  #pentru a introduce întârzieri


#Listă de utilizatori pentru testare multiplă
users = [
    {"username": "standard_user", "password": "secret_sauce"},
    {"username": "problem_user", "password": "secret_sauce"},
    {"username": "performance_glitch_user", "password": "secret_sauce"}
]

#Creează un driver cu profil temporar curat(fara cookies)
def create_driver_with_clean_profile():
    options = Options()
    options.add_argument("--start-maximized") #pornește browserul maximizat

    #Creează un director temporar pentru profilul utilizatorului
    temp_profile_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile_dir}") #folosește profilul temporar

    #Creează serviciul ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)  #lansează Chrome

    #Atașează directorul temporar la driver pentru a-l putea șterge ulterior
    driver.temp_profile_dir = temp_profile_dir
    return driver

#Închide driverul și șterge profilul temporar
def cleanup_driver(driver):
    try:
        driver.quit() #închide browserul
    finally:
        if hasattr(driver, "temp_profile_dir") and os.path.exists(driver.temp_profile_dir):
            shutil.rmtree(driver.temp_profile_dir) #șterge directorul temporar

#Funcție de autentificare
def login(driver, username, password):
    driver.get("https://www.saucedemo.com/") #deschide pagina principală

    #Dacă ești logat deja, fă logout
    if "inventory.html" in driver.current_url or "checkout" in driver.current_url or "checkout-complete" in driver.current_url:
        try:
            print(" Se încearcă logout...")
            menu_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn")))
            menu_button.click()
            logout_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
            logout_button.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-button")))
        except Exception as e:
            print("Nu s-a putut face logout:", e)
            driver.get("https://www.saucedemo.com/")
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "login-button")))

            #Login normal
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-name"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()


#Adaugă produse în coș
def add_items_to_cart(driver):

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn_inventory")))
    add_buttons = driver.find_elements(By.CLASS_NAME, "btn_inventory")
    for i in range(3):  #adaugă doar primele 3 produse
        add_buttons[i].click()
    cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
    assert cart_badge.text == "3", "Nu sunt 3 produse în coș!"  #verifică că sunt 3 produse


#Checkout complet
def checkout(driver):
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()  #deschide pagina coșului
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "checkout"))).click()


#Completează formularul de checkout
    driver.find_element(By.ID, "first-name").send_keys("Ion")
    driver.find_element(By.ID, "last-name").send_keys("Popescu")
    driver.find_element(By.ID, "postal-code").send_keys("123456")
    driver.find_element(By.ID, "continue").click()

    driver.find_element(By.ID, "finish").click()
    confirmation = driver.find_element(By.CLASS_NAME, "complete-header")
    assert "THANK YOU FOR YOUR ORDER" in confirmation.text #verifică confirmarea comenzii

#Rulează test pentru fiecare user
def run_test_for_user(user):
    driver = create_driver_with_clean_profile() #creează un browser cu profil curat
    try:
        login(driver, user["username"], user["password"]) #autentificare
        add_items_to_cart(driver) #adaugă produse în coș
        checkout(driver) #finalizează comanda
        print(f" Test finalizat cu succes pentru {user['username']}")
        time.sleep(2)  #pauza pentru a vedea rezultatul
    except Exception as e:
        print(f" Eroare pentru {user['username']}: {str(e)}")
        input("Apasă Enter pentru a închide browserul după eroare...") #așteaptă input dacă apare o eroare
    finally:
        cleanup_driver(driver) #închide browserul și curăță fișierele

#Rularea testelor pentru toți utilizatorii
for user in users:
    run_test_for_user(user) #ruleaza testul pentru toti utilizatorii

