import requests
from bs4 import BeautifulSoup as Bs
from selenium import webdriver
from time import sleep
import os
import json
from settings import *

file_path = os.path.join(os.getcwd(), "lists.json")
with open(file_path) as file:
    data: dict = json.load(file)
print(data["words"])

for subject in data["words"]:
    folder_path = os.path.join(os.getcwd(), "images")
    nom_dossier = subject
    nom_complet = str(folder_path) + "/" + str(nom_dossier)
    if not os.path.exists(nom_complet):
        os.mkdir(f'{folder_path}/{nom_dossier}')
        print(f"Le dossier '{nom_dossier}' a été créé avec succès.")
    else:
        print(f"Le dossier '{nom_dossier}' existe déjà.")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    url = f'https://www.pinterest.fr/search/pins/?q={subject}'
    driver.get(url)
    rawlinks = []
    for i in range (1,scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(time_sleep)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_position = driver.execute_script("return window.pageYOffset + window.innerHeight")
        if scroll_position >= scroll_height:
            break
        soup = driver.page_source
        links = Bs(soup, 'html.parser')
        links = links.find_all('a')
        for link in links:
            rawlinks.append(link)
    driver.quit()
    linkstab = []
    j=0
    for link in rawlinks:
        link_url = link.get("href")
        if "/pin/" in link_url:
            j+=1
            if j%2 == 0:
                linkstab.append(link_url)
        else:
            print("Ceci n'est pas un URL valide")
    i=0

    for link in linkstab:
        url = f"https://www.pinterest.fr{link}"
        digits = link[-5:]
        digits = digits.replace('/','')
        response = requests.get(url)
        html = response.text
        soup = Bs(html,'html.parser')
        img = soup.find('img')
        img_url = img.get('src')
        try:
            linkcreator = soup.find("div", {"data-test-id": "official-user-attribution"})
            acreator = linkcreator.find("a")
            creator = acreator.get("href")
            creator = creator.replace('/', '')
        except:
            creator = "NoUserCreation"
        img_data = requests.get(img_url).content
        img_len = len(img_data)
        try:
            if(img_len>10000):
                if creator in data["banlist"]:
                    print("Utilisateur bloqué")
                else:
                    filename = f'{nom_complet}/{creator}_{digits}.jpg'
                    with open(filename, 'wb') as file:
                        file.write(img_data)
                    print(f"L'image n°{i} a été téléchargée avec succès.")
        except:
            print(f"L'image n°{i} n'a pas été téléchargée avec succès.")
        i+=1