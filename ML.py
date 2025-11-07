
from sklearn.neighbors import BallTree
import os 
import numpy as np
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
from shapely import wkt


DATA_DIR = "Données_Nettoyées"

ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidents_velos.csv")
INFRA_FILE = os.path.join(DATA_DIR, "pistes-cyclables.csv")
CHANT_FILE=os.path.join(DATA_DIR, "chantiers_perturb.csv")
df_acc = pd.read_csv(ACCIDENTS_FILE, sep=',', low_memory=False)
df_ame = pd.read_csv(INFRA_FILE, sep=',', low_memory=False)
df_chant=pd.read_csv(CHANT_FILE, sep=',', low_memory=False)

#objectif: faire un gros data frame qui est le data frame des accidents avec en plus si chantier avec son nivea et l'amenagement et ses caracteridtiques 

#POUR LE CHANTIER;

df_chant['début']=pd.to_datetime(df_chant['début'])
df_chant['fin']=pd.to_datetime(df_chant['fin'])
df_acc['Date']=pd.to_datetime(df_acc['Date'])



# --- Proximité géographique via BallTree (Haversine) ---
R_EARTH = 6_371_000  # rayon terrestre (m)
radius_m = 150        # seuil de proximité (à ajuster)
radius_rad = radius_m / R_EARTH

acc_rad = np.radians(df_acc[["lat", "lon"]].to_numpy())
chant_rad = np.radians(df_chant[["lat", "lon"]].to_numpy())

tree = BallTree(chant_rad, metric="haversine") #permet de faire une recherhce de voisins spatiales
neighbors = tree.query_radius(acc_rad, r=radius_rad)  # liste d'indices chantier pour chaque accident


pairs = []  # (i_acc, i_chant)
for i_acc, idxs in enumerate(neighbors): #idx tableau des chantiers proche de l'accident 
    if len(idxs) == 0:
        continue
    d = df_acc.iloc[i_acc]["Date"]
    cand = df_chant.iloc[idxs]
    cand = cand[(cand["début"] <= d) & (cand["fin"] >= d)]
    for j in cand.index:
        pairs.append((i_acc, j))

df_acc["perturbation"] = 0  # défaut si aucun chantier proche & actif

if pairs:
    pairs_df = pd.DataFrame(pairs, columns=["i_acc", "i_chant"])
    merged = pairs_df.merge(
        df_chant[["Niveau de perturbation"]], left_on="i_chant", right_index=True, how="left"
    )
    agg = merged.groupby("i_acc")["Niveau de perturbation"].max().astype(int)
    df_acc.loc[agg.index, "perturbation"] = agg.values

#prend le chantier au niveau max; si égalité, on garde le premier.


#print((df_acc["perturbation"] != 0).sum()) 
#print(df_acc[df_acc["perturbation"] != 0])



#les acc dans les ame

df_ame["geometry"] = df_ame["geo_shape"].apply(lambda s: shape(json.loads(s)))
pistes = gpd.GeoDataFrame(df_ame, geometry="geometry", crs="EPSG:4326")



lat_col = "lat"
lon_col = "lon"

acc = gpd.GeoDataFrame(
    df_acc.copy(),
    geometry=gpd.points_from_xy(df_acc[lon_col], df_acc[lat_col]), #permet de faire des coor (x,y) avec le bon type
    crs="EPSG:4326"
)

# Projection métrique pour des distances en mètres
acc_m    = acc.to_crs(2154)
pistes_m = pistes.to_crs(2154)


# Assure un index unique côté accidents et pistes
acc_m = acc_m.reset_index(drop=True)
pistes_m = pistes_m.reset_index(drop=True)

# Jointure plus proche (peut renvoyer plusieurs lignes par accident en cas d’égalité)
merged = gpd.sjoin_nearest(
    acc_m, 
    pistes_m, 
    how="left", 
    distance_col="dist_m"
)

piste_cols = [col for col in merged.columns if col in df_ame.columns or col.endswith("_right")]

mask_loin = merged["dist_m"] > 2
merged.loc[mask_loin, piste_cols] = None  # met NaN sur les colonnes de piste si accidents > a 2m


merged = merged.to_crs(4326)




merged_no_geo = merged.drop(columns="geometry").copy()

cols_to_keep = [
    "Date", "lat_left","lon_left","Gravité","perturbation",
    "dist_m",
    "Côté aménagement","Sens",
    "Aménagement",
    "Côté aménagement",
    "Gravité",
    
]

merged_no_geo = merged_no_geo[cols_to_keep]

merged_no_geo['dist_m'] = np.where(merged_no_geo['dist_m'].notna(), merged_no_geo['dist_m'] <= 2, False)
merged_no_geo =merged_no_geo.rename(columns={"lat_left": "lat", "lat_right": "lon", "dist_m": "ame"})

output_path = "Données_Nettoyées/accidents_avec_amenagement.csv"
merged_no_geo.to_csv(output_path, index=False, sep=';')
