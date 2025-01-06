import requests
from bs4 import BeautifulSoup
import json
import re

# URL de la página a scrapear
url = "https://www.dexerto.com/gaming/all-ea-fc-25-licenses-teams-clubs-leagues-stadiums-confirmed-2818441/"

# Realizar la solicitud HTTP
response = requests.get(url)

# Tu código existente
if response.status_code == 200:
    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar la tabla
    table = soup.find("table")
    if table:
        # Diccionario para almacenar los datos organizados
        data = {}

        # Procesar filas de la tabla
        rows = table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) == 3:  # Asegurarse de que haya columnas válidas
                region = columns[0].text.strip()
                league = columns[1].text.strip()
                club_list_raw = columns[2].text.strip()

                # Separar los clubes correctamente usando "–" como delimitador
                club_list = re.split(r"–\s*", club_list_raw.strip())
                club_list = [club.strip() for club in club_list if club]

                if region not in data:
                    data[region] = {}

                if league not in data[region]:
                    data[region][league] = {
                        "logo": f"{league.replace(' ', '_').lower()}.png",
                        "clubs": [],
                    }

                for club_name in club_list:
                    data[region][league]["clubs"].append(
                        {
                            "name": club_name,
                            "logo": (
                                f"{club_name.lower().replace(' ', '_').replace('’', '').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}.png"
                            ),
                        }
                    )

        # Guardar los datos en un archivo JSON
        with open("fc25_teams.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print("Datos guardados en fc25_teams.json")
    else:
        print("No se encontró ninguna tabla en la página.")
else:
    print(f"Error al obtener la página: {response.status_code}")
