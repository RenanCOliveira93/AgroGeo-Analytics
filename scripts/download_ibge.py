"""Baixa malhas municipais do IBGE (API de Malhas v3) e salva em data/sample.

Uso: python scripts/download_ibge.py [--codigo 3538808] [--vizinhos]
Fonte: https://servicodados.ibge.gov.br/api/docs/malhas (dados públicos do IBGE).
"""
import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"
API = "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{cod}"
LOC = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{cod}"
# Piraju e municípios vizinhos (códigos conferidos na API de Localidades do IBGE)
VIZINHOS = {3538808: "Piraju", 3515400: "Fartura", 3551207: "Sarutaiá", 3554201: "Tejupá", 3554607: "Timburi"}


def fetch(cod: int, qualidade: str = "intermediaria") -> gpd.GeoDataFrame:
    r = requests.get(API.format(cod=cod), params={"formato": "application/vnd.geo+json", "qualidade": qualidade}, timeout=60)
    r.raise_for_status()
    g = gpd.GeoDataFrame.from_features(json.loads(r.text)["features"], crs="EPSG:4326")
    nome = requests.get(LOC.format(cod=cod), timeout=30).json()["nome"]
    g["cod_ibge"], g["nome"] = cod, nome
    return g[["cod_ibge", "nome", "geometry"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codigo", type=int, default=3538808)
    ap.add_argument("--vizinhos", action="store_true", help="baixa também os municípios vizinhos")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cods = list(VIZINHOS) if a.vizinhos else [a.codigo]
    g = pd.concat([fetch(c) for c in cods], ignore_index=True)
    g = gpd.GeoDataFrame(g, crs="EPSG:4326")
    dest = OUT / ("municipios_regiao_piraju.geojson" if a.vizinhos else f"municipio_{a.codigo}.geojson")
    g.to_file(dest, driver="GeoJSON")
    print(f"OK: {len(g)} município(s) -> {dest}")


if __name__ == "__main__":
    sys.exit(main())
