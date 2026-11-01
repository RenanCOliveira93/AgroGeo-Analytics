import geopandas as gpd
import pytest

from agrogeo.config import DATA_SAMPLE
from agrogeo.synthetic import make_talhoes, make_timeseries


@pytest.fixture(scope="session")
def municipio():
    return gpd.read_file(DATA_SAMPLE / "municipio_3538808.geojson")


@pytest.fixture(scope="session")
def talhoes(municipio):
    return make_talhoes(municipio)


@pytest.fixture(scope="session")
def ts(talhoes):
    return make_timeseries(talhoes, "2021-01-01", "2023-12-31")
