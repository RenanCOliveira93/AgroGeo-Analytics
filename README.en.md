# AgroGeo Analytics

A **Geospatial Data Science** study applied to agriculture, focused on **coffee growing in Piraju, São Paulo (Brazil)**, adaptable to other crops and countries. Core deliverable: **six executable Jupyter notebooks**; documentation is in Brazilian Portuguese (`docs/pt-BR`). [Versão em português](README.md)

> **Data notice.** Field plots (*talhões*), the NDVI/NDRE time series and the sample raster are **SYNTHETIC** (fixed random seed; labelled in files, columns and plots). They exist so the code runs offline and for teaching — they are **not empirical results**. The Piraju municipal boundary (and neighbours) is **real** (IBGE). For real work, supply your own plot GeoJSON and use Earth Engine.
>
> **NDVI/NDRE do not diagnose diseases, pests or deficiencies.** They reflect spectral reflectance and only yield *hypotheses* to be checked in the field.

## Contents
| Notebook | Topic |
|---|---|
| [01_fundamentos_gis](notebooks/01_fundamentos_gis.ipynb) | CRS/EPSG, geometry, reprojection, area, buffers, intersections |
| [02_dados_satellite](notebooks/02_dados_satellite.ipynb) | Sentinel-2, SCL cloud mask, temporal composites, NDVI & NDRE, Earth Engine |
| [03_analise_talhoes](notebooks/03_analise_talhoes.ipynb) | zonal statistics, edge effects, plot comparison |
| [04_series_temporais](notebooks/04_series_temporais.ipynb) | gaps, seasonality, temporal and relative anomalies |
| [05_mapas_interativos](notebooks/05_mapas_interativos.ipynb) | folium maps, raster overlay, GeoJSON/HTML export |
| [06_insights_agricolas](notebooks/06_insights_agricolas.ipynb) | interpretation, limitations, agronomic hypotheses, MapBiomas |

```
src/agrogeo/     reusable functions (gis, indices, zonal, timeseries, maps, ee_utils, synthetic, config)
tests/           pytest (30 tests)
scripts/         IBGE download, sample-data generation, Earth Engine/MapBiomas export, notebook build/run
data/sample/     small data: IBGE boundaries (real) + plots/series/raster (synthetic)
docs/pt-BR/      study guide, GIS, remote sensing, indices, formulas, walkthrough, plot reading,
                 provenance, limitations, installation, worked exercises, deeper questions
outputs/         figures, HTML maps and GeoJSON produced by the notebooks
```

## Installation
Requires Python ≥ 3.10.
```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest -q
jupyter lab notebooks/                                   # or: python scripts/run_notebooks.py
```
Notebooks run **offline** on `data/sample/` by default.

## Earth Engine (optional, real data)
1. Register a Google Cloud project for Earth Engine ([earthengine.google.com](https://earthengine.google.com); check the non-commercial/commercial terms).
2. `cp .env.example .env`, then set `EE_PROJECT` and `AGROGEO_USE_EE=1`.
3. `earthengine authenticate`
4. `python scripts/export_s2_timeseries.py --talhoes YOURS.geojson --out data/processed/serie_s2.csv`
5. `python scripts/export_mapbiomas_stats.py --geojson YOURS.geojson --year 2023`

Your plot GeoJSON must be in EPSG:4326 with a unique `talhao_id` column. See [docs/pt-BR/09_instalacao_earth_engine.md](docs/pt-BR/09_instalacao_earth_engine.md) (Portuguese).

## Reproducing the sample data
```bash
python scripts/download_ibge.py --codigo 3538808 && python scripts/download_ibge.py --vizinhos
python scripts/generate_sample_data.py
python scripts/build_notebooks.py && python scripts/run_notebooks.py
```

## Sources (verified 2026-10-31)
- **Sentinel-2 SR Harmonized** — `COPERNICUS/S2_SR_HARMONIZED` (Earth Engine); Copernicus Sentinel Data Terms and Conditions apply.
- **MapBiomas Brazil** — `projects/mapbiomas-public/assets/brazil/lulc/v1` (30 m; CC-BY-4.0 per the Earth Engine catalog); class 46 = Coffee.
- **IBGE** — municipal boundaries (Malhas API v3). Piraju = 3538808.
- **Plots** — user-provided GeoJSON; otherwise synthetic, explicitly labelled.

## Verification status (in the development environment)
| Item | Status |
|---|---|
| `pytest` (30 tests) | **run, passing** |
| Notebooks 01–06 (offline mode) | **executed successfully** (outputs stored in the `.ipynb` files) |
| IBGE download | **run** |
| Earth Engine code (`ee_utils`, export scripts) | **NOT run** — no credentials; only `features_to_dataframe` is unit-tested. Written from the docs; may need adjustments |
| MapBiomas filter (`collection_id=10`, `version="v1"`) | **NOT run/confirmed** — verify the values in the asset |
| HTML maps | generated, **not opened in a browser** (tiles need internet) |

## Limitations (summary)
Pixel mixing (10/20 m), seasonality, clouds, perennial crops (continuous canopy, biennial bearing, pruning), autocorrelation, and no ground truth. See [docs/pt-BR/08_limitacoes.md](docs/pt-BR/08_limitacoes.md).

## Repository, versioning and running on another machine

Published from the original development machine (macOS, Podman). This has **not** been run on GitHub Codespaces or Docker Desktop; if you run it there, treat it as a first verification and compare with the tests section.

- **Not versioned:** `data/raw/` and `data/processed/` (IBGE downloads and derivatives). Recreate with the `scripts/download_ibge.py` and `scripts/generate_sample_data.py` commands in *Reprodução dos dados de exemplo* (internet required).
- **Versioned:** `src/`, `scripts/`, executed notebooks, tests, `docs/pt-BR/` and `data/sample/` (**synthetic** demo data; notebooks run offline with it).
- **Not executed in this delivery:** Earth Engine (needs account/credentials); see *Estado de verificação*.
- **Code licence:** GPL-3.0 (`LICENSE`). Third-party data/model licences and attributions: see the sections and docs above.
