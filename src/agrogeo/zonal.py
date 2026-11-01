"""Estatísticas zonais por talhão (raster local ou tabelas)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rio_mask
from scipy import stats


def zonal_stats_raster(gdf: gpd.GeoDataFrame, raster_path, id_col: str = "talhao_id",
                       band: int = 1, all_touched: bool = False) -> pd.DataFrame:
    """Média, desvio, mín, máx, mediana, P10/P90 e nº de pixels válidos por polígono."""
    rows = []
    with rasterio.open(raster_path) as src:
        g = gdf.to_crs(src.crs)
        for _, r in g.iterrows():
            data, _ = rio_mask(src, [r.geometry], crop=True, all_touched=all_touched,
                               filled=False, indexes=band)
            v = np.ma.masked_invalid(data).compressed()
            if v.size == 0:
                rows.append({id_col: r[id_col], "n_pixels": 0})
                continue
            rows.append({
                id_col: r[id_col], "n_pixels": int(v.size), "mean": v.mean(), "std": v.std(ddof=1) if v.size > 1 else np.nan,
                "min": v.min(), "p10": np.percentile(v, 10), "median": np.median(v),
                "p90": np.percentile(v, 90), "max": v.max(),
            })
    out = pd.DataFrame(rows)
    out["cv"] = out["std"] / out["mean"]
    return out


def summarize_by_talhao(ts: pd.DataFrame, value_col: str = "ndvi", id_col: str = "talhao_id") -> pd.DataFrame:
    """Resumo de uma série longa por talhão: n obs, % lacunas, média, desvio, CV, P10/P90."""
    g = ts.groupby(id_col)[value_col]
    out = pd.DataFrame({
        "n_total": g.size(), "n_validas": g.count(),
        "pct_lacuna": 100 * (1 - g.count() / g.size()),
        "media": g.mean(), "desvio": g.std(), "mediana": g.median(),
        "p10": g.quantile(.10), "p90": g.quantile(.90),
    })
    out["cv"] = out["desvio"] / out["media"]
    return out.reset_index()


def compare_groups(ts: pd.DataFrame, value_col: str = "ndvi", id_col: str = "talhao_id") -> dict:
    """Kruskal-Wallis entre talhões (não paramétrico). Observações de datas repetidas NÃO são
    independentes (autocorrelação temporal); use p-valor apenas como indicador exploratório."""
    groups = [g[value_col].dropna().values for _, g in ts.groupby(id_col)]
    groups = [g for g in groups if len(g) > 1]
    h, p = stats.kruskal(*groups)
    return {"H": float(h), "p_value": float(p), "n_groups": len(groups)}


def rank_talhoes(summary: pd.DataFrame, col: str = "media") -> pd.DataFrame:
    s = summary.sort_values(col, ascending=False).reset_index(drop=True)
    s["rank"] = np.arange(1, len(s) + 1)
    return s
