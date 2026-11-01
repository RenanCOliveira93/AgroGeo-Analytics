# Proveniência dos dados

Verificação feita em **2026-10-31** (catálogos e APIs consultados nessa data).

## Resumo
| Dado | Origem | Arquivo no projeto | Real/sintético | Licença/termos |
|---|---|---|---|---|
| Limite de Piraju e vizinhos | IBGE – API de Malhas v3 (qualidade intermediária) e API de Localidades | `data/sample/municipio_3538808.geojson`, `municipios_regiao_piraju.geojson` | **real** (simplificado) | dados públicos do IBGE; cite a fonte |
| Talhões | gerados por `agrogeo.synthetic.make_talhoes` (semente 42) | `data/sample/talhoes_sinteticos.geojson` | **SINTÉTICO** | n/a |
| Série NDVI/NDRE | `agrogeo.synthetic.make_timeseries` (semente 7) | `data/sample/serie_sintetica_ndvi_ndre.csv` | **SINTÉTICO** | n/a |
| Raster NDVI | `agrogeo.synthetic.make_ndvi_raster` (semente 11) | `data/sample/ndvi_sintetico.tif` | **SINTÉTICO** | n/a |
| Sentinel-2 | `COPERNICUS/S2_SR_HARMONIZED` no Earth Engine | não incluído (baixe com `scripts/export_s2_timeseries.py`) | real | Copernicus Sentinel Data Terms and Conditions (link no catálogo) |
| MapBiomas | `projects/mapbiomas-public/assets/brazil/lulc/v1` | não incluído (`scripts/export_mapbiomas_stats.py`) | real | CC-BY-4.0 (conforme catálogo) |

## IBGE
- Códigos conferidos na API de Localidades: Piraju **3538808**, Fartura 3515400, Sarutaiá 3551207, Tejupá 3554201, Timburi 3554607. (Atenção: 3539301 é *Pirassununga*; foi um erro evitado durante o desenvolvimento.)
- Área do município (Censo 2022, API de Agregados, tabela 4714, variável 6318): **504,591 km²**. A malha simplificada usada aqui, medida em EPSG:31982, dá 505,73 km² (+0,23%) — diferença atribuída à simplificação da geometria (não verificada por outros meios).
- Malhas: https://servicodados.ibge.gov.br/api/docs/malhas

## Sentinel-2 SR Harmonized
Conforme o catálogo do Earth Engine:
- Intervalo listado a partir de 2017-03-28; cobertura L2A de 2017–2018 não global.
- Revisita de 5 dias; bandas B4, B8 (10 m), B5, B8A, SCL (20 m); escala 0,0001.
- Cenas com baseline de processamento ≥ 04.00 têm DN deslocado em +1000; a coleção harmonizada o corrige.
- QA60 deixou de ser produzido em 2022-01-25 (reconstruído a partir de 2024-02-28) — por isso a máscara usa **SCL**, não QA60.
- Termos: Copernicus Sentinel Data Terms and Conditions. **Cite** "Contains modified Copernicus Sentinel data [ano]" em publicações.
- Uso do Earth Engine: sujeito aos termos do Google Earth Engine (uso não comercial gratuito vs. comercial pago — **verifique o seu enquadramento** em earthengine.google.com).

## MapBiomas Brasil
- Asset: `projects/mapbiomas-public/assets/brazil/lulc/v1` (ImageCollection; banda `classification`; propriedades `year`, `version`, `collection_id`). Disponibilidade 1985–2024 no momento da consulta.
- Resolução: 30 m. Licença CC-BY-4.0 (atribuição obrigatória).
- Classes úteis: 46 Café, 36 Lavoura perene, 47 Citrus, 15 Pastagem, 3 Formação florestal, 20 Cana, 39 Soja.
- Metodologia: Souza et al. (2020), *Remote Sensing* 12(17), 2735, DOI 10.3390/rs12172735.
- O filtro usado em `ee_utils.mapbiomas_image` (`collection_id=10`, `version="v1"`) segue o exemplo do catálogo; **a consulta feita não confirmou quais `collection_id` existem no asset** — confira antes de usar.
- **Não executado:** sem credenciais do Earth Engine no ambiente de desenvolvimento.

## Basemaps nos mapas HTML
OpenStreetMap (© contribuidores do OpenStreetMap, ODbL) e CARTO. Mantenha a atribuição exibida; verifique as políticas de uso de tiles em caso de uso intenso.

## Dados sintéticos: como foram feitos
- **Talhões:** 12 retângulos (220–360 m × 200–320 m), rotacionados ±12°, em grade 4×3 ancorada em um ponto interno de Piraju; atributos (cultivar, ano de plantio) sorteados.
- **Série:** 293 datas (passo de 5 dias, 2021-01-01 a 2024-12-31); nível-base por talhão 0,68–0,80; sazonalidade cossenoidal (amplitude 0,035; mínimo no meio do ano); ruído AR(1) (φ = 0,6, σ = 0,012) + ruído comum de cena (σ = 0,01); lacunas por nuvem com probabilidade 12–60% conforme o mês; NDRE = 0,62·NDVI − 0,04 + ruído; **eventos injetados**: T03 (queda de 0,18 decaindo com τ = 70 d desde 2023-08-10) e T08 (−0,07 constante desde 2023-03-01).
- **Raster:** entorno N(0,35; 0,04), talhões N(nível 0,66–0,80; 0,03), filtro 3×3 para mimetizar mistura de pixels.
- Reprodução: `python scripts/generate_sample_data.py`.

**Nenhum parâmetro acima foi calibrado com dados reais de café ou de Piraju.**
