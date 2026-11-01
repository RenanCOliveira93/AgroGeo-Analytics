# Exercícios resolvidos

Todos os números abaixo foram obtidos executando o código do projeto sobre os dados **sintéticos** (ou a malha real do IBGE, onde indicado). São respostas para o *exercício*, não achados agronômicos. Reexecute para confirmar.

## Notebook 01
**1. Área de Piraju vs. valor oficial.**
`gis.area_ha(municipio, "EPSG:31982")` → **50 572,9 ha = 505,73 km²**. IBGE (Censo 2022, tabela 4714/variável 6318): **504,591 km²**. Diferença: **+0,23%**. A malha em qualidade intermediária é simplificada; diferenças dessa ordem são esperadas (causa exata não investigada).

**2. Buffer que mantém ≥ 70% do menor talhão.**
Menor talhão: T10, 4,98 ha. Fração mantida: −5 m → 91,2%; −10 m → 82,8%; −15 m → 74,8%. Os três mantêm ≥ 70%; −15 m é o maior testado (valores maiores não foram avaliados).

**3. Web Mercator a −12° de latitude.**
Fator de área = 1/cos²(12°) − 1 = **4,5%**, menor que o de Piraju (~18%): a distorção diminui ao se aproximar do equador (cos φ cresce).

## Notebook 02
**1. `min_obs` = 1, 2, 3.** Combinações talhão×mês com composição vazia (sobre 566 combinações com ≥ 1 observação válida): 0 → 44 → 114. Com `min_obs=2`, 33 das 44 ausências caem em dez–mar; com 3, 75 das 114. Exigir mais observações custa principalmente meses chuvosos (no gerador, onde a nuvem é mais provável por construção).

**2. Remover a classe 7 de `SCL_VALID`.** Não se aplica à série sintética (não há banda SCL nela). Com Earth Engine real, compare `col.size()` e o nº de pixels válidos por talhão antes/depois: espera-se menos pixels válidos, e talvez menos nuvem fina residual. Resultado depende dos seus dados; não foi executado aqui.

**3. NDRE com B8A.** B8A (narrow NIR, ~865 nm) tem 20 m, igual ao B5; ao usar B8A + B5 todo o índice passa a ter resolução nativa de 20 m (sem reamostrar B8 de 10 m) — coerente, porém mais grosseiro. Troca-se `"B8"` por `"B8A"` em `normalizedDifference`.

## Notebook 03
**1. CV por talhão no raster sintético.** Maiores CV: T04 (0,0725), T07 (0,0721), T10 (0,0699). Aqui vêm do ruído simulado e da proporção de borda (T10 é o menor talhão), mas a relação com a área não é estritamente monotônica (T06 é menor que T04 e T07). Em dados reais, CV alto motivaria *hipóteses* (variação de solo/relevo, falhas, plantas daninhas, borda) a verificar em campo.

**2. `all_touched=True`.** Inclui pixels que apenas tocam o polígono → nº de pixels × 1,06–1,10 (média 1,076). A média zonal cai em média 0,0165 e o desvio sobe em média 0,029, porque entram pixels de borda mistos (NDVI menor e mais variável no raster sintético).

**3. Ranking por média, mediana ou P10.** Os quatro primeiros são iguais nas três métricas (T09, T01, T04, T12); a ordem do meio do ranking muda (p. ex., T06/T02/T10 trocam de posição). Mediana e P10 são menos sensíveis a observações extremas e a lacunas desiguais, mas P10 enfatiza a cauda inferior.

## Notebook 04
**1. Efeito de `window_days` e do limiar de |z|** (talhões com ≥ 5 datas marcadas a partir de 2023-01-01; z robusto sobre a série completa):

| janela | |z| > 2,5 | |z| > 3 | |z| > 4 |
|---|---|---|---|
| 0 d | T03, T10, T12 | T03 | T03 |
| 15 d | T01, T03, T12 | T03, T12 | T03 |
| 60 d | T01, T03, T04 | T01, T03, T04 | T03 |

Limiares baixos e janelas longas aumentam a sensibilidade e os falsos positivos; o limiar 4 só encontra T03. **T08 não aparece em nenhuma célula**: a regra de z robusto não captura anomalias persistentes (viram o "normal" da série) — por isso o notebook usa também a regra baseada na média. (Os resultados do notebook diferem desta tabela porque lá os dias marcados são contados sobre a série inteira.)

**2. Base que inclui o evento.** Anomalia média do T03 entre 10/08 e 30/09/2023: **−0,126** com base 2021–22; **−0,093** com base 2021–23. Incluir o evento no período-base reduz a anomalia (~26%), porque o evento passa a fazer parte do "normal" — e seu efeito se espalha para outros anos do clima.

**3. Queda regional simulada** (−0,1 em todos os talhões em jun/2023). Anomalia **relativa** média em jun/2023: **−0,0017** (≈ 0: não detecta); anomalia **temporal**: **−0,104** (detecta). Mostra por que usar ambas.

## Notebook 05 e 06 (respostas conceituais)
- *Mapa de NDRE:* basta mapear `ndre_medio_12m`; padrões espaciais diferem quando o NDVI está saturado (se a hipótese de maior sensibilidade do NDRE for verdadeira para seus dados — testar).
- *Mapa por idade:* use `ano_plantio` como `value_col` com `cmap` sequencial.
- *Comparação de períodos:* fixe `vmin`/`vmax` iguais nas duas chamadas de `choropleth_talhoes`.
- *Mediana vs. MVC (máximo mensal):* MVC reduz nuvem residual mas tem viés para valores altos e é sensível a outliers de brilho; mediana é mais conservadora.
