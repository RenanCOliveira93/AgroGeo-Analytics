# Sensoriamento remoto aplicado à agricultura

## 1. Princípio
Sensores passivos medem a **radiação solar refletida** pela superfície em faixas espectrais (bandas). A vegetação sadia, de forma geral:
- **absorve** muito no vermelho (clorofila);
- **reflete** muito no infravermelho próximo (NIR), por causa da estrutura celular das folhas;
- tem transição abrupta entre ambos — o **red edge** (~700–750 nm).

Solo exposto, água e nuvens têm assinaturas diferentes, o que permite índices que as separam.

## 2. Sentinel-2
Missão da Agência Espacial Europeia (programa Copernicus), com satélites em constelação.
| Característica | Valor (conforme catálogo do Earth Engine) |
|---|---|
| Revisita | 5 dias (com a constelação completa) |
| Resolução | 10 m (B2, B3, B4, B8), 20 m (B5, B6, B7, B8A, B11, B12, SCL), 60 m (B1, B9) |
| Produto usado | `COPERNICUS/S2_SR_HARMONIZED` (reflectância de superfície, nível 2A) |
| Escala | reflectância = DN / 10 000 |

**Harmonização:** cenas processadas com baseline ≥ 04.00 (a partir de 25/01/2022) têm um deslocamento de +1000 no DN; a coleção HARMONIZED o remove para manter consistência com cenas antigas. Use-a para séries que cruzam 2022.

**Disponibilidade:** o catálogo lista cobertura de 2017-03-28 em diante; observe que, segundo o próprio catálogo, a cobertura L2A de 2017–2018 não é global. Verifique para sua área antes de assumir série de 2017.

## 3. Correção atmosférica e nuvens
SR = reflectância **na superfície**, após correção atmosférica (Sen2Cor). Ainda assim restam nuvens finas, cirrus e sombras. A banda **SCL** (Scene Classification Layer, 20 m) classifica cada pixel:

| Valor | Classe | Uso neste projeto |
|---|---|---|
| 0 | sem dado | descarta |
| 1 | saturado/defeituoso | descarta |
| 2 | área escura | mantém¹ |
| 3 | sombra de nuvem | descarta |
| 4 | vegetação | mantém |
| 5 | solo exposto | mantém |
| 6 | água | mantém |
| 7 | nuvem baixa prob./não classificado | mantém¹ |
| 8 | nuvem prob. média | descarta |
| 9 | nuvem prob. alta | descarta |
| 10 | cirrus | descarta |
| 11 | neve/gelo | descarta |

¹ Escolha do projeto (`config.SCL_VALID`); é um ponto de ajuste. Classe 7 pode conter nuvem fina residual — a composição por mediana mitiga.

## 4. Resoluções
- **Espacial**: tamanho do pixel. Define mistura de pixels e o menor talhão analisável.
- **Temporal**: revisita (5 d), reduzida na prática por nuvens (verão chuvoso).
- **Espectral**: bandas disponíveis (inclui 3 bandas red edge — raras em sensores gratuitos).
- **Radiométrica**: sensibilidade (12 bits).

## 5. Mistura de pixels
O valor de um pixel é uma média ponderada do que há dentro dele (folhas, solo, sombra, estrada). Em talhões pequenos e bordas, o pixel não é "café puro". Mitigações: buffer interno, filtro por nº mínimo de pixels, reporte da fração de pixels válidos.

## 6. Culturas perenes (café)
Dossel contínuo → NDVI alto o ano todo e amplitude sazonal menor; contribuição de entrelinha (mato/cobertura/solo); manejos como poda e esqueletamento alteram o dossel abruptamente; ciclo bienal de produção. Veja [08 Limitações](08_limitacoes.md).

## 7. MapBiomas
Projeto colaborativo que mapeia uso e cobertura da terra no Brasil (Landsat, 30 m, anual). Classe **46 = Café** (consulte a legenda da coleção em uso). Serve como contexto, não como delineador de talhões (30 m).
