import json
import psycopg2
from psycopg2.extras import execute_batch

# Leer el archivo JSON
with open("fc25_teams.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname="",
    user="",
    password="",
    host="",
    port="",
)
cur = conn.cursor()

# Insertar datos en la base de datos
for region_name, region_data in data.items():
    # Insertar región
    cur.execute(
        """
        INSERT INTO "Region" (id, name, logo)
        VALUES (gen_random_uuid(), %s, %s)
        ON CONFLICT (name) DO UPDATE SET logo = EXCLUDED.logo
        RETURNING id;
    """,
        (region_name, region_data["logo"]),
    )
    region_id = cur.fetchone()[0]

    for league_name, league_data in region_data["leagues"].items():
        # Insertar liga
        cur.execute(
            """
            INSERT INTO "League" (id, name, logo, "regionId")
            VALUES (gen_random_uuid(), %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET logo = EXCLUDED.logo, "regionId" = EXCLUDED."regionId"
            RETURNING id;
        """,
            (league_name, league_data["logo"], region_id),
        )
        league_id = cur.fetchone()[0]

        # Preparar datos de los equipos
        teams = [
            (club["name"], club["logo"], league_id) for club in league_data["clubs"]
        ]

        # Insertar equipos
        execute_batch(
            cur,
            """
            INSERT INTO "Team" (id, name, logo, "leagueId")
            VALUES (gen_random_uuid(), %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET logo = EXCLUDED.logo, "leagueId" = EXCLUDED."leagueId";
            """,
            teams,
        )

# Confirmar los cambios y cerrar la conexión
conn.commit()
cur.close()
conn.close()
