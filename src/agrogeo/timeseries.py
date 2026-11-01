"""Séries temporais: lacunas, climatologia, anomalias e suavização."""
from __future__ import annotations

import numpy as np
import pandas as pd


def to_wide(ts: pd.DataFrame, value_col: str = "ndvi") -> pd.DataFrame:
    """Formato longo -> largo (index=date, colunas=talhao_id)."""
    return ts.pivot(index="date", columns="talhao_id", values=value_col).sort_index()


def monthly_composite(ts: pd.DataFrame, value_col: str = "ndvi", how: str = "median", min_obs: int = 1) -> pd.DataFrame:
    """Composição mensal por talhão. Meses com menos de `min_obs` observações viram NaN."""
    d = ts.dropna(subset=[value_col]).copy()
    d["mes"] = d["date"].dt.to_period("M").dt.to_timestamp()
    g = d.groupby(["talhao_id", "mes"])[value_col]
    out = pd.DataFrame({value_col: g.agg(how), "n_obs": g.size()}).reset_index()
    out.loc[out["n_obs"] < min_obs, value_col] = np.nan
    return out


def find_gaps(dates: pd.Series, values: pd.Series, min_days: int = 20) -> pd.DataFrame:
    """Lacunas: intervalos entre observações válidas consecutivas maiores que `min_days`."""
    valid = pd.Series(pd.to_datetime(dates)[~pd.isna(values).values]).sort_values().reset_index(drop=True)
    if len(valid) < 2:
        return pd.DataFrame(columns=["inicio", "fim", "dias"])
    delta = valid.diff().dt.days
    idx = delta[delta > min_days].index
    return pd.DataFrame({"inicio": valid[idx - 1].values, "fim": valid[idx].values, "dias": delta[idx].astype(int).values})


def gap_summary(ts: pd.DataFrame, value_col: str = "ndvi", min_days: int = 20) -> pd.DataFrame:
    rows = []
    for tid, g in ts.groupby("talhao_id"):
        gaps = find_gaps(g["date"], g[value_col], min_days)
        rows.append({"talhao_id": tid, "n_lacunas": len(gaps), "maior_lacuna_dias": int(gaps["dias"].max()) if len(gaps) else 0})
    return pd.DataFrame(rows)


def climatology(ts: pd.DataFrame, value_col: str = "ndvi", baseline: tuple[str, str] | None = None) -> pd.DataFrame:
    """Média e desvio por mês do ano e talhão (período-base opcional)."""
    d = ts.dropna(subset=[value_col]).copy()
    if baseline:
        d = d[(d["date"] >= baseline[0]) & (d["date"] <= baseline[1])]
    d["mes_ano"] = d["date"].dt.month
    return d.groupby(["talhao_id", "mes_ano"])[value_col].agg(clim_mean="mean", clim_std="std", n="count").reset_index()


def temporal_anomaly(ts: pd.DataFrame, value_col: str = "ndvi", baseline: tuple[str, str] | None = None) -> pd.DataFrame:
    """Anomalia temporal: valor − climatologia mensal do próprio talhão (e z-score)."""
    clim = climatology(ts, value_col, baseline)
    d = ts.copy()
    d["mes_ano"] = d["date"].dt.month
    d = d.merge(clim, on=["talhao_id", "mes_ano"], how="left")
    d["anom"] = d[value_col] - d["clim_mean"]
    d["z"] = d["anom"] / d["clim_std"].replace(0, np.nan)
    return d.drop(columns=["n"])


def relative_anomaly(ts: pd.DataFrame, value_col: str = "ndvi", window_days: int = 0,
                     baseline: tuple[str, str] | None = None) -> pd.DataFrame:
    """Anomalia RELATIVA: valor do talhão − mediana de todos os talhões na mesma data.

    Remove efeitos comuns (sazonalidade, atmosfera, clima). Resultado indica *diferença
    em relação aos vizinhos*, não dano absoluto. Com `window_days` > 0 aplica média móvel
    centrada (em nº de dias) sobre a anomalia para reduzir ruído. Com `baseline=(ini, fim)`
    subtrai antes a média de cada talhão nesse período, de modo que diferenças *permanentes*
    de nível (cultivar, idade, solo) não apareçam como anomalia: mede-se a *mudança*
    de cada talhão em relação à mudança típica do conjunto.
    """
    w = to_wide(ts, value_col)
    if baseline:
        w = w - w.loc[baseline[0]:baseline[1]].mean()
    ref = w.median(axis=1)
    rel = w.sub(ref, axis=0)
    if window_days > 0:
        rel = rel.rolling(f"{window_days}D", center=True, min_periods=1).mean()
    out = rel.reset_index().melt(id_vars="date", var_name="talhao_id", value_name="anom_rel")
    out["ref_mediana"] = out["date"].map(ref)
    return out


def robust_z(x: pd.Series) -> pd.Series:
    """z robusto: (x − mediana)/(1,4826·MAD)."""
    med = x.median()
    mad = (x - med).abs().median()
    return (x - med) / (1.4826 * mad) if mad and not np.isnan(mad) else x * np.nan


def flag_anomalies(rel: pd.DataFrame, z_thr: float = 3.0) -> pd.DataFrame:
    """Marca anomalias relativas com |z robusto| > z_thr (z calculado por talhão)."""
    r = rel.copy()
    r["z_rel"] = r.groupby("talhao_id")["anom_rel"].transform(robust_z)
    r["flag"] = r["z_rel"].abs() > z_thr
    return r


def interpolate_series(s: pd.Series, max_gap_days: int = 30) -> pd.Series:
    """Interpolação linear no tempo limitada: não preenche lacunas > `max_gap_days`."""
    s = s.sort_index()
    filled = s.interpolate(method="time", limit_area="inside")
    # reverte pontos dentro de lacunas longas
    valid_idx = s.dropna().index
    if len(valid_idx) < 2:
        return filled
    pos = valid_idx.searchsorted(filled.index)
    prev = valid_idx[np.clip(pos - 1, 0, len(valid_idx) - 1)]
    nxt = valid_idx[np.clip(pos, 0, len(valid_idx) - 1)]
    gap = (nxt - prev).days
    mask = s.isna() & (gap > max_gap_days)
    filled[mask] = np.nan
    return filled


def rolling_smooth(s: pd.Series, window: int = 5) -> pd.Series:
    """Média móvel centrada em nº de observações (ignora NaN)."""
    return s.rolling(window, center=True, min_periods=max(1, window // 2)).mean()
