import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor


# Función para obtener la URL de la primera imagen
def get_first_image_url(query):
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver = webdriver.Chrome()
    driver.get(search_url)

    try:
        time.sleep(3)  # Esperar 3 segundos después de cargar la página
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".czzyk.XOEbc"))
        )
        element.click()
        time.sleep(3)  # Esperar 3 segundos después de hacer clic en el primer elemento
        next_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sFlh5c.FyHeAf.iPVvYb"))
        )
        image_url = next_element.get_attribute("src")
    except Exception as e:
        print(f"Error al obtener la URL de la imagen: {e}")
        image_url = None
    finally:
        driver.quit()

    return image_url


# Función para descargar la imagen
def download_image(url, file_name):
    try:
        os.makedirs("logos", exist_ok=True)
        file_path = os.path.join("logos", file_name)
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Imagen guardada como {file_path}")
        else:
            print(
                f"No se pudo descargar la imagen. Código de estado: {response.status_code}"
            )
    except Exception as e:
        print(f"Error al descargar la imagen: {e}")


# Función para agregar logo a la lista de descargas
def add_logo_to_download(args):
    query, logo_name = args
    image_url = get_first_image_url(query)
    if image_url:
        return (image_url, logo_name)
    else:
        print(f"No se encontró ninguna imagen para {query}")
        return None


# Leer el archivo JSON
with open("fc25_teams.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Preparar las consultas para obtener las URLs de los logos
queries = []
downloaded_logos = set()

for country, country_data in data.items():
    # Logo de la región
    region_logo_name = country_data["logo"]
    if region_logo_name not in downloaded_logos:
        region_query = f"wikipedia bandera {region_logo_name.replace('_', ' ').replace('.png', '')}"
        queries.append((region_query, region_logo_name))
        downloaded_logos.add(region_logo_name)

    # Omitir la primera liga y procesar las demás
    first_league = True
    for league, league_data in country_data["leagues"].items():
        if first_league:
            first_league = False
            continue

        # Logo de la liga
        league_logo_name = league_data.get("logo")
        if league_logo_name and league_logo_name not in downloaded_logos:
            league_query = f"wikipedia liga logo {league_logo_name.replace('_', ' ').replace('.png', '')}"
            queries.append((league_query, league_logo_name))
            downloaded_logos.add(league_logo_name)

        for club in league_data["clubs"]:
            # Logo del club
            club_logo_name = club["logo"]
            if club_logo_name not in downloaded_logos:
                club_query = f"wikipedia escudo equipo {club_logo_name.replace('_', ' ').replace('.png', '')}"
                queries.append((club_query, club_logo_name))
                downloaded_logos.add(club_logo_name)

# Obtener las URLs de los logos utilizando multiprocessing
with Pool(processes=6) as pool:
    logo_urls = pool.map(add_logo_to_download, queries)

# Filtrar los resultados válidos
logo_urls = [result for result in logo_urls if result is not None]

# Descargar las imágenes utilizando multithreading
with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(lambda args: download_image(*args), logo_urls)
