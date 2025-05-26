from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import shutil
import os
import time

#Utilizatori de test
users = [
    {"username": "standard_user", "password": "secret_sauce"},
    {"username": "problem_user", "password": "secret_sauce"},
    {"username": "performance_glitch_user", "password": "secret_sauce"}
]

#Creează driver cu opțiuni robuste și profil curat
def create_driver_with_clean_profile():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    temp_profile_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.temp_profile_dir = temp_profile_dir
    return driver

#Curăță resursele
def cleanup_driver(driver):
    try:
        driver.quit()
    finally:
        if hasattr(driver, "temp_profile_dir") and os.path.exists(driver.temp_profile_dir):
            shutil.rmtree(driver.temp_profile_dir)

#Login si logout dacă e necesar
def login(driver, username, password):
    driver.get("https://www.saucedemo.com/")
    time.sleep(1)

    if "inventory.html" in driver.current_url:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))).click()
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-button")))
        except:
            driver.get("https://www.saucedemo.com/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-button")))

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-name"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 10).until(EC.url_contains("inventory.html"))

    time.sleep(2)  #Pauză vizuală după login

#Adaugă 3 produse în coș
def add_items_to_cart(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item")))

    added = 0
    while added < 3:
        buttons = driver.find_elements(By.CSS_SELECTOR, ".inventory_item button")
        for btn in buttons:
            if btn.text.strip().lower() == "add to cart":
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(btn)).click()
                added += 1
                time.sleep(1)  #Pauză vizuală după adăugare
                break  #Regăsește lista butoanelor după modificare

    #Verificare badge coș
    cart_badge = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    )
    assert cart_badge.text == "3", f"Eroare: doar {cart_badge.text} produse adăugate!"
    time.sleep(2)  #Pauză vizuală

#Checkout complet
def checkout(driver):
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "checkout"))).click()

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "first-name"))).send_keys("Ion")
    driver.find_element(By.ID, "last-name").send_keys("Popescu")
    driver.find_element(By.ID, "postal-code").send_keys("123456")
    time.sleep(2)  # Pauză după completarea formularului

    driver.find_element(By.ID, "continue").click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "finish"))).click()
    confirmation = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "complete-header"))
    )
    assert "THANK YOU FOR YOUR ORDER" in confirmation.text

    time.sleep(3)  #Pauză finală pentru a vedea mesajul de confirmare

# Rulează testul complet pentru un user
def run_test_for_user(user):
    driver = create_driver_with_clean_profile()
    try:
        login(driver, user["username"], user["password"])
        add_items_to_cart(driver)
        checkout(driver)
        print(f"Test reușit pentru {user['username']}")
    except Exception as e:
        print(f"Eroare pentru {user['username']}: {str(e)}")
        input("Apasă Enter pentru a închide browserul...")
    finally:
        cleanup_driver(driver)

 #Rulează testele pentru toți utilizatorii
for user in users:
    run_test_for_user(user)
