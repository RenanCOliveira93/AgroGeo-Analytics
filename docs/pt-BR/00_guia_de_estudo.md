# Guia de estudo — AgroGeo Analytics

Roteiro para estudar o projeto do zero, em ~12–16 horas (4 a 6 sessões).

## Pré-requisitos
- Python básico (pandas, funções, matplotlib).
- Noções de estatística descritiva (média, desvio, percentil).
- Não é necessário conhecer GIS nem sensoriamento remoto — os documentos 01–04 cobrem o essencial.

## Como os materiais se organizam
| Camada | Onde | Para quê |
|---|---|---|
| Conceito | `docs/pt-BR/01–04` | teoria curta, com fórmulas |
| Prática | `notebooks/01–06` | executar, alterar, quebrar |
| Código reutilizável | `src/agrogeo/` | funções testadas (`tests/`) |
| Aprofundamento | `docs/pt-BR/05–11` | linha a linha, gráficos, limitações, exercícios |

## Roteiro sugerido
| Sessão | Ler | Executar | Entregável seu |
|---|---|---|---|
| 1 | [01 Fundamentos GIS](01_fundamentos_gis.md) | `notebooks/01_fundamentos_gis.ipynb` | exercícios 1–3 do nb01 |
| 2 | [02 Sensoriamento remoto](02_sensoriamento_remoto.md), [03 Índices](03_indices_espectrais.md), [04 Fórmulas](04_formulas.md) | `02_dados_satellite.ipynb` | explicação própria do efeito da máscara SCL |
| 3 | [05 Walkthrough](05_walkthrough_linha_a_linha.md) (parte zonal) | `03_analise_talhoes.ipynb` | ranking de talhões com métricas robustas |
| 4 | [06 Gráficos](06_interpretacao_graficos.md) | `04_series_temporais.ipynb` | experimento de limiares (exercício 04.1) |
| 5 | [07 Proveniência](07_proveniencia_dados.md) | `05_mapas_interativos.ipynb` | mapa HTML com sua variável |
| 6 | [08 Limitações](08_limitacoes.md), [11 Questões](11_questoes_aprofundamento.md) | `06_insights_agricolas.ipynb` | texto de 1 página: sinal → hipótese → verificação |

## Regras de ouro do projeto
1. **Dados sintéticos são rotulados** (coluna `SINTETICO`, títulos "sintético") e **nunca** são resultados empíricos.
2. **Índice de vegetação ≠ diagnóstico.** Gera hipóteses a verificar em campo.
3. **Área só em CRS métrico.**
4. **Reporte lacunas e nº de pixels** junto com qualquer média.

## Instalação e execução
Veja o [README](../../README.md) e [09 Instalação e Earth Engine](09_instalacao_earth_engine.md).

## Autoavaliação
Você domina o projeto quando consegue, sem consultar, explicar: (a) por que EPSG:3857 não serve para área; (b) por que a máscara SCL não remove solo exposto; (c) a diferença entre anomalia temporal e relativa; (d) por que NDVI não diagnostica doença; (e) como substituir os talhões sintéticos pelos seus.
