"""Dados SINTÉTICOS para demonstração offline.

ATENÇÃO: nada aqui é medição. Polígonos, séries NDVI/NDRE e raster são gerados por
modelos simples com semente fixa, apenas para exercitar o código e a didática.
Todo produto gerado carrega o marcador ``SINTETICO``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from scipy.ndimage import uniform_filter
from shapely import affinity
from shapely.geometry import box

from .config import CRS_GEO, CRS_UTM22S

CULTIVARES = ["Catuaí Vermelho", "Mundo Novo", "Arara", "Catuaí Amarelo"]


def make_talhoes(municipio: gpd.GeoDataFrame, n_cols: int = 4, n_rows: int = 3, seed: int = 42) -> gpd.GeoDataFrame:
    """Gera talhões retangulares fictícios (levemente rotacionados) dentro do município.

    O agrupamento é ancorado em um ponto interno do município (representative_point).
    Retorna GeoDataFrame em EPSG:4326 com ``SINTETICO=True``.
    """
    rng = np.random.default_rng(seed)
    muni = municipio.to_crs(CRS_UTM22S).union_all()
    anchor = muni.representative_point()
    x0, y0 = anchor.x - n_cols * 450 / 2, anchor.y - n_rows * 400 / 2
    rows = []
    k = 1
    for r in range(n_rows):
        for c in range(n_cols):
            w, h = rng.uniform(220, 360), rng.uniform(200, 320)
            cx = x0 + c * 450 + 225 + rng.uniform(-30, 30)
            cy = y0 + r * 400 + 200 + rng.uniform(-30, 30)
            poly = affinity.rotate(box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
                                   rng.uniform(-12, 12), origin=(cx, cy))
            rows.append({
                "talhao_id": f"T{k:02d}",
                "nome": f"Talhão sintético {k:02d}",
                "cultivar": CULTIVARES[(k - 1) % len(CULTIVARES)],
                "ano_plantio": int(rng.integers(2008, 2020)),
                "SINTETICO": True,
                "geometry": poly,
            })
            k += 1
    gdf = gpd.GeoDataFrame(rows, crs=CRS_UTM22S)
    gdf = gdf[gdf.within(muni)].reset_index(drop=True)
    return gdf.to_crs(CRS_GEO)


# Probabilidade de observação inutilizável (nuvem/sombra) por mês: verão chuvoso > inverno seco
CLOUD_PROB = {1: .60, 2: .60, 3: .50, 4: .35, 5: .25, 6: .15, 7: .12, 8: .12, 9: .25, 10: .40, 11: .50, 12: .60}


def make_timeseries(talhoes: gpd.GeoDataFrame, start="2021-01-01", end="2024-12-31",
                    step_days: int = 5, seed: int = 7) -> pd.DataFrame:
    """Série SINTÉTICA de NDVI/NDRE por talhão e data (formato longo).

    Componentes simulados: nível-base por talhão, sazonalidade suave (mínimo no inverno seco),
    ruído AR(1), ruído comum de cena, lacunas por nuvem e dois eventos injetados:
      * T03: queda tipo "poda/esqueletamento" em ago/2023 com recuperação gradual;
      * T08: nível reduzido de forma persistente a partir de mar/2023 (anomalia relativa).
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq=f"{step_days}D")
    doy = dates.day_of_year.values
    seasonal = 0.035 * np.cos(2 * np.pi * (doy - 30) / 365.25)  # máx. ~jan, mín. ~jul
    common = rng.normal(0, 0.01, len(dates))
    cloud_p = np.array([CLOUD_PROB[m] for m in dates.month])
    recs = []
    for tid in talhoes["talhao_id"]:
        base = rng.uniform(0.68, 0.80)
        ar = np.zeros(len(dates))
        for i in range(1, len(dates)):
            ar[i] = 0.6 * ar[i - 1] + rng.normal(0, 0.012)
        ndvi = base + seasonal + common + ar
        if tid == "T03":
            t0 = pd.Timestamp("2023-08-10")
            dt = (dates - t0).days.values
            ndvi = ndvi - np.where(dt >= 0, 0.18 * np.exp(-dt / 70.0), 0.0)
        if tid == "T08":
            ndvi = ndvi - np.where(dates >= pd.Timestamp("2023-03-01"), 0.07, 0.0)
        ndre = 0.62 * ndvi - 0.04 + rng.normal(0, 0.008, len(dates))
        cloudy = rng.random(len(dates)) < cloud_p
        recs.append(pd.DataFrame({
            "date": dates, "talhao_id": tid,
            "ndvi": np.where(cloudy, np.nan, np.clip(ndvi, -1, 1)),
            "ndre": np.where(cloudy, np.nan, np.clip(ndre, -1, 1)),
            "valid_pixel_frac": np.where(cloudy, 0.0, rng.uniform(0.85, 1.0, len(dates))),
        }))
    df = pd.concat(recs, ignore_index=True)
    df["SINTETICO"] = True
    return df


def make_ndvi_raster(talhoes: gpd.GeoDataFrame, path, res: float = 10.0, seed: int = 11) -> str:
    """Raster NDVI SINTÉTICO (10 m, EPSG:31982): talhões de NDVI alto sobre entorno de NDVI baixo,
    com borda suavizada (3x3) para imitar mistura de pixels."""
    rng = np.random.default_rng(seed)
    g = talhoes.to_crs(CRS_UTM22S)
    minx, miny, maxx, maxy = g.total_bounds
    minx, miny = np.floor((minx - 100) / res) * res, np.floor((miny - 100) / res) * res
    maxx, maxy = np.ceil((maxx + 100) / res) * res, np.ceil((maxy + 100) / res) * res
    width, height = int((maxx - minx) / res), int((maxy - miny) / res)
    transform = from_origin(minx, maxy, res, res)
    arr = rng.normal(0.35, 0.04, (height, width))  # entorno: pasto/solo/estrada
    for i, geom in enumerate(g.geometry):
        m = rasterize([(geom, 1)], out_shape=(height, width), transform=transform).astype(bool)
        level = rng.uniform(0.66, 0.80)
        arr[m] = rng.normal(level, 0.03, m.sum())
    # mistura de pixels: filtro 3x3 simula a resposta espacial do sensor nas bordas dos talhões
    arr = uniform_filter(arr, size=3, mode="nearest")
    arr = np.clip(arr, -1, 1).astype("float32")
    with rasterio.open(path, "w", driver="GTiff", height=height, width=width, count=1, dtype="float32",
                       crs=CRS_UTM22S, transform=transform, nodata=np.nan, compress="lzw") as dst:
        dst.write(arr, 1)
        dst.update_tags(SINTETICO="true", descricao="NDVI sintetico, nao e medicao")
    return str(path)
