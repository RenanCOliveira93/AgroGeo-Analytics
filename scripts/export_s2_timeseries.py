"""Extrai série NDVI/NDRE por talhão do Sentinel-2 SR Harmonized via Earth Engine.

Requer autenticação (veja docs/pt-BR/00_guia_de_estudo.md e README). Saída: CSV longo
com colunas date, talhao_id, ndvi, ndre (média zonal a 10 m, composição mensal por mediana).

Uso:
  python scripts/export_s2_timeseries.py --talhoes data/sample/talhoes_sinteticos.geojson \
      --start 2021-01-01 --end 2024-12-31 --out data/processed/serie_s2.csv
Para talhões REAIS, passe seu próprio GeoJSON (EPSG:4326, coluna talhao_id).
"""
import argparse
from pathlib import Path

import geopandas as gpd

from agrogeo import ee_utils
from agrogeo.config import DATA_PROCESSED, END_DATE, START_DATE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--talhoes", required=True)
    ap.add_argument("--start", default=START_DATE)
    ap.add_argument("--end", default=END_DATE)
    ap.add_argument("--max-cloud", type=float, default=60)
    ap.add_argument("--out", default=str(DATA_PROCESSED / "serie_s2.csv"))
    a = ap.parse_args()

    ee_utils.init_ee()
    g = gpd.read_file(a.talhoes)
    fc = ee_utils.gdf_to_fc(g)
    col = ee_utils.s2_collection(fc.geometry(), a.start, a.end, a.max_cloud)
    monthly = ee_utils.monthly_composites(col, a.start, a.end)
    df = ee_utils.zonal_timeseries(monthly, fc)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"OK: {len(df)} linhas -> {a.out}")


if __name__ == "__main__":
    main()
