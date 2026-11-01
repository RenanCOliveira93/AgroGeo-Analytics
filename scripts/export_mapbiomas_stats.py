"""Área por classe MapBiomas dentro de cada talhão/município (Earth Engine).

Saída: CSV com talhao_id, classe, area_ha. Requer autenticação.
Uso: python scripts/export_mapbiomas_stats.py --geojson data/sample/municipio_3538808.geojson --year 2023
"""
import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

from agrogeo import ee_utils
from agrogeo.config import DATA_PROCESSED, MAPBIOMAS_CLASSES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", required=True)
    ap.add_argument("--id-col", default=None)
    ap.add_argument("--year", type=int, default=2023)
    ap.add_argument("--out", default=str(DATA_PROCESSED / "mapbiomas_area.csv"))
    a = ap.parse_args()
    ee = ee_utils.init_ee()
    g = gpd.read_file(a.geojson)
    id_col = a.id_col or ("talhao_id" if "talhao_id" in g.columns else "cod_ibge")
    fc = ee_utils.gdf_to_fc(g, id_col)
    img = ee_utils.mapbiomas_image(a.year)
    area = ee.Image.pixelArea().divide(10_000).addBands(img)
    red = area.reduceRegions(
        collection=fc, scale=30,
        reducer=ee.Reducer.sum().group(groupField=1, groupName="classe"))
    rows = []
    for f in red.getInfo()["features"]:
        for grp in f["properties"].get("groups", []):
            rows.append({id_col: f["properties"][id_col], "classe": int(grp["classe"]),
                         "classe_nome": MAPBIOMAS_CLASSES.get(int(grp["classe"]), "outra"), "area_ha": grp["sum"]})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)
    print(f"OK -> {a.out}")


if __name__ == "__main__":
    main()
