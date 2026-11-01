# Questões para aprofundamento

## GIS
1. Por que o centróide de um polígono pode cair fora dele? Quando usar `representative_point`?
2. Compare a área de um talhão em EPSG:31982 e EPSG:5880. Em que escala de área a diferença passa a importar para um laudo?
3. O que muda ao tratar talhões como *multipolígonos* (talhões com divisão por carreadores)?
4. Como a precisão de GPS de campo (m) se compara ao tamanho do pixel (10 m) ao digitalizar talhões?

## Sensoriamento remoto
5. Por que a coleção HARMONIZED é necessária para séries que cruzam 2022? O que ocorreria sem ela em NDVI? (Pense em razão vs. diferença.)
6. Quais classes SCL você manteria para análise de entrelinha com mato alto? Justifique.
7. Como o ângulo solar e a sazonalidade afetam a comparação entre datas?
8. Que alternativas existem para lacunas longas (radar Sentinel-1, fusão com Landsat/HLS, modelos de gap-filling)? Quais os riscos de cada uma?

## Índices
9. Em que condições NDVI e NDRE divergem em dossel denso? Como testar com seus dados, evitando assumir a hipótese?
10. Proponha um índice de contraste de copa vs. entrelinha e discuta as limitações a 10 m.
11. Como estimar a incerteza de uma média zonal com *n* pixels autocorrelacionados espacialmente?

## Séries temporais
12. Compare média móvel, Savitzky–Golay e ajuste harmônico para suavização. Quando cada uma introduz viés?
13. Como definir um período-base "livre de eventos" sem conhecimento prévio?
14. Desenhe um experimento com injeção de eventos sintéticos de intensidades e durações variadas para medir sensibilidade × falsos alarmes (como no nb04, em escala).
15. Como incorporar chuva/temperatura para separar efeito climático de efeito de manejo?

## Agronomia
16. Que registros de campo (poda, colheita, adubação, irrigação, pragas) são essenciais para interpretar anomalias? Como estruturá-los para cruzar com talhões?
17. Como a bienalidade do café afeta a comparação ano a ano? Como controlar?
18. Que evidências de campo confirmariam ou refutariam cada hipótese da tabela do notebook 06?

## Dados e ética
19. Quais cuidados ao compartilhar mapas de talhões de produtores (privacidade, LGPD)?
20. Como citar corretamente Sentinel-2, MapBiomas, IBGE e OpenStreetMap em uma publicação?
21. Como garantir reprodutibilidade quando a coleção MapBiomas muda de versão?

## Adaptação a outras culturas e países
22. Que parâmetros você mudaria para soja (ciclo anual)? E para cana (ciclos de corte)?
23. Para outro país: como escolher o CRS (UTM/CRS nacional)? Onde obter limites administrativos? (`gis.utm_epsg_for` ajuda no CRS UTM.) O MapBiomas cobre o seu país? (Existem iniciativas MapBiomas para outros países da América do Sul — verifique cobertura e termos.)
