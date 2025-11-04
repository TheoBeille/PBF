import pandas as pd
import folium
import os
from ast import literal_eval

# Chemins des fichiers
DATA_DIR = "Données Brutes"
OUTPUT_DIR = "Données Nettoyées"
INFRA_FILE = os.path.join(DATA_DIR, "amenagements-cyclables.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pistes-cyclables.csv")


# --- Ajout des infrastructures cyclables ---
print("Ajout des infrastructures cyclables...")
df_infra = pd.read_csv(INFRA_FILE, sep=';', low_memory=False)

# Utilisation de la colonne 'geo_point_2d' pour les coordonnées
# Elle est au format "lat,lon" (ex: "48.85,2.35")
def extract_lat_lon(geo_str):
    try:
        lat, lon = geo_str.split(',')
        return float(lat.replace(',', '.')), float(lon.replace(',', '.'))
    except:
        return None, None
    
print(df_infra)
# Application de l'extraction sur chaque ligne
df_infra[['lat', 'lon']] = df_infra['geo_point_2d'].apply(lambda x: pd.Series(extract_lat_lon(str(x).replace(' ', ''))))

# Affichage des types d'aménagements cyclables
print("Types d'aménagements cyclables présents :")
print(df_infra['Aménagement'].unique())


output_cols = ['lat', 'lon', 'geo_shape', 'Aménagement', 'Côté aménagement', 'Sens']
df_final = df_infra[output_cols].copy()

# Sauvegarde du CSV nettoyé
df_final.to_csv(OUTPUT_FILE, index=False)




