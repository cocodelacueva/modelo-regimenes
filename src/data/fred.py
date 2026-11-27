# src/data/fred.py
"""Bajada de series de FRED y guardado de crudos en data/raw."""
import os
from datetime import date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# src/data/fred.py → parents[0]=src/data, [1]=src, [2]=raíz del repo
RAW = Path(__file__).resolve().parents[2] / "data" / "raw"

# Series de la sección 4.1, más DGS2 y DGS10 (tu duda de qué tasa mueve la curva)
SERIES = {
    "T10Y2Y":   "Curva 10a - 2a",
    "T10Y3M":   "Curva 10a - 3m",
    "DGS2":     "Tasa Tesoro 2a",
    "DGS10":    "Tasa Tesoro 10a",
    "FEDFUNDS": "Tasa Fed",
    "CPIAUCSL": "IPC EE.UU. (nivel)",
    "UNRATE":   "Desempleo",
    "INDPRO":   "Producción industrial",
    "BAA10Y":   "Spread crédito Baa",
    "NFCI":     "Condiciones financieras",
    "VIXCLS":   "VIX",
    "DTWEXBGS": "Índice dólar amplio",
    "USREC":    "Recesiones NBER (solo validación)",
    "GS10":     "Tasa Tesoro 10a",
    "TB3MS":    "Tasa Tesoro 3m",
    "BAA":      "Tasa Baa"
}


def cliente() -> Fred:
    load_dotenv()
    return Fred(api_key=os.environ["FRED_API_KEY"])


def bajar(serie_id: str, fred: Fred) -> pd.Series:
    serie = fred.get_series(serie_id)    
    serie.name = serie_id
    return serie


def guardar_crudo(s: pd.Series) -> Path:
    hoy = date.today().isoformat()
    path = RAW / f"{s.name}_{hoy}.parquet"
    s.to_frame(s.name).to_parquet(path)
    return path


def bajar_todas() -> dict[str, pd.Series]:
    series_dict = {}
    fred = cliente()
    for serie_id in SERIES.keys():
        serie = bajar(serie_id, fred)
        guardar_crudo(serie)
        series_dict[serie_id] = serie
        print(f"{serie_id} | {serie.index.min()} → {serie.index.max()} | {len(serie)} | {serie.isna().sum()}")
    return series_dict