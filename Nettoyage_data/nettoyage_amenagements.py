import pandas as pd
import numpy as np
import os
from ast import literal_eval

DATA_DIR = "Données_Brutes"
OUTPUT_DIR = "Données_Nettoyées"
INFRA_FILE = os.path.join(DATA_DIR, "amenagements-cyclables.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pistes-cyclables.csv")




df = pd.read_csv(INFRA_FILE, sep=';', low_memory=False)
df[['lat', 'lon']] = df['geo_point_2d'].str.split(',', expand=True)

df = df.dropna(subset=["lat", "lon"])
print(df.head())


output_cols = ["lat", "lon","Longueur", "geo_shape", "Aménagement", "Côté aménagement", "Sens"]
df_final = df[output_cols].copy()
df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")


