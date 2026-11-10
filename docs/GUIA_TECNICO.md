# AgroGeo Analytics: Guia técnico

Documentação de engenharia do projeto: arquitetura, dados, instalação, execução, metodologia, testes, limitações e licenças.

## Sumário

1. [Escopo e avisos](#1-escopo-e-avisos)
2. [Arquitetura](#2-arquitetura)
3. [Fontes de dados e proveniência](#3-fontes-de-dados-e-proveniência)
4. [Instalação](#4-instalação)
5. [Execução e reprodução](#5-execução-e-reprodução)
6. [Metodologia e pipeline](#6-metodologia-e-pipeline)
7. [Testes e validação](#7-testes-e-validação)
8. [Limitações conhecidas](#8-limitações-conhecidas)
9. [Licenças e atribuições](#9-licenças-e-atribuições)
10. [Solução de problemas](#10-solução-de-problemas)

---

## 1. Escopo e avisos

O projeto implementa um fluxo de ciência de dados geoespacial para agricultura, aplicado à cafeicultura em Piraju/SP: operações GIS sobre talhões, índices espectrais (NDVI, NDRE) a partir do Sentinel-2, estatísticas zonais, séries temporais com detecção de anomalias e mapas interativos.

- **Dados sintéticos.** Talhões, série NDVI/NDRE e raster em `data/sample/` são **sintéticos** (semente fixa, marcados com a coluna/atributo `SINTETICO`). Servem para execução offline e testes; **não são resultados empíricos**. Apenas o limite municipal de Piraju e vizinhos (IBGE) é real.
- **NDVI/NDRE não diagnosticam doenças, pragas ou deficiências nutricionais.** Indicam reflectância e geram hipóteses a verificar em campo. Não medem produtividade.
- Sem verdade de campo, o projeto não valida hipóteses agronômicas. Para decisões de manejo, envolva um engenheiro agrônomo.

## 2. Arquitetura

```
data/sample/ ──► src/agrogeo/ ──► notebooks/ (01..06) ──► outputs/ (figuras, mapas HTML, GeoJSON)
                    ▲
scripts/ ───────────┘   (download IBGE, geração de dados sintéticos, export Earth Engine/MapBiomas,
                         build/execução dos notebooks)
```

| Módulo (`src/agrogeo/`) | Responsabilidade |
|---|---|
| `config.py` | caminhos, CRS, constantes de fontes (coleção S2, escala, `SCL_VALID`, asset MapBiomas), variáveis de ambiente |
| `gis.py` | CRS UTM automático, validação de geometrias, área (ha), perímetro, compacidade, buffer em metros, fração de interseção |
| `indices.py` | reflectância, diferença normalizada, NDVI, NDRE, máscara SCL |
| `zonal.py` | estatísticas zonais sobre raster, resumo por talhão, comparação entre grupos, ranking |
| `timeseries.py` | formato largo, composição mensal, lacunas, climatologia, anomalia temporal e relativa, z-score robusto, flags, interpolação limitada, suavização |
| `maps.py` | mapas coropléticos folium, exportação GeoJSON/HTML |
| `ee_utils.py` | integração opcional com Earth Engine (máscara SCL, índices, composições, séries zonais, MapBiomas) |
| `synthetic.py` | geração dos talhões, série e raster sintéticos |

Estrutura de diretórios:

```
src/agrogeo/     pacote Python
tests/           pytest (30 testes)
scripts/         utilitários de linha de comando; scripts/nbdefs/ define o conteúdo dos notebooks
notebooks/       6 notebooks executados (saídas gravadas)
data/sample/     dados pequenos versionados
outputs/         figuras (outputs/figures), mapas HTML e GeoJSON gerados pelos notebooks
docs/            este guia e os cartões de dados/modelo, quando aplicáveis
```

`data/raw/` e `data/processed/` não são versionados (ver `.gitignore`).

## 3. Fontes de dados e proveniência

Catálogos e APIs consultados em 2026-10-31.

| Dado | Origem | Arquivo | Real/sintético | Licença/termos |
|---|---|---|---|---|
| Limite de Piraju e vizinhos | IBGE, API de Malhas v3 (qualidade intermediária) e API de Localidades | `data/sample/municipio_3538808.geojson`, `municipios_regiao_piraju.geojson` | real (simplificado) | dados públicos do IBGE; citar a fonte |
| Talhões | `agrogeo.synthetic.make_talhoes` (semente 42) | `data/sample/talhoes_sinteticos.geojson` | **sintético** | n/a |
| Série NDVI/NDRE | `agrogeo.synthetic.make_timeseries` (semente 7) | `data/sample/serie_sintetica_ndvi_ndre.csv` | **sintético** | n/a |
| Raster NDVI | `agrogeo.synthetic.make_ndvi_raster` (semente 11) | `data/sample/ndvi_sintetico.tif` | **sintético** | n/a |
| Sentinel-2 | `COPERNICUS/S2_SR_HARMONIZED` (Earth Engine) | não incluído (`scripts/export_s2_timeseries.py`) | real | Copernicus Sentinel Data Terms and Conditions |
| MapBiomas | `projects/mapbiomas-public/assets/brazil/lulc/v1` | não incluído (`scripts/export_mapbiomas_stats.py`) | real | CC-BY-4.0 (conforme catálogo) |

### 3.1 IBGE
- Códigos conferidos na API de Localidades: Piraju 3538808, Fartura 3515400, Sarutaiá 3551207, Tejupá 3554201, Timburi 3554607. O código 3539301 corresponde a Pirassununga, não a Piraju.
- Área do município (Censo 2022, API de Agregados, tabela 4714, variável 6318): 504,591 km². A malha simplificada, medida em EPSG:31982, resulta em 505,73 km² (+0,23%); a diferença é atribuída à simplificação da geometria (não verificada por outros meios).
- Malhas: https://servicodados.ibge.gov.br/api/docs/malhas

### 3.2 Sentinel-2 SR Harmonized
Conforme o catálogo do Earth Engine:
- Cobertura listada a partir de 2017-03-28; a cobertura L2A de 2017-2018 não é global.
- Revisita de 5 dias; bandas B4 e B8 a 10 m; B5, B8A e SCL a 20 m; reflectância = DN / 10 000.
- Cenas com baseline de processamento >= 04.00 (a partir de 2022-01-25) têm DN deslocado em +1000; a coleção HARMONIZED corrige o deslocamento. Use-a em séries que cruzam 2022.
- QA60 deixou de ser produzido em 2022-01-25 (reconstruído a partir de 2024-02-28); por isso a máscara de nuvens usa **SCL**.
- Citação recomendada em publicações: "Contains modified Copernicus Sentinel data [ano]".
- O uso do Earth Engine está sujeito aos termos do Google (uso não comercial gratuito, uso comercial pago); verifique o enquadramento em earthengine.google.com.

Classes SCL e tratamento (`config.SCL_VALID = (2, 4, 5, 6, 7)`):

| Valor | Classe | Tratamento |
|---|---|---|
| 0 | sem dado | descarta |
| 1 | saturado/defeituoso | descarta |
| 2 | área escura | mantém |
| 3 | sombra de nuvem | descarta |
| 4 | vegetação | mantém |
| 5 | solo exposto | mantém |
| 6 | água | mantém |
| 7 | nuvem de baixa probabilidade / não classificado | mantém |
| 8 | nuvem, probabilidade média | descarta |
| 9 | nuvem, probabilidade alta | descarta |
| 10 | cirrus | descarta |
| 11 | neve/gelo | descarta |

A manutenção das classes 2 e 7 é uma escolha de projeto e um ponto de ajuste; a classe 7 pode conter nuvem fina residual, mitigada pela composição por mediana.

### 3.3 MapBiomas Brasil
- Asset: `projects/mapbiomas-public/assets/brazil/lulc/v1` (ImageCollection; banda `classification`; propriedades `year`, `version`, `collection_id`). Disponibilidade 1985-2024 na data da consulta.
- Resolução 30 m; licença CC-BY-4.0 (atribuição obrigatória).
- Classes usadas (`config.MAPBIOMAS_CLASSES`): 46 Café, 36 Lavoura perene, 47 Citrus, 15 Pastagem, 3 Formação florestal, 20 Cana-de-açúcar, 39 Soja.
- Metodologia: Souza et al. (2020), *Remote Sensing* 12(17), 2735, DOI 10.3390/rs12172735.
- O filtro de `ee_utils.mapbiomas_image` (`collection_id=10`, `version="v1"`) segue o exemplo do catálogo; **os valores de `collection_id` existentes no asset não foram confirmados**. Confira antes de usar.

### 3.4 Basemaps dos mapas HTML
OpenStreetMap (ODbL, atribuição aos contribuidores) e CARTO. Mantenha a atribuição exibida e verifique as políticas de uso de tiles em caso de uso intenso.

### 3.5 Geração dos dados sintéticos
- **Talhões:** 12 retângulos (220-360 m x 200-320 m), rotacionados +/-12 graus, em grade 4x3 ancorada em um ponto interno de Piraju; cultivar e ano de plantio sorteados.
- **Série:** 293 datas (passo de 5 dias, 2021-01-01 a 2024-12-31); nível-base por talhão de 0,68 a 0,80; sazonalidade cossenoidal (amplitude 0,035; mínimo no meio do ano); ruído AR(1) (phi = 0,6, sigma = 0,012) mais ruído comum de cena (sigma = 0,01); lacunas por nuvem com probabilidade de 12 a 60% conforme o mês; NDRE = 0,62 x NDVI - 0,04 + ruído. **Eventos injetados:** T03 (queda de 0,18 com decaimento tau = 70 d desde 2023-08-10) e T08 (redução constante de 0,07 desde 2023-03-01).
- **Raster:** entorno N(0,35; 0,04), talhões N(nível 0,66-0,80; 0,03), filtro 3x3 para mimetizar mistura de pixels.
- Reprodução: `python scripts/generate_sample_data.py`.

Nenhum parâmetro acima foi calibrado com dados reais de café ou de Piraju.

## 4. Instalação

Requer Python >= 3.10 (desenvolvido em 3.11, macOS). GeoPandas, Rasterio e Shapely possuem wheels binárias para as plataformas comuns; sem wheel, instale GDAL/GEOS/PROJ pelo gerenciador de pacotes ou use `conda`.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                     # instala o pacote agrogeo (src/)
```

Dependências opcionais declaradas em `pyproject.toml`: extra `ee` (`earthengine-api`, `geemap`) e extra `dev` (`pytest`, `nbformat`, `nbclient`, `ipykernel`).

### 4.1 Earth Engine (opcional)
Os notebooks rodam offline por padrão; o Earth Engine só é necessário para dados reais.

1. Registre um projeto Google Cloud para uso do Earth Engine (https://earthengine.google.com) e confira a elegibilidade de uso.
2. `cp .env.example .env` e preencha `EE_PROJECT=<seu-projeto>` e `AGROGEO_USE_EE=1`.
3. Autentique: `earthengine authenticate`. Alternativa: `import ee; ee.Authenticate(); ee.Initialize(project="seu-projeto")`. Sem navegador, use `earthengine authenticate --auth_mode=notebook` ou uma conta de serviço.
4. Teste: `python -c "from agrogeo.ee_utils import init_ee; ee=init_ee(); print(ee.Number(1).add(1).getInfo())"` deve imprimir `2`.

Variáveis do `.env` (ver `.env.example`): `EE_PROJECT`, `AGROGEO_USE_EE` (0 = dados sintéticos offline), `MUNICIPIO_IBGE` (3538808), `START_DATE`, `END_DATE`, `MAPBIOMAS_YEAR`. Nunca versione `.env` nem credenciais (ignorados pelo `.gitignore`).

## 5. Execução e reprodução

```bash
pytest -q                                    # testes
jupyter lab notebooks/                       # uso interativo
python scripts/run_notebooks.py              # executa todos os notebooks e grava as saídas
```

Reprodução completa:

```bash
# (a) dados de exemplo (já incluídos; para regenerar)
python scripts/download_ibge.py --codigo 3538808
python scripts/download_ibge.py --vizinhos
python scripts/generate_sample_data.py

# (b) notebooks (reconstruir a partir de scripts/nbdefs e executar)
python scripts/build_notebooks.py
python scripts/run_notebooks.py

# (c) dados reais (requer Earth Engine)
python scripts/export_s2_timeseries.py --talhoes SEU_ARQUIVO.geojson --out data/processed/serie_s2.csv
python scripts/export_mapbiomas_stats.py --geojson SEU_ARQUIVO.geojson --year 2023
```

Opções dos scripts: `download_ibge.py` (`--codigo`, `--vizinhos`); `export_s2_timeseries.py` (`--talhoes` obrigatório, `--start`, `--end`, `--max-cloud`, `--out`); `export_mapbiomas_stats.py` (`--geojson` obrigatório, `--id-col`, `--year`, `--out`). O download do IBGE exige internet.

O GeoJSON de talhões deve estar em EPSG:4326 e conter a coluna `talhao_id` (única por talhão).

Para que os notebooks 03-06 usem a série real, ajuste a leitura do CSV (`data/processed/serie_s2.csv`) na célula de carregamento, mantendo as colunas `date, talhao_id, ndvi, ndre`. A série do Earth Engine é **mensal** (composição por mediana), não de 5 dias; ajuste `window_days`, `min_obs` e `step` nas funções.

### 5.1 Notebooks

| Notebook | Conteúdo |
|---|---|
| `01_fundamentos_gis` | CRS/EPSG, geometria, reprojeção, área, buffers, interseções |
| `02_dados_satellite` | Sentinel-2, máscara SCL, composições temporais, NDVI e NDRE, Earth Engine |
| `03_analise_talhoes` | estatísticas zonais, efeito de borda, comparação entre talhões |
| `04_series_temporais` | lacunas, sazonalidade, anomalia temporal e relativa |
| `05_mapas_interativos` | mapas folium, raster sobreposto, exportação GeoJSON/HTML |
| `06_insights_agricolas` | interpretação, limitações, hipóteses agronômicas, MapBiomas |

Saídas: figuras em `outputs/figures/`, mapas `outputs/mapa_ndvi_medio.html`, `mapa_raster_ndvi.html`, `mapa_anomalia_relativa.html` e `outputs/talhoes_resumo.geojson`. Mapas de períodos diferentes só são comparáveis com `vmin`/`vmax` fixos.

## 6. Metodologia e pipeline

### 6.1 CRS e geometria
- Medidas de área, perímetro e buffer são feitas em CRS métrico: UTM derivado do centróide (`gis.utm_crs_for_gdf`; zona = floor((lon+180)/6)+1, EPSG 327xx no hemisfério sul) ou EPSG:31982 (SIRGAS 2000 / UTM 22S) para Piraju. Resultados voltam ao CRS original (`gis.buffer_m`).
- Em EPSG:4326, `.area` devolve graus quadrados, sem significado em hectares. Em Piraju (lat ~ 23,2 graus S) 1 grau de longitude equivale a ~102 km.
- Web Mercator (EPSG:3857) distorce área por 1/cos²(lat): em Piraju, ~18,3% teórico (~18,9% medido nos talhões sintéticos). Use-o apenas para visualização.
- Área (ha) = área (m²) / 10 000. Compacidade de Polsby-Popper: 4*pi*A/P² (círculo = 1; quadrado = pi/4).
- Buffer de um quadrado de lado L: A = L² + 4*L*d + pi*d² (d > 0); para L = 100 m e d = 10 m, 14 314,16 m² (coberto em `tests/test_gis.py`).
- Fração de interseção: f = A(talhão ∩ máscara) / A(talhão).
- `gis.ensure_crs` emite aviso quando o CRS está ausente; `gis.validate_geometries` repara geometrias inválidas.

| EPSG | Tipo | Uso |
|---|---|---|
| 4326 | geográfico (WGS 84) | padrão de GeoJSON e Earth Engine |
| 4674 | geográfico (SIRGAS 2000) | datum oficial brasileiro |
| 31982 | UTM 22S (SIRGAS 2000) | medidas em Piraju |
| 5880 | Polyconic | Brasil inteiro |
| 3857 | Web Mercator | apenas visualização |

### 6.2 Índices espectrais
- Reflectância: rho = DN / 10 000.
- NDVI = (B8 - B4) / (B8 + B4). Intervalo [-1, 1]; faixas indicativas: água/nuvem <= ~0, solo ~0,1-0,3, vegetação densa > ~0,6. Satura em dossel denso e é sensível a solo e atmosfera.
- NDRE = (B8 - B5) / (B8 + B5) (alternativa: B8A). B5 tem 20 m, reamostrada a 10 m ao combinar com B8, com maior mistura de pixels. Valores tipicamente menores que os de NDVI.
- `indices.normalized_difference` converte para `float64` e devolve `NaN` onde a soma é zero.
- O deslocamento de +1000 do DN não se cancela na razão; por isso a coleção HARMONIZED.

| | NDVI | NDRE |
|---|---|---|
| Bandas | B8, B4 | B8 (ou B8A), B5 |
| Resolução nativa | 10 m | 20 m (B5) |
| Uso | série principal | série complementar |

### 6.3 Máscara de nuvens e composição
- Máscara por SCL (`indices.mask_invalid`, `ee_utils.mask_scl`) com as classes de `config.SCL_VALID`.
- Composição mensal por mediana (`timeseries.monthly_composite`, `min_obs` mínimo de observações por mês; `ee_utils.monthly_composites` no Earth Engine).
- No pixel de 10 m, buffer interno de 10 m reduz mistura de pixels de borda (nos talhões sintéticos, 11,7-17,1% dos pixels são removidos).

### 6.4 Estatísticas zonais
- `zonal.zonal_stats_raster`: média, desvio-padrão amostral (ddof = 1), coeficiente de variação (sigma/mu), percentis P10/P90, número de pixels; `all_touched` opcional.
- `zonal.summarize_by_talhao`, `zonal.rank_talhoes` e `zonal.compare_groups` (Kruskal-Wallis entre grupos; pressupõe independência, portanto o p-valor é apenas exploratório devido à autocorrelação).

### 6.5 Séries temporais e anomalias
- **Climatologia:** média das observações válidas de cada mês do ano no período-base, por talhão.
- **Anomalia temporal:** x - clim(talhão, mês); z = anomalia / sigma_clim(mês). Depende de período-base representativo e sem eventos.
- **Anomalia relativa:** (1) opcional remoção da média de cada talhão no período-base; (2) referência ref(t) = mediana entre talhões; (3) anom_rel = x' - ref(t); (4) média móvel centrada opcional (`window_days`). Remove efeitos comuns (atmosfera, clima, sazonalidade) e diferenças permanentes de nível; não detecta eventos que afetem todos os talhões.
- **z-score robusto:** z = (x - mediana) / (1,4826 * MAD).
- **Interpolação linear** limitada: x(t) = x0 + (x1 - x0)(t - t0)/(t1 - t0) entre observações válidas adjacentes, não aplicada se t1 - t0 > `max_gap_days`.
- Uso conjunto das duas anomalias: a relativa não vê eventos regionais; a temporal os confunde com sazonalidade se o período-base for curto.
- No notebook 04, o dado sintético permite conferir regras de detecção contra os eventos injetados (T03 transitório, T08 persistente). A regra persistente captura T08 e dilui T03; o z robusto captura T03 e normaliza T08; a união recupera ambos ao custo de um falso positivo (T01). Trata-se de teste de sanidade do método, não de desempenho em campo.

### 6.6 Culturas perenes
Dossel contínuo implica NDVI alto o ano todo e menor amplitude sazonal; há contribuição da entrelinha (mato, cobertura, solo); poda e esqueletamento alteram o dossel de forma abrupta; ciclo bienal de produção. Esses fatores limitam a interpretação (seção 8).

### 6.7 Leitura das figuras
Todas as figuras de `outputs/figures/` derivam de dados sintéticos.

| Figura | Conteúdo |
|---|---|
| `01_area_talhoes`, `01_buffers`, `01_regiao` | área por talhão; limite, buffer interno (-10 m) e externo (+30 m); municípios IBGE e talhões |
| `02_patch_mascara`, `02_disponibilidade_mensal`, `02_composicao_mensal`, `02_ndvi_ndre_t01` | NDVI com/sem máscara SCL e NDRE; % de observações válidas por mês; composição mensal; séries NDVI e NDRE de T01 |
| `03_efeito_borda`, `03_boxplot_talhoes`, `03_heatmap_talhao_mes` | média com e sem buffer interno por talhão; distribuição por talhão; talhão x mês (padrão vertical = efeito comum, horizontal = efeito do talhão) |
| `04_lacunas`, `04_interpolacao`, `04_climatologia`, `04_anomalia_temporal`, `04_anomalia_relativa` | disponibilidade de observações; preenchimento (<= 30 d) e suavização; climatologia 2021-2022; anomalias |
| `06_t03_t08` | anomalia relativa de T03 (transitória) e T08 (persistente) |

Mapas HTML: `mapa_ndvi_medio` (NDVI médio dos últimos 12 meses da série), `mapa_raster_ndvi` (raster reprojetado para lat/lon sobre OSM), `mapa_anomalia_relativa` (escala divergente simétrica em torno de 0).

## 7. Testes e validação

```bash
pytest -q
```

A suíte contém 30 testes (`tests/test_gis.py`, `test_indices.py`, `test_synthetic_zonal.py`, `test_timeseries.py`, `test_ee_maps.py`). Na integração com o Earth Engine, apenas a conversão `features_to_dataframe` possui teste automatizado; `ee_utils` e os scripts de exportação não foram testados contra o Earth Engine real e podem exigir ajustes. A consulta ao `collection_id` do MapBiomas não foi confirmada.

Os mapas HTML dependem de tiles via internet.

## 8. Limitações conhecidas

**Método**
1. NDVI/NDRE não diagnosticam doenças, pragas, nutrição ou produtividade; várias causas produzem o mesmo sinal.
2. Mistura de pixels: 10 m (B4/B8) e 20 m (B5, SCL). Em um talhão sintético de 5 ha há ~500 pixels de 10 m, dos quais ~14% são removidos por buffer interno de 10 m (11,7-17,1% nos talhões sintéticos). NDRE e SCL, a 20 m, têm ~4x menos pixels.
3. MapBiomas (30 m) não separa talhões pequenos, entrelinhas ou ruas.
4. Sazonalidade: compare mesmas épocas; a anomalia exige período-base representativo e sem eventos.
5. Nuvens e sombras: SCL é imperfeita; no verão chuvoso as lacunas são longas. No dado sintético, 36% das observações ficaram vazias (valor definido pelo gerador).
6. Culturas perenes: dossel contínuo, saturação, entrelinha, manejos abruptos, bienalidade, idade da lavoura.
7. Consistência do sensor: HARMONIZED mitiga a mudança de baseline; podem existir pequenas diferenças inter-satélite.
8. Autocorrelação: testes que supõem independência superestimam significância.
9. Anomalia relativa não vê eventos que afetem todos os talhões; anomalia temporal depende do período-base.
10. Regras de detecção têm trade-off entre sensibilidade e falsos alarmes.

**Dados**
- Talhões, séries e raster de exemplo são sintéticos.
- Malha IBGE em qualidade intermediária (simplificada).

**Código**
- `ee_utils` não foi testado contra o Earth Engine real.
- `reduceRegions` pode exceder limites de memória/tempo com muitos talhões/datas; para escala use `ee.batch.Export`.
- A coleção MapBiomas muda por versão; confira `collection_id` e `version`.

## 9. Licenças e atribuições

- **Código:** GPL-3.0 (`LICENSE`).
- **Sentinel-2:** Copernicus Sentinel Data Terms and Conditions; citar "Contains modified Copernicus Sentinel data [ano]".
- **MapBiomas:** CC-BY-4.0, atribuição obrigatória.
- **IBGE:** dados públicos; citar a fonte.
- **Basemaps:** OpenStreetMap (ODbL) e CARTO; manter a atribuição exibida.
- **Earth Engine:** sujeito aos termos do Google Earth Engine.

## 10. Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ee.EEException: ... not registered` | projeto sem registro no Earth Engine | registrar o projeto |
| `Computation timed out` / `User memory limit exceeded` | muitos talhões/datas em `getInfo()` | usar `ee.batch.Export.table.toDrive` e `tileScale` maior |
| `ModuleNotFoundError: agrogeo` | pacote não instalado | `pip install -e .` |
| `rasterio` não instala | sem wheel para a plataforma | `conda install -c conda-forge rasterio` |
| Mapas HTML sem fundo | sem internet (tiles) | conectar-se ou usar apenas camadas vetoriais |
