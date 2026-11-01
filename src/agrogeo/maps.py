"""Mapas interativos (folium) e exportações."""
from __future__ import annotations

from pathlib import Path

import folium
import geopandas as gpd
import matplotlib
import matplotlib.colors as mcolors


def _color_scale(values, vmin, vmax, cmap="RdYlGn"):
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax, clip=True)
    cm = matplotlib.colormaps[cmap]
    return lambda v: mcolors.to_hex(cm(norm(v))) if v == v else "#999999"


def choropleth_talhoes(talhoes: gpd.GeoDataFrame, value_col: str, municipio: gpd.GeoDataFrame | None = None,
                       title: str | None = None, cmap: str = "RdYlGn", tooltip_cols: list[str] | None = None,
                       vmin: float | None = None, vmax: float | None = None) -> folium.Map:
    """Mapa folium com talhões coloridos por `value_col`, limite municipal e controle de camadas."""
    g = talhoes.to_crs(4326)
    c = g.union_all().centroid
    m = folium.Map(location=[c.y, c.x], zoom_start=13, tiles=None, control_scale=True)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB positron", name="CartoDB Positron", show=False).add_to(m)
    if municipio is not None:
        folium.GeoJson(municipio.to_crs(4326), name="Município (IBGE)",
                       style_function=lambda f: {"color": "#444", "weight": 2, "fill": False, "dashArray": "6"}).add_to(m)
    vmin = g[value_col].min() if vmin is None else vmin
    vmax = g[value_col].max() if vmax is None else vmax
    colorf = _color_scale(None, vmin, vmax, cmap)
    cols = tooltip_cols or [c_ for c_ in ["talhao_id", "cultivar", value_col] if c_ in g.columns]
    folium.GeoJson(
        g, name=f"Talhões ({value_col})",
        style_function=lambda f: {"fillColor": colorf(f["properties"][value_col]), "color": "#222",
                                  "weight": 1, "fillOpacity": 0.75},
        tooltip=folium.GeoJsonTooltip(fields=cols, aliases=cols, localize=True),
    ).add_to(m)
    cmobj = matplotlib.colormaps[cmap]
    stops = ", ".join(mcolors.to_hex(cmobj(i / 4)) for i in range(5))
    legend = (f'<div style="position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:8px 10px;'
              f'border:1px solid #888;font:12px sans-serif"><b>{title or value_col}</b><br>'
              f'<div style="width:160px;height:10px;background:linear-gradient(to right,{stops})"></div>'
              f'<div style="display:flex;justify-content:space-between"><span>{vmin:.2f}</span><span>{vmax:.2f}</span></div></div>')
    m.get_root().html.add_child(folium.Element(legend))
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def export_geojson(gdf: gpd.GeoDataFrame, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_crs(4326).to_file(path, driver="GeoJSON")
    return path


def export_html(m: folium.Map, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(path))
    return path
