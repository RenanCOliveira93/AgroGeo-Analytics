# Instalação e autenticação do Earth Engine

## 1. Ambiente Python
Requer Python ≥ 3.10 (desenvolvido e testado em 3.11 / macOS). GeoPandas, Rasterio e Shapely têm *wheels* binárias para as plataformas comuns; em sistemas sem wheel, instale GDAL/GEOS/PROJ pelo gerenciador de pacotes (ou use `conda`).

```bash
cd 01-AgroGeo-Analytics
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                      # instala o pacote agrogeo (src/)
python -m ipykernel install --user --name python3 --display-name "Python 3 (agrogeo)"   # opcional
```

## 2. Testes
```bash
pytest -q
```

## 3. Earth Engine (opcional — notebooks rodam offline sem isso)
1. Crie/escolha um **projeto Google Cloud** e **registre-o para uso do Earth Engine** (https://earthengine.google.com — confira a elegibilidade para uso não comercial/comercial).
2. Copie `.env.example` para `.env` e preencha `EE_PROJECT=<seu-projeto>` e `AGROGEO_USE_EE=1`.
3. Autentique (abre o navegador):
   ```bash
   earthengine authenticate
   ```
   Alternativa em Python: `import ee; ee.Authenticate(); ee.Initialize(project="seu-projeto")`.
   Em ambientes sem navegador (servidores), use `earthengine authenticate --auth_mode=notebook` e cole o código, ou uma conta de serviço.
4. Teste:
   ```bash
   python -c "from agrogeo.ee_utils import init_ee; ee=init_ee(); print(ee.Number(1).add(1).getInfo())"
   ```
   Deve imprimir `2`.

> Nunca versione `.env` nem credenciais (já ignorados no `.gitignore`).

## 4. Reprodução completa
```bash
# (a) dados de exemplo (já incluídos; para regenerar)
python scripts/download_ibge.py --codigo 3538808
python scripts/download_ibge.py --vizinhos
python scripts/generate_sample_data.py

# (b) notebooks (reconstruir e executar)
python scripts/build_notebooks.py        # regenera .ipynb a partir de scripts/nbdefs
python scripts/run_notebooks.py          # executa todos e grava as saídas

# (c) dados reais (requer Earth Engine)
python scripts/export_s2_timeseries.py --talhoes SEU_ARQUIVO.geojson --out data/processed/serie_s2.csv
python scripts/export_mapbiomas_stats.py --geojson SEU_ARQUIVO.geojson --year 2023
```
Seu GeoJSON de talhões deve estar em EPSG:4326 e ter a coluna `talhao_id` (única por talhão).

Para que os notebooks 03–06 usem a série real, ajuste a leitura do CSV (`data/processed/serie_s2.csv`) na célula de carregamento — mantendo as colunas `date, talhao_id, ndvi, ndre`. Atenção: a série do Earth Engine é **mensal** (composição por mediana), não de 5 dias; ajuste `window_days`, `min_obs` e `step` nos parâmetros das funções.

## 5. Problemas comuns
| Sintoma | Causa provável | Solução |
|---|---|---|
| `ee.EEException: ... not registered` | projeto sem registro no EE | registrar o projeto |
| `Computation timed out` / `User memory limit exceeded` | muitos talhões/datas em `getInfo()` | usar `ee.batch.Export.table.toDrive` e `tileScale` maior |
| `ModuleNotFoundError: agrogeo` | pacote não instalado | `pip install -e .` |
| `rasterio` não instala | sem wheel p/ sua plataforma | usar `conda install -c conda-forge rasterio` |
| Mapas HTML sem fundo | sem internet (tiles) | conectar-se ou usar apenas camadas vetoriais |
