import pandas as pd

from agrogeo import ee_utils, maps


def test_features_to_dataframe_handles_masked():
    info = {"features": [
        {"properties": {"talhao_id": "T01", "date": "2022-02-01", "ndvi": 0.7, "ndre": 0.4}},
        {"properties": {"talhao_id": "T01", "date": "2022-01-01", "ndvi": 0.6}},  # ndre mascarado
    ]}
    df = ee_utils.features_to_dataframe(info)
    assert list(df["date"]) == list(pd.to_datetime(["2022-01-01", "2022-02-01"]))
    assert pd.isna(df.loc[0, "ndre"])


def test_ee_importable_without_init():
    import ee  # noqa: F401  (apenas importa; sem rede/credenciais)


def test_choropleth_and_export(talhoes, tmp_path):
    t = talhoes.copy()
    t["ndvi_medio"] = range(len(t))
    m = maps.choropleth_talhoes(t, "ndvi_medio", title="teste")
    p = maps.export_html(m, tmp_path / "m.html")
    assert p.exists() and "leaflet" in p.read_text().lower()
    gj = maps.export_geojson(t, tmp_path / "t.geojson")
    assert gj.exists()
