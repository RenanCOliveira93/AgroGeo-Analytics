"""Índices espectrais Sentinel-2 (NumPy, Earth Engine-agnóstico)."""
from __future__ import annotations

import numpy as np

from .config import S2_SCALE, SCL_VALID


def scale_reflectance(dn):
    """DN (inteiro) -> reflectância de superfície [0–1] (fator 1/10000)."""
    return np.asarray(dn, dtype="float64") / S2_SCALE


def normalized_difference(a, b):
    """(a − b)/(a + b). Retorna NaN onde a + b == 0 (evita divisão por zero)."""
    a = np.asarray(a, dtype="float64")
    b = np.asarray(b, dtype="float64")
    den = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(den == 0, np.nan, (a - b) / den)
    return out


def ndvi(nir, red):
    """NDVI = (NIR − RED)/(NIR + RED); Sentinel-2: B8 e B4."""
    return normalized_difference(nir, red)


def ndre(nir, red_edge):
    """NDRE = (NIR − RE)/(NIR + RE); Sentinel-2: B8 (ou B8A) e B5."""
    return normalized_difference(nir, red_edge)


def scl_valid_mask(scl, valid=SCL_VALID):
    """True onde a classe SCL é considerada observação utilizável."""
    return np.isin(np.asarray(scl), valid)


def mask_invalid(values, scl, valid=SCL_VALID):
    """Aplica NaN onde SCL indica nuvem/sombra/saturação/sem dado."""
    v = np.asarray(values, dtype="float64").copy()
    v[~scl_valid_mask(scl, valid)] = np.nan
    return v
