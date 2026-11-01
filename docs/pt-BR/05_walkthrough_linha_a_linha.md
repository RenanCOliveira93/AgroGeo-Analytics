# Walkthrough linha a linha

Anotações das funções centrais em `src/agrogeo/`. Leia com o código aberto.

## 1. `indices.normalized_difference`
```python
def normalized_difference(a, b):
    a = np.asarray(a, dtype="float64")      # (1)
    b = np.asarray(b, dtype="float64")
    den = a + b                              # (2)
    with np.errstate(divide="ignore", invalid="ignore"):   # (3)
        out = np.where(den == 0, np.nan, (a - b) / den)    # (4)
    return out
```
1. Converte para `float64`: DN inteiros dariam divisão inteira/overflow em alguns tipos.
2. Denominador calculado uma vez.
3. Silencia avisos de NumPy para divisão por zero — o tratamento é explícito na linha 4.
4. Onde a soma é zero o índice é indefinido → `NaN` (nunca 0, que seria um valor válido).

## 2. `indices.mask_invalid`
```python
v = np.asarray(values, dtype="float64").copy()   # copia: não altera o original
v[~scl_valid_mask(scl, valid)] = np.nan          # NaN onde a classe SCL não é válida
```
`scl_valid_mask` usa `np.isin(scl, valid)`; `valid` vem de `config.SCL_VALID = (2,4,5,6,7)`.

## 3. `gis.area_ha`
```python
crs = metric_crs or utm_crs_for_gdf(gdf)    # (1) CRS métrico informado ou estimado
return gdf.to_crs(crs).area / 10_000.0       # (2) m² → ha
```
1. `utm_crs_for_gdf` calcula o centróide em lon/lat e deriva o EPSG UTM WGS 84 (`utm_epsg_for`: zona = ⌊(lon+180)/6⌋+1; 327xx no hemisfério sul).
2. Reprojeta **antes** de medir.

## 4. `gis.buffer_m`
```python
out = gdf.copy()
out["geometry"] = gdf.to_crs(crs).buffer(dist_m).to_crs(gdf.crs)
```
Projeta → buffer em metros → volta ao CRS original (os dados continuam compatíveis com o restante do pipeline).

## 5. `gis.intersection_fraction`
```python
g = gdf.to_crs(crs).geometry
return g.intersection(mask_geom).area / g.area
```
A máscara também é projetada. Resultado ∈ [0, 1].

## 6. `zonal.zonal_stats_raster`
```python
with rasterio.open(raster_path) as src:
    g = gdf.to_crs(src.crs)                                   # (1) polígonos no CRS do raster
    for _, r in g.iterrows():
        data, _ = rio_mask(src, [r.geometry], crop=True, all_touched=all_touched,
                           filled=False, indexes=band)        # (2)
        v = np.ma.masked_invalid(data).compressed()           # (3)
```
1. Alinhar CRS é obrigatório: o `mask` compara coordenadas diretamente.
2. `crop=True` recorta à caixa do polígono; `filled=False` devolve array mascarado (pixels fora = máscara); `all_touched=False` considera só pixels cujo **centro** está dentro.
3. Remove NaN (nodata) e pixels fora → vetor 1D de valores válidos. Daí saem média, desvio (ddof = 1), percentis, CV.

## 7. `timeseries.relative_anomaly`
```python
w = to_wide(ts, value_col)                       # (1) matriz data × talhão
if baseline:
    w = w - w.loc[baseline[0]:baseline[1]].mean()   # (2) remove nível próprio de cada talhão
ref = w.median(axis=1)                           # (3) referência = mediana dos talhões por data
rel = w.sub(ref, axis=0)                         # (4) desvio de cada talhão em relação à referência
if window_days > 0:
    rel = rel.rolling(f"{window_days}D", center=True, min_periods=1).mean()  # (5)
```
1. `pivot` coloca cada talhão em uma coluna.
2. Sem essa linha, diferenças *permanentes* (cultivar, idade) aparecem como anomalia (descoberto durante os testes: sem baseline o talhão com evento injetado não era o mais negativo).
3. A mediana ignora NaN e resiste a outliers.
4. `sub(..., axis=0)` alinha por data.
5. Janela temporal centrada em dias (índice deve ser `DatetimeIndex`).

## 8. `timeseries.interpolate_series`
Interpola com `method="time"`, restrito ao interior da série (`limit_area="inside"`). Depois, para cada ponto ausente, acha a observação válida anterior e a seguinte (`searchsorted`) e **desfaz** o preenchimento se o intervalo entre elas > `max_gap_days`.

## 9. `ee_utils` (Earth Engine)
```python
def mask_scl(img, valid=SCL_VALID):
    scl = img.select("SCL")
    ok = ee.Image.constant(0)
    for v in valid:
        ok = ok.Or(scl.eq(v))     # OR de igualdades → máscara booleana
    return img.updateMask(ok)
```
```python
ndvi = img.normalizedDifference(["B8", "B4"]).rename("ndvi")   # (B8−B4)/(B8+B4)
```
`monthly_composites` gera, para cada mês, `median()` das imagens do mês. `zonal_timeseries` aplica `reduceRegions` com `Reducer.mean()` a 10 m (`tileScale=4` reduz risco de estouro de memória) e converte o resultado com `features_to_dataframe` (testado sem Earth Engine). Pixels mascarados em todo o talhão resultam em propriedade ausente → `NaN`.

> **Não verificado em execução real:** o ambiente de desenvolvimento não tinha credenciais do Earth Engine; essas funções foram escritas conforme a API e a documentação, e só `features_to_dataframe` foi testado automaticamente.

## 10. Sequência de um notebook típico
`config` (caminhos/CRS) → `gpd.read_file` → `gis.*` (validar/medir) → `zonal.*`/`timeseries.*` (estatísticas) → `maps.*` (visualização/exportação). Cada notebook começa com a célula de *setup* que importa estes módulos e define o estilo dos gráficos.
