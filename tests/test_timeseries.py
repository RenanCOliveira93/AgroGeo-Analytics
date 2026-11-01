import numpy as np
import pandas as pd
import pytest

from agrogeo import timeseries as T


def _mini():
    d = pd.date_range("2022-01-01", periods=6, freq="10D")
    return d


def test_find_gaps():
    d = pd.Series(pd.date_range("2022-01-01", periods=6, freq="10D"))
    v = pd.Series([1, np.nan, np.nan, np.nan, 1, 1.0])
    g = T.find_gaps(d, v, min_days=20)
    assert len(g) == 1 and g["dias"].iloc[0] == 40


def test_monthly_composite_min_obs():
    d = pd.DataFrame({"date": pd.to_datetime(["2022-01-05", "2022-01-15", "2022-02-05"]),
                      "talhao_id": "A", "ndvi": [0.6, 0.8, 0.5]})
    m = T.monthly_composite(d, min_obs=2)
    assert m.loc[m.mes == "2022-01-01", "ndvi"].iloc[0] == pytest.approx(0.7)
    assert np.isnan(m.loc[m.mes == "2022-02-01", "ndvi"].iloc[0])


def test_relative_anomaly_removes_common_signal():
    d = pd.date_range("2022-01-01", periods=10, freq="5D")
    common = np.sin(np.arange(10))
    rows = []
    for t, off in [("A", 0.0), ("B", 0.0), ("C", -0.2)]:
        rows.append(pd.DataFrame({"date": d, "talhao_id": t, "ndvi": 0.7 + 0.1 * common + off}))
    rel = T.relative_anomaly(pd.concat(rows))
    assert rel[rel.talhao_id == "A"]["anom_rel"].abs().max() < 1e-12  # A coincide com a mediana
    assert rel[rel.talhao_id == "C"]["anom_rel"].mean() == pytest.approx(-0.2)


def test_temporal_anomaly_zero_mean_on_baseline(ts):
    a = T.temporal_anomaly(ts)
    per_month = a.dropna(subset=["anom"]).groupby(["talhao_id", "mes_ano"])["anom"].mean().abs()
    assert per_month.max() < 1e-9


def test_injected_events_detected(ts):
    """T08 (nível reduzido a partir de mar/2023) deve ficar abaixo dos pares após o evento."""
    rel = T.relative_anomaly(ts, window_days=30, baseline=("2021-01-01", "2022-12-31"))
    post = rel[rel.date >= "2023-04-01"].groupby("talhao_id")["anom_rel"].mean()
    assert post.idxmin() == "T08" and post["T08"] < -0.04


def test_flag_anomalies_columns(ts):
    f = T.flag_anomalies(T.relative_anomaly(ts, window_days=15))
    assert {"z_rel", "flag"} <= set(f.columns)


def test_interpolate_respects_max_gap():
    idx = pd.date_range("2022-01-01", periods=12, freq="10D")
    s = pd.Series([1.0] + [np.nan] * 2 + [4.0] + [np.nan] * 6 + [10.0, 11.0], index=idx)
    f = T.interpolate_series(s, max_gap_days=30)
    assert f.iloc[1] == pytest.approx(2.0)          # lacuna de 30 d → preenche
    assert f.iloc[4:10].isna().all()                # lacuna de 70 d → mantém NaN
