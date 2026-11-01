"""Fundamentos GIS: CRS, reprojeção, área, buffers e interseções."""
from __future__ import annotations

import math

import geopandas as gpd
from shapely.geometry.base import BaseGeometry

from .config import CRS_GEO


def utm_epsg_for(lon: float, lat: float) -> int:
    """EPSG WGS84/UTM para um ponto (326xx norte, 327xx sul)."""
    zone = int((lon + 180) // 6) + 1
    return (32600 if lat >= 0 else 32700) + zone


def utm_crs_for_gdf(gdf: gpd.GeoDataFrame) -> str:
    """Estima o CRS UTM (WGS84) adequado ao centróide do conjunto."""
    c = gdf.to_crs(CRS_GEO).union_all().centroid
    return f"EPSG:{utm_epsg_for(c.x, c.y)}"


def ensure_crs(gdf: gpd.GeoDataFrame, default: str = CRS_GEO) -> gpd.GeoDataFrame:
    """Garante que o GeoDataFrame tenha CRS (assume `default` se ausente, com aviso)."""
    if gdf.crs is None:
        print(f"AVISO: CRS ausente; assumindo {default}.")
        return gdf.set_crs(default)
    return gdf


def validate_geometries(gdf: gpd.GeoDataFrame, repair: bool = True) -> gpd.GeoDataFrame:
    """Remove vazios e (opcionalmente) repara geometrias inválidas com make_valid."""
    out = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()].copy()
    if repair:
        invalid = ~out.geometry.is_valid
        if invalid.any():
            out.loc[invalid, "geometry"] = out.loc[invalid, "geometry"].make_valid()
    return out


def area_ha(gdf: gpd.GeoDataFrame, metric_crs: str | None = None) -> gpd.GeoSeries:
    """Área em hectares calculada em CRS métrico (nunca em graus)."""
    crs = metric_crs or utm_crs_for_gdf(gdf)
    return gdf.to_crs(crs).area / 10_000.0


def perimeter_m(gdf: gpd.GeoDataFrame, metric_crs: str | None = None) -> gpd.GeoSeries:
    crs = metric_crs or utm_crs_for_gdf(gdf)
    return gdf.to_crs(crs).length


def compactness(gdf: gpd.GeoDataFrame, metric_crs: str | None = None) -> gpd.GeoSeries:
    """Índice de Polsby-Popper 4πA/P² (1 = círculo). Útil para forma de talhões."""
    m = gdf.to_crs(metric_crs or utm_crs_for_gdf(gdf))
    return 4 * math.pi * m.area / (m.length ** 2)


def buffer_m(gdf: gpd.GeoDataFrame, dist_m: float, metric_crs: str | None = None) -> gpd.GeoDataFrame:
    """Buffer em metros: projeta, aplica buffer e devolve no CRS original."""
    crs = metric_crs or utm_crs_for_gdf(gdf)
    out = gdf.copy()
    out["geometry"] = gdf.to_crs(crs).buffer(dist_m).to_crs(gdf.crs)
    return out


def intersection_fraction(gdf: gpd.GeoDataFrame, mask: BaseGeometry | gpd.GeoDataFrame,
                          metric_crs: str | None = None) -> gpd.GeoSeries:
    """Fração (0–1) da área de cada feição contida em `mask` (ex.: município)."""
    crs = metric_crs or utm_crs_for_gdf(gdf)
    if isinstance(mask, gpd.GeoDataFrame):
        mask_geom = mask.to_crs(crs).union_all()
    else:
        mask_geom = gpd.GeoSeries([mask], crs=gdf.crs).to_crs(crs).iloc[0]
    g = gdf.to_crs(crs).geometry
    return g.intersection(mask_geom).area / g.area


def overlay_area_ha(a: gpd.GeoDataFrame, b: gpd.GeoDataFrame, metric_crs: str | None = None) -> gpd.GeoDataFrame:
    """Interseção (overlay) entre camadas com área em ha da peça resultante."""
    crs = metric_crs or utm_crs_for_gdf(a)
    res = gpd.overlay(a.to_crs(crs), b.to_crs(crs), how="intersection", keep_geom_type=True)
    res["area_ha"] = res.area / 10_000.0
    return res
