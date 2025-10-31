import pandas as pd
import os

# Chemins des fichiers
DATA_DIR = "Données Brutes"
OUTPUT_DIR = "Données Nettoyées"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidentologie0.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "accidents_velos.csv")

# Création du dossier de sortie si besoin
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Chargement des données
df = pd.read_csv(ACCIDENTS_FILE, sep=';', low_memory=False)

# Filtrage : on garde uniquement les accidents impliquant des vélos
# On utilise la colonne 'Mode' pour filtrer
if 'Mode' in df.columns:
    df_velos = df[df['Mode'].str.lower().str.strip() == 'vélo']
else:
    df_velos = df.copy()

# Nettoyage : suppression des lignes sans coordonnées
lat_col = [c for c in df_velos.columns if 'lat' in c.lower()][0]
lng_col = [c for c in df_velos.columns if 'lng' in c.lower() or 'lon' in c.lower()][0]
df_velos = df_velos.dropna(subset=[lat_col, lng_col])
df_velos[lat_col] = df_velos[lat_col].astype(str).str.replace(',', '.').astype(float)
df_velos[lng_col] = df_velos[lng_col].astype(str).str.replace(',', '.').astype(float)

# Création des colonnes gravité à partir de la colonne 'Gravité'
def gravite_from_categorie(val):
    val = str(val)
    
    if 'Tué' in val:
        
        return pd.Series({'Tué': 1, 'Blessés hospitalisés': 0, 'Blessés Légers': 0})
    elif 'Blessé hospitalisé' in val:
        return pd.Series({'Tué': 0, 'Blessés hospitalisés': 1, 'Blessés Légers': 0})
    elif 'Blessé léger' in val:
        return pd.Series({'Tué': 0, 'Blessés hospitalisés': 0, 'Blessés Légers': 1})
    else:
        return pd.Series({'Tué': 0, 'Blessés hospitalisés': 0, 'Blessés Légers': 0})

df_velos[['Tué', 'Blessés hospitalisés', 'Blessés Légers']] = df_velos['Gravité'].apply(gravite_from_categorie)

# On ne garde que les colonnes utiles (coordonnées, gravité, date)
if 'Date' in df_velos.columns:
    output_cols = [lat_col, lng_col, 'Date'] + ['Tué', 'Blessés hospitalisés', 'Blessés Légers']
else:
    output_cols = [lat_col, lng_col] + ['Tué', 'Blessés hospitalisés', 'Blessés Légers']
df_final = df_velos[output_cols].copy()

# Sauvegarde du CSV nettoyé
df_final.to_csv(OUTPUT_FILE, index=False)
