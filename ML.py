import pandas as pd
import geopandas as gpd
from shapely import wkt
import os 

DATA_DIR = "Données Nettoyées"

ACCIDENTS_FILE = os.path.join(DATA_DIR, "accidents_velos.csv")
INFRA_FILE = os.path.join(DATA_DIR, "pistes-cyclables.csv")

df_acc = pd.read_csv(ACCIDENTS_FILE, sep=';', low_memory=False)
df_ame = pd.read_csv(INFRA_FILE, sep=';', low_memory=False)
