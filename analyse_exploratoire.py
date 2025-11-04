import pandas as pd
import folium
import os
from ast import literal_eval

# Chemins des fichiers
DATA_DIR = "Données Brutes"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidentologie0.csv")
INFRA_FILE = os.path.join(DATA_DIR, "amenagements-cyclables.csv")

# 1. Chargement des données
print("Chargement des données...")
df_accidents = pd.read_csv(ACCIDENTS_FILE, sep=';', low_memory=False)

# 2. Nettoyage des données
print("Nettoyage des données...")
# Suppression des lignes sans coordonnées
if 'lat' in df_accidents.columns and 'lng' in df_accidents.columns:
    lat_col = 'lat'
    lng_col = 'lng'
    df_accidents = df_accidents.dropna(subset=[lat_col, lng_col])
else:
    # Recherche des colonnes de coordonnées
    lat_col = [c for c in df_accidents.columns if 'lat' in c.lower()][0]
    lng_col = [c for c in df_accidents.columns if 'lng' in c.lower() or 'lon' in c.lower()][0]
    df_accidents = df_accidents.dropna(subset=[lat_col, lng_col])

# Correction du format des coordonnées (remplacement des virgules par des points et conversion en float)
df_accidents[lat_col] = df_accidents[lat_col].astype(str).str.replace(',', '.').astype(float)
df_accidents[lng_col] = df_accidents[lng_col].astype(str).str.replace(',', '.').astype(float)

# 3. Agrégation par quartier (exemple: arrondissement)
if 'arrondissement' in df_accidents.columns:
    accidents_par_arrdt = df_accidents.groupby('arrondissement').size()
    print("Accidents par arrondissement:")
    print(accidents_par_arrdt)

# 4. Visualisation sur une carte
print("Création de la carte Folium...")
# Centre Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Ajout des points d'accidents
for _, row in df_accidents.iterrows():
    folium.CircleMarker(
        location=[row[lat_col], row[lng_col]],
        radius=3,
        color='red',
        fill=True,
        fill_opacity=0.5
    ).add_to(m)

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

# Application de l'extraction sur chaque ligne
df_infra[['lat', 'lon']] = df_infra['geo_point_2d'].apply(lambda x: pd.Series(extract_lat_lon(str(x).replace(' ', ''))))

# Affichage des types d'aménagements cyclables
print("Types d'aménagements cyclables présents :")
print(df_infra['Aménagement'].unique())

# Type d'aménagement : colonne 'Aménagement'
type_col = 'Aménagement'

# Définition des couleurs par type d'aménagement
infra_types = df_infra[type_col].unique()
type_colors = {
    'Piste': 'blue',
    'Bande': 'green',
    'Couloir de bus': 'orange',
    'Voie mixte': 'purple',
    'Autre': 'gray'
}

# Ajout des infrastructures sur la carte (limité à 1000 points pour éviter lenteur)
max_points = 1000
for i, row in enumerate(df_infra.iterrows()):
    if i >= max_points:
        break
    _, row = row
    infra_type = str(row[type_col])
    color = type_colors.get(infra_type, 'gray')
    if not pd.isna(row['lat']) and not pd.isna(row['lon']):
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=infra_type
        ).add_to(m)

# Ajout des infrastructures sous forme de lignes (polylines)
for i, row in enumerate(df_infra.iterrows()):
    if i >= max_points:
        break
    _, row = row
    infra_type = str(row[type_col])
    color = type_colors.get(infra_type, 'gray')
    # Utilisation de geo_shape pour tracer la ligne
    if pd.notna(row['geo_shape']):
        try:
            # Format attendu: {'type': 'LineString', 'coordinates': [[lon, lat], ...]}
            geo = literal_eval(row['geo_shape'])
            if geo['type'] == 'LineString':
                coords = [[lat, lon] for lon, lat in geo['coordinates']]
                folium.PolyLine(
                    coords,
                    color=color,
                    weight=4,
                    opacity=0.7,
                    popup=f"{row['Nom']}<br>Longueur: {row['Longueur']} m<br>Type: {infra_type}"
                ).add_to(m)
        except Exception as e:
            pass

# Ajout d'une légende personnalisée
legend_html = '''
 <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: 120px; 
     background-color: white; z-index:9999; font-size:14px; border:1px solid #ccc; padding:10px;">
     <b>Légende infrastructures cyclables</b><br>
     <span style="color:blue">●</span> Piste<br>
     <span style="color:green">●</span> Bande<br>
     <span style="color:orange">●</span> Couloir de bus<br>
     <span style="color:purple">●</span> Voie mixte<br>
     <span style="color:gray">●</span> Autre
 </div>
 '''
m.get_root().html.add_child(folium.Element(legend_html))

# Sauvegarde de la carte
m.save("carte_accidents.html")
print("Carte enregistrée sous carte_accidents.html")

# Pour aller plus loin : visualiser les infrastructures, croiser les données, etc.
