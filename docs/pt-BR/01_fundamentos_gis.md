# Fundamentos de GIS

## 1. Dados vetoriais e raster
- **Vetor**: pontos, linhas e polígonos com atributos (talhões, municípios). Formatos: GeoJSON, Shapefile, GeoPackage.
- **Raster**: grade de pixels com valores (imagens de satélite, NDVI). Formato típico: GeoTIFF.

## 2. CRS, datum e projeção
Um **CRS** liga coordenadas a posições na Terra. Tem dois componentes:
- **datum** (modelo de elipsoide/origem; ex.: WGS 84, SIRGAS 2000);
- **projeção** (como a superfície curva vira plano), ou nenhuma (CRS geográfico, em graus).

| EPSG | Tipo | Unidade | Nota |
|---|---|---|---|
| 4326 | geográfico | graus | padrão de GeoJSON, GPS, Earth Engine |
| 4674 | geográfico | graus | SIRGAS 2000, datum oficial do Brasil |
| 31982 | projetado (UTM 22S) | metros | adequado a Piraju (lon ≈ −49,4°; zona 22 cobre −54° a −48°) |
| 5880 | projetado (Polyconic) | metros | projeção para o Brasil inteiro |
| 3857 | projetado (Web Mercator) | metros | só visualização web; distorce área |

WGS 84 e SIRGAS 2000 diferem pouco na prática (sub-métrico); para este projeto são intercambiáveis, mas em levantamentos oficiais use SIRGAS 2000.

### Por que graus não servem para medir
1° de latitude ≈ 111 km, mas 1° de longitude vale 111·cos(φ) km. Em Piraju (φ ≈ 23,2°), ≈ 102 km. `.area` em EPSG:4326 devolve graus², sem significado em hectares.

### Distorção do Web Mercator
A escala linear cresce com 1/cos φ; a de área, com 1/cos²φ. Em Piraju: 1/cos²(23,2°) − 1 ≈ **18,3%** (valor medido sobre os talhões sintéticos: ≈ 18,9%; diferenças de décimos de ponto percentual são esperadas pela latitude exata dos talhões e porque a referência UTM também carrega pequena distorção).

## 3. Geometria
- `Polygon` tem anel externo e (opcional) furos.
- **Validade**: auto-interseções tornam o polígono inválido; `make_valid` repara.
- **Área em ha** = área(m²) / 10 000.
- **Compacidade (Polsby–Popper)**: 4πA/P²; 1 = círculo; quadrados dão π/4 ≈ 0,785.

## 4. Operações essenciais
| Operação | Pergunta | Função do projeto |
|---|---|---|
| Reprojeção | "Em que CRS meço?" | `GeoDataFrame.to_crs` |
| Buffer | "O que está a d metros?" | `gis.buffer_m` (projeta → buffer → volta) |
| Buffer negativo | "Qual o interior a ≥ d m da borda?" | `gis.buffer_m(g, -10)` |
| Interseção | "Quanto está dentro de X?" | `gis.intersection_fraction`, `gis.overlay_area_ha` |
| Junção espacial | "Em qual município cai?" | `geopandas.sjoin` |

## 5. Raster e geotransformação
Um raster tem CRS, **resolução** (10 m no Sentinel-2 para B4/B8) e uma **transformação afim** que mapeia (linha, coluna) → (x, y). `rasterio.mask` usa a geometria para selecionar pixels (por padrão, cujo centro está dentro do polígono).

## 6. Erros comuns
1. Calcular área/distância em graus.
2. Misturar CRS sem reprojetar (camadas "não se encontram").
3. Esquecer que `buffer` em graus gera elipses distorcidas.
4. Não validar geometrias desenhadas à mão.
5. Assumir CRS ausente sem avisar (`gis.ensure_crs` avisa).

## Leituras
- Documentação do GeoPandas e do Rasterio.
- Registro EPSG: epsg.org.
