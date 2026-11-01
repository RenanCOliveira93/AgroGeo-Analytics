"""Gera os 6 notebooks em notebooks/. Uso: python scripts/build_notebooks.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbdefs import nb01, nb02, nb03, nb04, nb05, nb06  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "notebooks"
NAMES = {
    "01_fundamentos_gis": nb01, "02_dados_satellite": nb02, "03_analise_talhoes": nb03,
    "04_series_temporais": nb04, "05_mapas_interativos": nb05, "06_insights_agricolas": nb06,
}
OUT.mkdir(exist_ok=True)
for name, mod in NAMES.items():
    mod.build().save(OUT / f"{name}.ipynb")
    print("gerado", name)
