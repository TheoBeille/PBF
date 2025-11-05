import pandas as pd
from sklearn.neighbors import BallTree
import os 
import numpy as np

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


print((df_acc["perturbation"] != 0).sum()) 
print(df_acc[df_acc["perturbation"] != 0])

