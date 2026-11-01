# Interpretação dos gráficos

Todos os gráficos dos notebooks usam dados **sintéticos**; as leituras abaixo ensinam *como ler*, não o que acontece em campo. Arquivos em `outputs/figures/`.

## Notebook 01
| Figura | Eixos | Como ler | Cuidado |
|---|---|---|---|
| `01_area_talhoes.png` | talhão × ha | barras = área em CRS métrico | tamanhos vêm do gerador |
| `01_buffers.png` | Leste × Norte (m) | contínua = limite; tracejada = −10 m (pixels "puros"); pontilhada = +30 m | eixo com aspecto igual |
| `01_regiao.png` | lon × lat | municípios IBGE; talhões em vermelho | malha simplificada (qualidade intermediária) |

## Notebook 02
| Figura | Como ler | Cuidado |
|---|---|---|
| `02_patch_mascara.png` | 3 painéis: NDVI sem máscara, com máscara SCL, NDRE mascarado. Cinza = descartado | solo exposto permanece (classe 5 válida) |
| `02_disponibilidade_mensal.png` | % de observações válidas por mês | padrão sazonal vem da probabilidade de nuvem definida no gerador |
| `02_composicao_mensal.png` | pontos cinza = observações; linha verde = mediana mensal (≥ 2 obs.) | meses ausentes não atingiram o mínimo |
| `02_ndvi_ndre_t01.png` | duas séries do mesmo talhão | relação NDVI→NDRE foi imposta pelo gerador |

## Notebook 03
| Figura | Como ler |
|---|---|
| `03_efeito_borda.png` | cada ponto = um talhão. Acima da diagonal: valor maior com buffer interno. Na média, interior ↑ e desvio ↓ (borda mistura entorno de NDVI baixo) |
| `03_boxplot_talhoes.png` | caixa = Q1–Q3, linha = mediana, bigodes sem outliers; ordenado por média |
| `03_heatmap_talhao_mes.png` | linha = talhão, coluna = mês; padrão **vertical** = efeito comum (clima/sazonalidade); **horizontal** = efeito do talhão; branco = sem dado |

## Notebook 04
| Figura | Como ler | Cuidado |
|---|---|---|
| `04_lacunas.png` | preto = observação válida; branco = ausente | colunas brancas em várias linhas = nuvem regional |
| `04_interpolacao.png` | cinza = dado; azul = preenchido (≤ 30 d); verde = média móvel | onde a azul some, não preenchemos |
| `04_climatologia.png` | curva grossa = média mensal 2021–22; cinzas = talhões | amplitude pequena frente ao ruído dificulta separar sinal |
| `04_anomalia_temporal.png` | anomalia = NDVI − clima do mês; preta = média móvel | base 2021–22 evita "normalizar" o evento |
| `04_anomalia_relativa.png` | azul = acima dos vizinhos; **vermelho = abaixo**; faixas horizontais persistentes = mudança específica do talhão | eventos regionais não aparecem |

## Notebook 06
`06_t03_t08.png`: duas curvas de anomalia relativa contra a mediana dos demais. T03 cai e recupera (transitório); T08 permanece baixo (persistente). A **forma** orienta hipóteses (veja tabela no notebook), sem diagnosticar.

## Mapas interativos (HTML)
- `mapa_ndvi_medio.html`: talhões coloridos pelo NDVI médio dos últimos 12 meses da série; legenda no canto inferior esquerdo; tooltip com atributos.
- `mapa_raster_ndvi.html`: raster reprojetado para lat/lon sobre OSM.
- `mapa_anomalia_relativa.html`: escala divergente simétrica em torno de 0.
Mapas de períodos diferentes só são comparáveis se `vmin`/`vmax` forem fixos.

## Checklist para ler qualquer gráfico de índice
1. Qual é a fonte (real/sintética) e o período?
2. Quantas observações válidas sustentam cada ponto?
3. A escala de cor é comum e centrada de forma justificável?
4. A variação é maior que o ruído/mistura de pixels esperados?
5. O padrão é do talhão ou comum a todos?
