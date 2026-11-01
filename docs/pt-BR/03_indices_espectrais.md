# Índices espectrais

## NDVI — Normalized Difference Vegetation Index
**Sentinel-2:** NDVI = (B8 − B4) / (B8 + B4)
- Intervalo [−1, 1]. Água/nuvem: ≈ ≤ 0; solo: ~0,1–0,3; vegetação densa: > ~0,6 (faixas são **indicativas** e dependem do contexto).
- **Pontos fortes:** simples, robusto, resolução de 10 m, longa tradição.
- **Fraquezas:** satura em dossel denso; sensível a solo/brilho de fundo e atmosfera; não é medida física direta de biomassa, clorofila ou produtividade.

## NDRE — Normalized Difference Red Edge
**Sentinel-2:** NDRE = (B8 − B5) / (B8 + B5) (alternativa: B8A no lugar de B8)
- Usa a banda red edge, que satura mais tarde que o vermelho; frequentemente empregado para dosséis densos.
- **Resolução:** B5 tem 20 m (reamostrada a 10 m ao combinar com B8): mistura de pixels mais forte.
- Valores tipicamente menores que os de NDVI.
- A literatura associa NDRE à clorofila/N foliar em condições controladas; **isso não autoriza usá-lo como diagnóstico** de deficiência nutricional ou doença neste projeto.

## Comparação
| | NDVI | NDRE |
|---|---|---|
| Bandas | B8, B4 | B8 (ou B8A), B5 |
| Resolução nativa | 10 m | 20 m (B5) |
| Saturação em dossel denso | mais cedo | mais tarde (hipótese a verificar) |
| Sensibilidade ao solo | alta | menor |
| Uso aqui | série principal | série complementar |

## Anomalias
- **Temporal**: valor − média do mesmo mês do ano no próprio talhão (período-base). Responde "está fora do normal para a época?".
- **Relativa**: valor do talhão − mediana dos talhões na data (após remover a média de cada um no período-base). Responde "mudou diferente dos vizinhos?".
- **z-score robusto**: (x − mediana)/(1,4826·MAD).

Use as duas anomalias juntas: a relativa não vê eventos regionais; a temporal os confunde com sazonalidade se o período-base for curto.

## O que NDVI/NDRE **não** fazem
- Não diagnosticam doenças, pragas ou deficiências.
- Não medem produtividade (a relação com produtividade deve ser calibrada com dados de campo, por cultura e região).
- Não distinguem causas: poda, seca, mato na entrelinha e doença podem produzir sinais parecidos.
