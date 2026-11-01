# AgroGeo Analytics

Estudo de **Geospatial Data Science** aplicado à agricultura, com foco em **cafeicultura em Piraju/SP** (adaptável a outras culturas e países). Entregável central: **6 notebooks Jupyter executáveis** com documentação em PT-BR. [English version](README.en.md)

> **Aviso sobre dados.** Os talhões, a série NDVI/NDRE e o raster de exemplo são **SINTÉTICOS** (gerados com semente fixa; rotulados em arquivos, colunas e gráficos). Eles existem para o código rodar offline e para fins didáticos — **não são resultados empíricos**. O limite municipal de Piraju (e vizinhos) é **real** (IBGE). Para uso real, forneça seu GeoJSON de talhões e use o Earth Engine.
>
> **NDVI/NDRE não diagnosticam doenças, pragas ou deficiências**; indicam reflectância e geram *hipóteses* a verificar em campo.

## O que há no projeto
| Notebook | Conteúdo |
|---|---|
| [01_fundamentos_gis](notebooks/01_fundamentos_gis.ipynb) | CRS/EPSG, geometria, reprojeção, área, buffers, interseções |
| [02_dados_satellite](notebooks/02_dados_satellite.ipynb) | Sentinel-2, máscara SCL, composições temporais, NDVI e NDRE, Earth Engine |
| [03_analise_talhoes](notebooks/03_analise_talhoes.ipynb) | estatísticas zonais, efeito de borda, comparação entre talhões |
| [04_series_temporais](notebooks/04_series_temporais.ipynb) | lacunas, sazonalidade, anomalia temporal e relativa |
| [05_mapas_interativos](notebooks/05_mapas_interativos.ipynb) | mapas folium, raster sobreposto, exportação GeoJSON/HTML |
| [06_insights_agricolas](notebooks/06_insights_agricolas.ipynb) | interpretação, limitações, hipóteses agronômicas, MapBiomas |

```
src/agrogeo/     funções reutilizáveis (gis, indices, zonal, timeseries, maps, ee_utils, synthetic, config)
tests/           pytest (30 testes)
scripts/         download IBGE, geração dos dados de exemplo, export Earth Engine/MapBiomas, build/run dos notebooks
data/sample/     dados pequenos: malha IBGE (real) + talhões/série/raster (sintéticos)
docs/pt-BR/      guia de estudo, GIS, sensoriamento remoto, índices, fórmulas, walkthrough, gráficos,
                 proveniência, limitações, instalação, exercícios resolvidos, questões
outputs/         figuras, mapas HTML e GeoJSON gerados pelos notebooks
```

## Instalação
Requer Python ≥ 3.10.
```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest -q                                                # 30 testes
jupyter lab notebooks/                                   # ou: python scripts/run_notebooks.py
```
Os notebooks rodam **offline** com os dados de `data/sample/` (modo padrão).

## Earth Engine (opcional, dados reais)
1. Registre um projeto Google Cloud para o Earth Engine ([earthengine.google.com](https://earthengine.google.com); verifique os termos de uso não comercial/comercial).
2. `cp .env.example .env` e preencha `EE_PROJECT` e `AGROGEO_USE_EE=1`.
3. `earthengine authenticate`
4. `python scripts/export_s2_timeseries.py --talhoes SEU.geojson --out data/processed/serie_s2.csv`
5. `python scripts/export_mapbiomas_stats.py --geojson SEU.geojson --year 2023`

Detalhes e solução de problemas: [docs/pt-BR/09_instalacao_earth_engine.md](docs/pt-BR/09_instalacao_earth_engine.md).

## Reprodução dos dados de exemplo
```bash
python scripts/download_ibge.py --codigo 3538808 && python scripts/download_ibge.py --vizinhos
python scripts/generate_sample_data.py
python scripts/build_notebooks.py && python scripts/run_notebooks.py
```

## Fontes (verificadas em 2026-10-31)
- **Sentinel-2 SR Harmonized** — `COPERNICUS/S2_SR_HARMONIZED` (Earth Engine); termos: Copernicus Sentinel Data Terms and Conditions.
- **MapBiomas Brasil** — `projects/mapbiomas-public/assets/brazil/lulc/v1` (30 m; CC-BY-4.0 conforme catálogo); classe 46 = Café.
- **IBGE** — malhas municipais (API de Malhas v3). Piraju = 3538808.
- **Talhões** — GeoJSON do usuário; na ausência, sintéticos (explicitamente identificados).

Detalhes, licenças e como os dados sintéticos foram feitos: [docs/pt-BR/07_proveniencia_dados.md](docs/pt-BR/07_proveniencia_dados.md).

## Estado de verificação (neste ambiente de desenvolvimento)
| Item | Estado |
|---|---|
| `pytest` (30 testes) | **executado, passou** |
| Notebooks 01–06 (modo offline) | **executados com sucesso** (saídas gravadas nos `.ipynb`) |
| Download IBGE | **executado** (API respondeu; dados salvos) |
| Earth Engine (`ee_utils`, `export_s2_timeseries.py`, `export_mapbiomas_stats.py`) | **NÃO executado** — sem credenciais; só a conversão `features_to_dataframe` tem teste. Código escrito conforme a documentação; pode exigir ajustes |
| MapBiomas (filtro `collection_id=10`, `version="v1"`) | **NÃO executado/confirmado** — confirme os valores no asset |
| Mapas HTML | gerados; **não abertos em navegador** (tiles exigem internet) |

## Limitações (resumo)
Mistura de pixels (10/20 m), sazonalidade, nuvens, culturas perenes (dossel contínuo, bienalidade, poda), autocorrelação e ausência de verdade de campo. Veja [docs/pt-BR/08_limitacoes.md](docs/pt-BR/08_limitacoes.md).

## Documentação
Comece por [docs/pt-BR/00_guia_de_estudo.md](docs/pt-BR/00_guia_de_estudo.md).

## Repositório, versionamento e execução em outra máquina

Código publicado a partir da máquina de desenvolvimento original (macOS, Podman). Isto **não** foi executado em GitHub Codespaces nem em Docker Desktop; se rodar lá, trate como primeira verificação e compare com a seção de testes.

- **Versionado:** pacote `src/`, `scripts/`, notebooks já executados, testes (30), `docs/pt-BR/` e `data/sample/` (dados **sintéticos** de demonstração; os notebooks rodam offline com eles).
- **Não versionado:** `data/raw/` e `data/processed/` (downloads do IBGE e derivados). Para recriar: `python scripts/download_ibge.py --codigo 3538808 && python scripts/download_ibge.py --vizinhos` (precisa de internet) e `python scripts/generate_sample_data.py`.
- **Não executado nesta entrega:** Earth Engine (exige conta/credenciais); veja a seção *Estado de verificação*.
- **Licença do código:** GPL-3.0 (arquivo `LICENSE`). Licenças e atribuições de dados/modelos de terceiros: veja as seções e docs indicados acima.
