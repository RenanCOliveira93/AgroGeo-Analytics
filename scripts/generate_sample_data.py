"""Gera os dados de exemplo SINTÉTICOS (talhões, série NDVI/NDRE, raster) em data/sample.

Pré-requisito: data/sample/municipio_3538808.geojson (scripts/download_ibge.py).
Uso: python scripts/generate_sample_data.py
"""
import geopandas as gpd

from agrogeo.config import DATA_SAMPLE
from agrogeo.synthetic import make_ndvi_raster, make_talhoes, make_timeseries


def main():
    muni = gpd.read_file(DATA_SAMPLE / "municipio_3538808.geojson")
    tal = make_talhoes(muni)
    tal.to_file(DATA_SAMPLE / "talhoes_sinteticos.geojson", driver="GeoJSON")
    ts = make_timeseries(tal)
    ts.to_csv(DATA_SAMPLE / "serie_sintetica_ndvi_ndre.csv", index=False)
    make_ndvi_raster(tal, DATA_SAMPLE / "ndvi_sintetico.tif")
    print(f"talhões: {len(tal)} | linhas da série: {len(ts)}")


if __name__ == "__main__":
    main()
