"""Utilitários Google Earth Engine. `ee` é importado sob demanda (dependência opcional).

Estas funções exigem autenticação (`earthengine authenticate`) e um projeto Google Cloud
habilitado para Earth Engine. Sem credenciais, os notebooks usam dados sintéticos.
"""
from __future__ import annotations

import pandas as pd

from .config import EE_PROJECT, MAPBIOMAS_ASSET, S2_COLLECTION, SCL_VALID


def init_ee(project: str | None = None):
    """Inicializa o Earth Engine; se falhar, instrui a autenticar."""
    import ee
    project = project or EE_PROJECT or None
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)
    return ee


def gdf_to_fc(gdf, id_col: str = "talhao_id"):
    """GeoDataFrame (EPSG:4326) -> ee.FeatureCollection com a propriedade `id_col`."""
    import ee
    import json
    gj = json.loads(gdf.to_crs(4326)[[id_col, "geometry"]].to_json())
    return ee.FeatureCollection(gj["features"])


def mask_scl(img, valid=SCL_VALID):
    """Máscara por Scene Classification Layer (mantém classes `valid`)."""
    import ee
    scl = img.select("SCL")
    ok = ee.Image.constant(0)
    for v in valid:
        ok = ok.Or(scl.eq(v))
    return img.updateMask(ok)


def add_indices(img):
    """Adiciona NDVI (B8,B4) e NDRE (B8,B5) a uma imagem S2 SR já com máscara."""
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("ndvi")
    ndre = img.normalizedDifference(["B8", "B5"]).rename("ndre")
    return img.addBands([ndvi, ndre])


def s2_collection(aoi, start: str, end: str, max_cloud: float = 60):
    """COPERNICUS/S2_SR_HARMONIZED filtrada por área, datas e CLOUDY_PIXEL_PERCENTAGE."""
    import ee
    return (ee.ImageCollection(S2_COLLECTION).filterBounds(aoi).filterDate(start, end)
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", max_cloud))
            .map(mask_scl).map(add_indices))


def monthly_composites(col, start: str, end: str, bands=("ndvi", "ndre")):
    """Composição mensal por mediana (reduz ruído e nuvens residuais)."""
    import ee
    s, e = ee.Date(start), ee.Date(end)
    n = e.difference(s, "month").round()

    def _mk(i):
        a = s.advance(ee.Number(i), "month")
        img = col.filterDate(a, a.advance(1, "month")).select(list(bands)).median()
        return img.set({"system:time_start": a.millis(), "mes": a.format("YYYY-MM")})
    return ee.ImageCollection(ee.List.sequence(0, n.subtract(1)).map(_mk))


def zonal_timeseries(col, fc, scale: int = 10, id_col: str = "talhao_id", bands=("ndvi", "ndre")) -> pd.DataFrame:
    """Média por talhão e por imagem (reduceRegions). Para áreas grandes, use ee.batch.Export."""
    import ee

    def per_image(img):
        stats = img.select(list(bands)).reduceRegions(
            collection=fc, reducer=ee.Reducer.mean(), scale=scale, tileScale=4)
        return stats.map(lambda f: f.set("date", img.date().format("YYYY-MM-dd")))
    info = col.map(per_image).flatten().getInfo()
    return features_to_dataframe(info, id_col, bands)


def features_to_dataframe(info: dict, id_col: str = "talhao_id", bands=("ndvi", "ndre")) -> pd.DataFrame:
    """Converte o dict de FeatureCollection.getInfo() em DataFrame longo (testável sem EE)."""
    rows = []
    for f in info.get("features", []):
        p = f.get("properties", {})
        row = {"date": p.get("date"), id_col: p.get(id_col)}
        for b in bands:
            row[b] = p.get(b)  # ausente quando todos os pixels foram mascarados
        rows.append(row)
    df = pd.DataFrame(rows, columns=["date", id_col, *bands])
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values([id_col, "date"]).reset_index(drop=True)


def mapbiomas_image(year: int, collection_id: int = 10, version: str = "v1"):
    """Imagem de classificação MapBiomas Brasil para um ano.

    Filtra por `collection_id` e `version` (propriedades documentadas no catálogo do Earth Engine);
    confirme os valores disponíveis no asset antes de usar outra coleção.
    """
    import ee
    return (ee.ImageCollection(MAPBIOMAS_ASSET)
            .filter(ee.Filter.eq("collection_id", collection_id))
            .filter(ee.Filter.eq("version", version))
            .filter(ee.Filter.eq("year", year))
            .select("classification").mosaic())
