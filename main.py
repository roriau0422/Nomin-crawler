# Author: Temuujin.KH (https://github.com/roriau0422)
# Python Version: 3.x

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from models.content_model import Product
import platform
import time
import os
import subprocess
import json
import requests
import re
import mysql.connector

choices = ["Тавилга", "Эрэгтэй", "Эмэгтэй", "Хүүхдийн", "Спорт, аялал", "Цахилгаан хэрэгсэл", "Технологи", "Гоо сайхан", "Үнэт эдлэл"]

for i, choice in enumerate(choices, 1):
    print(f"{i}. {choice}")

while True:
    user_input = input("Категорийн дугаарыг оруулна уу: ")
    if user_input.isdigit() and 1 <= int(user_input) <= len(choices):
        break
    else:
        print("Буруу утга оруулсан байна.")

chrome_mode = input("Chrome-ийг ачааллахдаа headless төлөвтэй эхлүүлэх үү? энгийн төлөвтэй эхлүүлэх үү? ('headless' эсвэл 'normal' гэж бичнэ үү): ")

selected_choice = choices[int(user_input) - 1]

if selected_choice == "Тавилга":
    url = "https://shoppy.mn/t/home-furniture"
elif selected_choice == "Эрэгтэй":
    url = "https://shoppy.mn/t/men"
elif selected_choice == "Эмэгтэй":
    url = "https://shoppy.mn/t/women"
elif selected_choice == "Хүүхдийн":
    url = "https://shoppy.mn/t/kids"
elif selected_choice == "Спорт, аялал":
    url = "https://shoppy.mn/t/sport-and-camping"
elif selected_choice == "Цахилгаан хэрэгсэл":
    url = "https://shoppy.mn/t/appliences"
elif selected_choice == "Технологи":
    url = "https://shoppy.mn/t/technology"
elif selected_choice == "Гоо сайхан":
    url = "https://shoppy.mn/t/beauty"
elif selected_choice == "Үнэт эдлэл":
    url = "https://shoppy.mn/t/jewelry"

os_name = platform.system()
os_arch = platform.machine()

def get_webdriver_path(chrome_version_input, os_name_input, os_arch_input):

    """
        Chrome-ын хувилбар, үйлдлийн систем болон архитектурт тулгуурлан тохирох Chrome веб драйверын замыг буцаана.

        Оролт:
        chrome_version_input (str): Chrome-ын хувилбар.
        os_name_input (str): Үйлдлийн системийн нэр.
        os_arch_input (str): Үйлдлийн системийн архитектур.

        Буцах:
        str: Chrome вэб драйверын зам.

        Алдаа үүсэх нь:
        ValueError: Хэрэв Chrome хувилбар дэмжигдээгүй эсвэл үйлдлийн систем дэмжигдээгүй бол.
    """

    if chrome_version_input != '124':
        raise ValueError("Chrome-ын хувилбар таарахгүй байна. Chrome-ын 124 хувилбарыг суулгана уу.")
    if os_name_input == "Windows":
        return os.path.join("packages", "chromedriver", "chromedriver.exe")
    elif os_name_input == "Darwin":
        if os_arch_input == "x86_64":
            return os.path.join("packages", "chromedriver", "chromedriver_x64")
        elif os_arch_input == "arm64":
            return os.path.join("packages", "chromedriver", "chromedriver_arm64")
    else:
        raise ValueError(f"Тус үйлдлийн системийг дэмжихгүй: {os_name_input}")
    
def get_chrome_options(chrome_mode):

    """
       Хүссэн горимд (headless эсвэл normal)-д үндэслэн Chrome-ын сонголтыг буцаана.
      
       Оролт:
       chrome_mode (str): Chrome-ын горим.
      
       Буцах:
       Сонголтууд: Chrome сонголтуудын объект.
      
       Алдаа үүсэх нь:
       ValueError: Хэрэв Chrome горим нь "headless" эсвэл "normal" биш байвал.
    """

    if chrome_mode.lower() not in ['headless', 'normal']:
        raise ValueError("Chrome төлөв нь 'headless' эсвэл 'normal' байх ёстой.")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-features=CloudManagement")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    if chrome_mode.lower() == 'headless':
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
    else:
        options.add_argument("--start-maximized")
    return options

def get_chrome_version():

    """
        Системд суулгасан Chrome-ын хувилбарыг буцаана.  

        Буцах:
        str: Chrome-ын хувилбар.        

        Алдаа үүсэх нь:
        ValueError: Хэрэв үйлдлийн систем дэмжигдээгүй бол.
    """

    os_name = platform.system()
    if os_name == "Windows":
        chrome_path = os.path.join(os.environ['PROGRAMFILES'], 'Google', 'Chrome', 'Application', 'chrome.exe')
        if not os.path.exists(chrome_path):
            chrome_path = os.path.join(os.environ['PROGRAMFILES(X86)'], 'Google', 'Chrome', 'Application', 'chrome.exe')
        if not os.path.exists(chrome_path):
            return None
        chrome_path = chrome_path.replace("\\", "\\\\")
        command = f'wmic datafile where name="{chrome_path}" get Version /value'
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        version = output.split("=")[1].strip()
        version_parts = version.split(".")
        version = version_parts[0]
        return version
    elif os_name == "Darwin":
        command = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version"
        output = subprocess.check_output(command, shell=True).decode('UTF-8')
        version = output.strip().split(' ')[2]
        version_parts = version.split('.')
        version = version_parts[0]
        return version
    else:
        raise ValueError(f"Үйлдлийн систем тохирохгүй: {os_name}")

chrome_version = get_chrome_version()

try:
    webdriver_path = get_webdriver_path(chrome_version, os_name, os_arch)
    options = get_chrome_options(chrome_mode)
except ValueError as e:
    print(e)
    quit()

def main():
    driver = webdriver.Chrome(service=Service(executable_path=webdriver_path), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    products_section = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "products-container")))
    time.sleep(5)
    if len(products_section.find_elements(By.XPATH, ".//div[@itemtype='https://schema.org/Product']")) > 0:
        print("Бүтээгдэхүүнүүд амжилттай уншигдлаа.")
        scroll_pause_time = 0.5
        end_time = time.time() + 10

        while time.time() < end_time:
            driver.execute_script("window.scrollBy({ top: 960, behavior: 'smooth' });")
            time.sleep(scroll_pause_time)
            driver.execute_script("window.scrollBy({ top: document.body.scrollHeight, behavior: 'smooth' });")

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        product_divs = soup.select('.products-container div[itemtype="https://schema.org/Product"]')
        products = []
        for product_div in product_divs:
            sku = product_div.find('meta', {'itemprop': 'sku'})['content']
            mpn = product_div.find('meta', {'itemprop': 'mpn'})['content']
            description = product_div.find('meta', {'itemprop': 'description'})['content']
            image_url = product_div.find('img', {'itemprop': 'image'})['src']
            brand = product_div.find('meta', {'itemprop': 'name'})['content']
            name = product_div.find('h4', {'itemprop': 'name'}).text
            alternate_name = product_div.find('h5', {'itemprop': 'alternateName'}).text
            price = product_div.find('span', {'itemprop': 'price'}).text

            product = Product(sku, mpn, description, image_url, brand, name, alternate_name, price)
            product_json = json.dumps(product.to_dict(), indent=4, ensure_ascii=False)
            products.append(product_json)
            print(product_json)
        num_products = len(product_divs)
        print(f"{selected_choice} категорид {num_products} бүтээгдэхүүн байна.")
        driver.minimize_window()
        txt_choose = input("Бүтээгдэхүүнүүдийг текст файлд хадгалах уу? (Y/N): ")
        if txt_choose.lower() == "y":
            with open(f"{selected_choice}.txt", "w", encoding="utf-8") as f:
                for product in products:
                    f.write(product + "\n")
            print(f"{selected_choice}.txt файлд амжилттай хадгалагдлаа.")
    else:
        print("Бүтээгдэхүүн унших процесс амжилтгүй.")
        print(driver.page_source)
        driver.quit()
        quit()
    driver.quit()
    quit()

if __name__ == "__main__":
    main()