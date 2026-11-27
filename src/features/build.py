# src/features/build.py
"""Pasar las series crudas a una tabla mensual (fin de mes)."""
import pandas as pd

# Cómo resumir cada serie dentro del mes
COMO = {
    "T10Y2Y": "mean", "T10Y3M": "mean", "DGS2": "mean", "DGS10": "mean",
    "BAA10Y": "mean", "VIXCLS": "mean", "DTWEXBGS": "mean", "NFCI": "mean",
    "FEDFUNDS": "last", "CPIAUCSL": "last", "UNRATE": "last",
    "INDPRO": "last", "USREC": "last", "GS10": "last", "TB3MS": "last", "BAA": "last"
}


def a_mensual(s: pd.Series, como: str) -> pd.Series:
    if como == "mean":
        return s.resample("ME").mean()
    elif como == "last":
        return s.resample("ME").last()


def panel_mensual(series: dict[str, pd.Series]) -> pd.DataFrame:
    lista = series.copy()
    for id, s in series.items():
        como = COMO[id]
        lista[id] = a_mensual(s, como)
    return pd.concat(lista.values(), axis=1)

def agregar_sustitutos(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()

    # TB3MS viene en base descuento → la paso a rendimiento real
    d = p["TB3MS"] / 100                          # de % a decimal (5.0 → 0.05)
    #p["TB3MS"] / 100 divide toda la columna de una vez, sin loop.
    tb3_real = 365 * d / (360 - 91 * d) * 100     # fórmula, y de vuelta a %

    p["CURVA_10Y3M_LARGA"] = p["GS10"] - tb3_real
    p["SPREAD_BAA_LARGO"] = p["BAA"] - p["GS10"]
    
    return p