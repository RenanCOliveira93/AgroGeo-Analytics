import numpy as np
import pytest

from agrogeo import indices as ix


def test_ndvi_known_value():
    assert ix.ndvi(0.5, 0.1) == pytest.approx(0.4 / 0.6)


def test_ndvi_range_and_zero_division():
    r = ix.ndvi(np.array([0.0, 0.3, 0.9]), np.array([0.0, 0.3, 0.0]))
    assert np.isnan(r[0]) and r[1] == 0 and r[2] == 1


def test_scale():
    assert ix.scale_reflectance(5000) == 0.5


def test_ndre_formula():
    assert ix.ndre(0.4, 0.2) == pytest.approx(0.2 / 0.6)


def test_scl_mask():
    v = ix.mask_invalid([0.7, 0.7, 0.7, 0.7], [4, 9, 3, 5])
    assert np.isnan(v[1]) and np.isnan(v[2]) and v[0] == 0.7 and v[3] == 0.7
