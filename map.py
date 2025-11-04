import pandas as pd
import folium
import os
from ast import literal_eval   # <-- manquait

# Chemins des fichiers
DATA_DIR = "Données Nettoyées"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidents_velos.csv")
INFRA_FILE = os.path.join(DATA_DIR, "pistes-cyclables.csv")

print("Chargement des accidents vélos nettoyés...")
df_accidents = pd.read_csv(ACCIDENTS_FILE)

# Colonnes lat/lon accidents (auto-détection)
lat_col = [c for c in df_accidents.columns if 'lat' in c.lower()][0]
lng_col = [c for c in df_accidents.columns if 'lng' in c.lower() or 'lon' in c.lower()][0]

# Carte de base
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Couleurs accidents
type_colors_acc = {
    'Blessés Légers': 'orange',
    'Blessés hosp': 'blue',
    'Tué': 'black',
    'Aucun': 'gray'
}

# Points d'accidents
acc_layer = folium.FeatureGroup(name="Accidents vélo", show=True)
for _, row in df_accidents.iterrows():
    accident_type = 'Aucun'
    if row.get('Tué', 0) == 1:
        accident_type = 'Tué'
    elif row.get('Blessés hospitalisés', 0) == 1:
        accident_type = 'Blessés hosp'
    elif row.get('Blessés Légers', 0) == 1:
        accident_type = 'Blessés Légers'
    color = type_colors_acc.get(accident_type, 'gray')
    folium.CircleMarker(
        location=[row[lat_col], row[lng_col]],
        radius=3,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=f"Type: {accident_type}"
    ).add_to(acc_layer)
acc_layer.add_to(m)

# ---------- Infrastructures cyclables ----------
print("Ajout des infrastructures cyclables...")

# IMPORTANT : le CSV nettoyé est séparé par virgules (pas ';')
df_infra = pd.read_csv(INFRA_FILE)  # <-- supprimer sep=';'

# On n’essaie pas de ré-extraire depuis geo_point_2d (pas présent dans le fichier nettoyé)
# On attend déjà 'lat' et 'lon' dans ce fichier
if not {'lat','lon'}.issubset(df_infra.columns):
    raise ValueError("Le fichier 'pistes-cyclables.csv' doit contenir les colonnes 'lat' et 'lon'.")

# Colonne du type d'aménagement
type_col = 'Aménagement'
if type_col not in df_infra.columns:
    raise ValueError("La colonne 'Aménagement' est absente de 'pistes-cyclables.csv'.")

print("Types d'aménagements cyclables présents :", df_infra[type_col].unique())


def color_for_amg(txt: str) -> str:
    t = (txt or "").lower()
    if "piste" in t:
        return "blue"
    if "bande" in t:
        return "green"
    if "double-sens" in t:   
        return "cadetblue"
    if "couloir" in t and "bus" in t:
        return "orange"
    if "voie verte" in t or "mixte" in t:
        return "purple"
    if "voie piétonne" in t or "piétonne" in t:
        return "darkpurple"
    return "gray"
infra_points_layer = folium.FeatureGroup(name="Infrastructures (points)", show=False)
infra_lines_layer = folium.FeatureGroup(name="Infrastructures (lignes)", show=True)

# Limiter pour performance
max_points = 1000

# Points (si lat/lon présents)
count_points = 0
for _, row in df_infra.iterrows():
    if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
        if count_points >= max_points:
            break
        color = color_for_amg(str(row.get(type_col)))
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=str(row.get(type_col))
        ).add_to(infra_points_layer)
        count_points += 1

infra_points_layer.add_to(m)

# Lignes depuis 'geo_shape' si présent et de type LineString
if 'geo_shape' in df_infra.columns:
    count_lines = 0
    for _, row in df_infra.iterrows():
        if count_lines >= max_points:
            break
        geo = row.get('geo_shape')
        if pd.isna(geo):
            continue
        try:
            g = literal_eval(geo)
            if isinstance(g, dict) and g.get('type') == 'LineString':
                # coords format : [[lon, lat], ...]
                coords = g.get('coordinates', [])
                if coords and isinstance(coords[0], (list, tuple)) and len(coords[0]) >= 2:
                    latlon = [[pt[1], pt[0]] for pt in coords]
                    color = color_for_amg(str(row.get(type_col)))
                    name = row.get('Nom', '(sans nom)')
                    longueur = row.get('Longueur', '?')
                    folium.PolyLine(
                        latlon,
                        color=color,
                        weight=4,
                        opacity=0.7,
                        popup=f"{name}<br>Longueur: {longueur} m<br>Type: {row.get(type_col)}"
                    ).add_to(infra_lines_layer)
                    count_lines += 1
        except Exception:
            # on ignore les formes non parsables
            pass

infra_lines_layer.add_to(m)

# Légendes
legend_acc_html = '''
 <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 220px; height: 120px; 
     background-color: white; z-index:9999; font-size:14px; border:1px solid #ccc; padding:10px;">
     <b>Légende gravité accident vélo</b><br>
     <span style="color:orange">●</span> Blessés Légers<br>
     <span style="color:blue">●</span> Blessés hospitalisés<br>
     <span style="color:black">●</span> Tué<br>
     <span style="color:gray">●</span> Aucun
 </div>
'''
m.get_root().html.add_child(folium.Element(legend_acc_html))

legend_infra_html = '''
 <div style="position: fixed; 
     bottom: 50px; left: 290px; width: 200px; height: 120px; 
     background-color: white; z-index:9999; font-size:14px; border:1px solid #ccc; padding:10px;">
     <b>Légende infrastructures</b><br>
     <span style="color:blue">●</span> Piste<br>
     <span style="color:green">●</span> Bande<br>
     <span style="color:orange">●</span> Couloir de bus<br>
     <span style="color:purple">●</span> Voie verte/mixte<br>
     <span style="color:gray">●</span> Autre
 </div>
'''
m.get_root().html.add_child(folium.Element(legend_infra_html))

# Contrôle des calques
folium.LayerControl().add_to(m)

# Sauvegarde
output_map = os.path.join("Cartes", "carte_accidents_velos.html")
os.makedirs(os.path.dirname(output_map), exist_ok=True)
m.save(output_map)
print(f"Carte enregistrée sous {output_map}")