# Limitações

## Do método
1. **NDVI/NDRE não diagnosticam doenças, pragas, nutrição ou produtividade.** Indicam reflectância; várias causas produzem o mesmo sinal.
2. **Mistura de pixels.** Pixel de 10 m (B4/B8) e 20 m (B5, SCL). Num talhão sintético de 5 ha há ≈ 500 pixels de 10 m, dos quais ~14% são removidos por um buffer interno de 10 m (valores medidos nos talhões sintéticos: 11,7–17,1%). NDRE e SCL, a 20 m, têm ≈ 4× menos pixels.
3. **Resolução espacial.** MapBiomas (30 m) não separa talhões pequenos, entrelinhas ou ruas.
4. **Sazonalidade.** Compare mesmas épocas; anomalia exige período-base representativo e sem eventos.
5. **Nuvens e sombras.** SCL é imperfeita; no verão chuvoso as lacunas são longas. No dado sintético, 36% das observações ficaram vazias — valor definido pelo gerador, não medido.
6. **Culturas perenes.** Dossel contínuo (NDVI alto e pouco sazonal), saturação, contribuição da entrelinha, manejos abruptos (poda/esqueletamento), bienalidade, idade da lavoura.
7. **Consistência do sensor.** HARMONIZED mitiga a mudança de baseline; o Sentinel-2 tem constelação com mais de um satélite, e pequenas diferenças inter-sensor existem.
8. **Autocorrelação.** Testes que supõem independência (p-valores) superestimam significância.
9. **Anomalia relativa** não vê eventos que afetem todos os talhões; **anomalia temporal** depende do período-base.
10. **Regras de detecção** têm trade-off sensibilidade × falsos alarmes (veja nb04, onde a regra transitória marcou T01, que não tinha evento).

## Dos dados
- Talhões, séries e raster de exemplo são **sintéticos**.
- Malha IBGE em qualidade intermediária (simplificada).
- Earth Engine e MapBiomas **não foram executados** no ambiente de desenvolvimento (sem credenciais).

## Do código
- `ee_utils` não foi testado contra o Earth Engine real; só a conversão `features_to_dataframe` tem teste automatizado.
- `reduceRegions` pode estourar limite de memória/tempo em muitos talhões/datas; para escala use `ee.batch.Export`.
- A coleção MapBiomas muda por versão; `collection_id`/`version` devem ser conferidos.

## De escopo
Sem verdade de campo, o projeto não valida nenhuma hipótese agronômica nem relação com produtividade. Para decisões de manejo, envolva um engenheiro agrônomo.
