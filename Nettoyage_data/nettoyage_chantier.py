import pandas as pd
import os 

DATA_DIR = "Données_Brutes"
OUTPUT_DIR = "Données_Nettoyées"
ACCIDENTS_FILE = os.path.join(DATA_DIR, "chantiers-perturbants.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chantiers_perturb.csv")

df = pd.read_csv(ACCIDENTS_FILE, sep=';', low_memory=False)

#On travaille ensuite sur notre dataframe seul : 
#Données d'intérêt dans les chantiers : Voie(s) (à discuter), Date début/fin, Niveau de perturbation, (geo_shape (forme chantier) => en première approche pas besoin, mais sinon on le 
# rentre dans notre df comme les coordonnées pour sep colonnes), geo_point_2d(coord chantier)
#jsp si "impact sur description" a du sens parce que "IMPASSE" ne nous fournit pas beaucoup d'infos (à discuter)

#On ne garde du coup que ces deux colonnes : 
df_new = df[['Voie(s)', 'Date de début', 'Date de fin', 'Niveau de perturbation']]
df_new = df_new.rename(columns={'Date de début': 'début', 'Date de fin': 'fin'})
#ajout des deux colonnes pour les coordonnées (manip pour séparer en deux colonnes distinctes) : 
df_new[['lat', 'lon']] = df['geo_point_2d'].str.split(',', expand=True)

# Nettoyage si données manquantes : On fait ici le choix de n'enlever que les lignes où les coordonnées (lat ou lon) sont 
# manquantes + niveau de perturbation manquant car ce sont les deux seules données dont on a besoin pour estimer la perturbation je pense (à discuter)
df_new = df_new.dropna(subset=['lat', 'lon'])

df_new.fillna({'Niveau de perturbation':0},inplace=True)

#On convertit les types pour avoir des entiers : 
df_new['lat'] = df_new['lat'].astype(str).str.replace(',', '.').astype(float)
df_new['lon'] = df_new['lon'].astype(str).str.replace(',', '.').astype(float)
df_new['Niveau de perturbation'] = df_new['Niveau de perturbation'].astype(int) #pour avoir des entiers et pas des float ni des str


output_cols = ['Voie(s)', 'lat', 'lon', 'début', 'fin', 'Niveau de perturbation']
df_final = df_new[output_cols].copy()

print(df_final.head())


#Conversion en CSV : 
df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
