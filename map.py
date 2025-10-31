import pandas as pd
import folium
import os

# Chemins des fichiers
DATA_DIR = "Données Nettoyées"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidents_velos.csv")

# Chargement des données nettoyées
print("Chargement des accidents vélos nettoyés...")
df_accidents = pd.read_csv(ACCIDENTS_FILE)

# Vérification des colonnes de coordonnées
lat_col = [c for c in df_accidents.columns if 'lat' in c.lower()][0]
lng_col = [c for c in df_accidents.columns if 'lng' in c.lower() or 'lon' in c.lower()][0]

# Création de la carte
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Définition des couleurs par type d'accident
type_colors = {
    'Blessés Légers': 'orange',
    'Blessés hosp': 'blue',
    'Tué': 'black',
    'Aucun': 'gray'
}

# Ajout des points d'accidents vélos avec couleur selon gravité
for _, row in df_accidents.iterrows():
    # Détermination du type d'accident (priorité : Tué > Blessés hosp > Blessés Légers)
    accident_type = 'Aucun'
    if row.get('Tué', 0) == 1:
        accident_type = 'Tué'
    elif row.get('Blessés hospitalisés', 0) == 1:
        accident_type = 'Blessés hosp'
    elif row.get('Blessés Légers', 0) == 1:
        accident_type = 'Blessés Légers'
    color = type_colors.get(accident_type, 'gray')
    folium.CircleMarker(
        location=[row[lat_col], row[lng_col]],
        radius=3,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=f"Type: {accident_type}"
    ).add_to(m)

# Ajout d'une légende personnalisée
legend_html = '''
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
m.get_root().html.add_child(folium.Element(legend_html))

# Sauvegarde de la carte
output_map = os.path.join("Cartes", "carte_accidents_velos.html")
m.save(output_map)
print(f"Carte enregistrée sous {output_map}")
