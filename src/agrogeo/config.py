"""Configuração central: caminhos, CRS e constantes de fontes de dados."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DATA_SAMPLE = ROOT / "data" / "sample"
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

# CRS
CRS_GEO = "EPSG:4326"       # WGS 84 (lat/lon)
CRS_SIRGAS_GEO = "EPSG:4674"  # SIRGAS 2000 geográfico (oficial no Brasil)
CRS_UTM22S = "EPSG:31982"   # SIRGAS 2000 / UTM 22S (Piraju/SP, lon ~ -49,4)

# Fontes
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
S2_SCALE = 10_000.0
# Classes SCL descartadas: 0 sem dado, 1 saturado, 3 sombra, 8/9 nuvem, 10 cirrus, 11 neve
SCL_VALID = (2, 4, 5, 6, 7)
MAPBIOMAS_ASSET = "projects/mapbiomas-public/assets/brazil/lulc/v1"
MAPBIOMAS_CLASSES = {3: "Formação Florestal", 15: "Pastagem", 20: "Cana-de-açúcar",
                     36: "Lavoura Perene", 39: "Soja", 46: "Café", 47: "Citrus"}

MUNICIPIO_IBGE = int(os.getenv("MUNICIPIO_IBGE", "3538808"))
EE_PROJECT = os.getenv("EE_PROJECT", "")
USE_EE = os.getenv("AGROGEO_USE_EE", "0") == "1"
START_DATE = os.getenv("START_DATE", "2021-01-01")
END_DATE = os.getenv("END_DATE", "2024-12-31")
MAPBIOMAS_YEAR = int(os.getenv("MAPBIOMAS_YEAR", "2023"))
