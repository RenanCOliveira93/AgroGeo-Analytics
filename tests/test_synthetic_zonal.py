import numpy as np
import pytest

from agrogeo.config import DATA_SAMPLE
from agrogeo import zonal
from agrogeo.synthetic import make_ndvi_raster, make_talhoes


def test_talhoes_marked_synthetic_and_reproducible(municipio, talhoes):
    assert talhoes["SINTETICO"].all() and len(talhoes) == 12
    again = make_talhoes(municipio)
    assert talhoes.geometry.geom_equals_exact(again.geometry, 1e-9).all()


def test_series_has_gaps_and_range(ts):
    assert ts["ndvi"].isna().mean() > 0.2
    assert ts["ndvi"].dropna().between(-1, 1).all()
    assert ts["SINTETICO"].all()


def test_raster_zonal(talhoes, tmp_path):
    p = make_ndvi_raster(talhoes, tmp_path / "r.tif")
    z = zonal.zonal_stats_raster(talhoes, p)
    assert len(z) == 12 and (z["n_pixels"] > 100).all()
    assert z["mean"].between(0.55, 0.9).all()


def test_sample_raster_matches_talhoes():
    import geopandas as gpd
    t = gpd.read_file(DATA_SAMPLE / "talhoes_sinteticos.geojson")
    z = zonal.zonal_stats_raster(t, DATA_SAMPLE / "ndvi_sintetico.tif")
    assert z["n_pixels"].min() > 0


def test_summary_and_rank(ts):
    s = zonal.summarize_by_talhao(ts)
    assert (s["n_validas"] <= s["n_total"]).all()
    r = zonal.rank_talhoes(s)
    assert r["rank"].tolist() == list(range(1, 13))
    assert r["media"].is_monotonic_decreasing


def test_compare_groups_keys(ts):
    out = zonal.compare_groups(ts)
    assert set(out) == {"H", "p_value", "n_groups"} and 0 <= out["p_value"] <= 1
