import geopandas as gpd
import pytest
from shapely.geometry import box, Polygon

from agrogeo import gis


def test_utm_epsg_piraju():
    assert gis.utm_epsg_for(-49.4, -23.2) == 32722
    assert gis.utm_epsg_for(10.0, 50.0) == 32632


def test_area_ha_known_square():
    # quadrado 100 m x 100 m em UTM 22S = 1 ha
    g = gpd.GeoDataFrame(geometry=[box(500000, 7400000, 500100, 7400100)], crs="EPSG:31982")
    assert gis.area_ha(g).iloc[0] == pytest.approx(1.0, rel=1e-6)


def test_area_in_degrees_is_not_hectares(talhoes):
    wrong = talhoes.area.iloc[0]  # graus² — só para provar o erro conceitual
    right = gis.area_ha(talhoes).iloc[0]
    assert wrong < 1e-4 and right > 1


def test_area_same_across_input_crs(talhoes):
    a1 = gis.area_ha(talhoes)
    a2 = gis.area_ha(talhoes.to_crs("EPSG:31982"))
    assert (a1 - a2).abs().max() < 0.01


def test_buffer_m_grows_area():
    g = gpd.GeoDataFrame(geometry=[box(500000, 7400000, 500100, 7400100)], crs="EPSG:31982")
    b = gis.buffer_m(g, 10)
    assert b.crs == g.crs
    # 100x100 + 4*(100*10) + pi*10^2
    assert gis.area_ha(b).iloc[0] == pytest.approx((10_000 + 4_000 + 314.159) / 10_000, rel=1e-3)


def test_intersection_fraction_half():
    g = gpd.GeoDataFrame(geometry=[box(0, 0, 100, 100)], crs="EPSG:31982")
    f = gis.intersection_fraction(g, box(50, -10, 200, 110))
    assert f.iloc[0] == pytest.approx(0.5)


def test_talhoes_inside_municipio(talhoes, municipio):
    assert (gis.intersection_fraction(talhoes, municipio) > 0.999).all()


def test_validate_repairs_bowtie():
    bow = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    g = gpd.GeoDataFrame(geometry=[bow], crs="EPSG:31982")
    assert not g.geometry.is_valid.iloc[0]
    assert gis.validate_geometries(g).geometry.is_valid.all()


def test_compactness_square_vs_circle():
    sq = gpd.GeoDataFrame(geometry=[box(0, 0, 100, 100)], crs="EPSG:31982")
    assert gis.compactness(sq).iloc[0] == pytest.approx(3.14159 / 4, rel=1e-3)
