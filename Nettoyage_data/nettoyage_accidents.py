import pandas as pd
import os


DATA_DIR = "Données_Brutes"
OUTPUT_DIR = "Données_Nettoyées"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidentologie0.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "accidents_velos.csv")


df = pd.read_csv(ACCIDENTS_FILE, sep=';', low_memory=False)



#que les accidents de velo 
if 'Mode' in df.columns:
    df = df[df['Mode'] == 'Vélo']
    
df = df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
# Conversion et suppression des lignes invalides
df = df.dropna(subset=['lat', 'lon']) #enleve les lignes sans coordonnées 
df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
df['lon'] = df['lon'].astype(str).str.replace(',', '.').astype(float)


df['Tué']=3*df['Tué']
df['Blessés hospitalisés']=2*df['Blessés hospitalisés']
df["Gravité"] = df[["Blessés hospitalisés", "Tué", "Blessés Légers"]].sum(axis=1, skipna=True)
#
output_cols = ['Date','lat', 'lon', 'Gravité']
df_final = df[output_cols].copy()
#print(df_final.head())

df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')