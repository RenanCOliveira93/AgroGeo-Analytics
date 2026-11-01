"""Helpers para construir notebooks com nbformat."""
import nbformat as nbf

SETUP = '''import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from agrogeo import config, gis, indices, zonal, timeseries as ts_lib, maps
from agrogeo.config import DATA_SAMPLE, OUTPUTS, CRS_GEO, CRS_UTM22S

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .25,
                     "axes.spines.top": False, "axes.spines.right": False})
(OUTPUTS / "figures").mkdir(parents=True, exist_ok=True)
SYNTH_NOTE = "DADOS SINTÉTICOS — ilustrativo, não é medição"'''


class NB:
    def __init__(self):
        self.nb = nbf.v4.new_notebook()
        self.nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}

    def md(self, text):
        self.nb.cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))
        return self

    def code(self, text):
        self.nb.cells.append(nbf.v4.new_code_cell(text.strip("\n")))
        return self

    def save(self, path):
        nbf.write(self.nb, path)
