from ._helpers import NB, SETUP


def build():
    n = NB()
    n.md("""
# 03 · Análise de talhões: estatísticas zonais e comparação

**AgroGeo Analytics · Projeto 01**

> ⚠️ Raster e série usados aqui são **sintéticos** (veja `data/sample/` e `docs/pt-BR/07_proveniencia_dados.md`). Os números mostram *como calcular*, não resultados agronômicos.

## Objetivos
1. Calcular **estatísticas zonais** (média, desvio, percentis, CV) de um raster dentro de polígonos.
2. Medir o efeito da **mistura de pixels de borda** com buffer interno.
3. Resumir e **comparar talhões** ao longo do tempo (média, variabilidade, lacunas, ranking).
4. Visualizar talhão × mês em um mapa de calor.
""")
    n.code(SETUP + """
import rasterio
tal = gpd.read_file(DATA_SAMPLE / "talhoes_sinteticos.geojson")
serie = pd.read_csv(DATA_SAMPLE / "serie_sintetica_ndvi_ndre.csv", parse_dates=["date"])
RASTER = DATA_SAMPLE / "ndvi_sintetico.tif"
with rasterio.open(RASTER) as src:
    print("Raster:", src.crs, src.res, src.shape, "| tags:", src.tags())""")
    n.md("""
## 1. Atributos geométricos
""")
    n.code("""
tal["area_ha"] = gis.area_ha(tal, CRS_UTM22S)
tal[["talhao_id", "cultivar", "ano_plantio", "area_ha"]].round(2)
""")
    n.md("""
## 2. Estatísticas zonais no raster

Para cada polígono, `rasterio.mask` extrai os pixels cujo centro cai dentro do talhão (`all_touched=False`). Calculamos média, desvio-padrão, percentis e **coeficiente de variação** CV = σ/μ (variabilidade interna relativa).
""")
    n.code("""
z_full = zonal.zonal_stats_raster(tal, RASTER)
z_full.round(3)
""")
    n.md("""
## 3. Efeito da borda (mistura de pixels)

Pixels de borda misturam café com o entorno (no raster sintético, borda suavizada por filtro 3×3). Recalculamos com o talhão **encolhido em 10 m** e comparamos.
""")
    n.code("""
tal_int = tal.copy(); tal_int["geometry"] = gis.buffer_m(tal, -10, CRS_UTM22S).geometry
z_int = zonal.zonal_stats_raster(tal_int, RASTER)
cmp = z_full[["talhao_id", "n_pixels", "mean", "std"]].merge(
    z_int[["talhao_id", "n_pixels", "mean", "std"]], on="talhao_id", suffixes=("_total", "_interior"))
cmp["pixels_removidos_%"] = 100 * (1 - cmp["n_pixels_interior"] / cmp["n_pixels_total"])
cmp["delta_media"] = cmp["mean_interior"] - cmp["mean_total"]
cmp["delta_desvio"] = cmp["std_interior"] - cmp["std_total"]
print(cmp[["pixels_removidos_%", "delta_media", "delta_desvio"]].describe().loc[["mean", "min", "max"]].round(4))
cmp.round(3)
""")
    n.code("""
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
axs[0].scatter(cmp["mean_total"], cmp["mean_interior"], color="#2e7d32")
lim = [cmp[["mean_total", "mean_interior"]].min().min() - .01, cmp[["mean_total", "mean_interior"]].max().max() + .01]
axs[0].plot(lim, lim, "k--", lw=.8); axs[0].set(xlabel="Média (talhão inteiro)", ylabel="Média (interior −10 m)", title="Média zonal")
axs[1].scatter(cmp["std_total"], cmp["std_interior"], color="#c2185b")
lim = [0, cmp[["std_total", "std_interior"]].max().max() * 1.1]
axs[1].plot(lim, lim, "k--", lw=.8); axs[1].set(xlabel="Desvio (inteiro)", ylabel="Desvio (interior)", title="Desvio-padrão zonal")
fig.suptitle(SYNTH_NOTE, fontsize=8); plt.tight_layout()
plt.savefig(OUTPUTS / "figures" / "03_efeito_borda.png"); plt.show()
""")
    n.md("""
**Como ler:** pontos acima da diagonal = valor maior no interior. A média *aumenta* um pouco (borda diluída pelo entorno de NDVI baixo) e o desvio *diminui* (menos mistura) — comportamento esperado do filtro aplicado no raster sintético. Em dados reais, o mesmo teste informa o quanto a borda pesa nos seus talhões; **o tamanho do efeito depende do talhão e da imagem**.
""")
    n.md("""
## 4. Resumo temporal por talhão

Usando a série (sintética), resumimos cada talhão: nº de observações válidas, % de lacunas, média, desvio, CV e P10/P90.
""")
    n.code("""
resumo = zonal.summarize_by_talhao(serie, "ndvi")
rank = zonal.rank_talhoes(resumo, "media")
rank.round(3)
""")
    n.code("""
ordem = rank["talhao_id"].tolist()
dados = [serie.loc[serie.talhao_id == t, "ndvi"].dropna().values for t in ordem]
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.boxplot(dados, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#a5d6a7"))
ax.set_xticks(range(1, len(ordem) + 1)); ax.set_xticklabels(ordem)
ax.set(ylabel="NDVI", title="Distribuição do NDVI por talhão (ordenado pela média) — sintético")
plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "03_boxplot_talhoes.png"); plt.show()
kw = zonal.compare_groups(serie, "ndvi")
print(f"Kruskal-Wallis: H={kw['H']:.1f}, p={kw['p_value']:.2e} ({kw['n_groups']} talhões)")
""")
    n.md("""
**Como ler o boxplot:** caixa = quartis (Q1–Q3), linha = mediana, bigodes = amplitude sem outliers. Caixas deslocadas indicam níveis médios diferentes.

**Sobre o teste:** o Kruskal-Wallis compara distribuições entre grupos, mas as observações de um mesmo talhão são **autocorrelacionadas no tempo**, então o p-valor está inflado (parece significativo demais). Use-o só como indicador exploratório; a pergunta agronômica relevante é "a diferença é grande o bastante para importar?" (tamanho de efeito), não "p < 0,05".
""")
    n.md("""
## 5. Mapa de calor talhão × mês
""")
    n.code("""
m = ts_lib.monthly_composite(serie, "ndvi", "median", min_obs=2)
piv = m.pivot(index="talhao_id", columns="mes", values="ndvi").loc[ordem]
fig, ax = plt.subplots(figsize=(10, 3.8))
im = ax.imshow(piv.values, aspect="auto", cmap="RdYlGn", vmin=0.55, vmax=0.85)
ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index, fontsize=8)
ticks = np.arange(0, piv.shape[1], 6); ax.set_xticks(ticks); ax.set_xticklabels([piv.columns[i].strftime("%Y-%m") for i in ticks], rotation=45, fontsize=8)
ax.grid(False); plt.colorbar(im, label="NDVI (mediana mensal)")
ax.set_title("NDVI mensal por talhão — sintético (células vazias = sem observação válida)")
plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "03_heatmap_talhao_mes.png"); plt.show()
""")
    n.md("""
**Como ler:** cada linha é um talhão, cada coluna um mês; verde = NDVI alto, vermelho = baixo, branco = sem dado. Padrões verticais (todas as linhas mudam juntas) são **sazonalidade/clima/atmosfera**; padrões horizontais (uma linha se destaca) são **diferenças específicas do talhão** — o foco do notebook 04.
""")
    n.code("""
saida = tal[["talhao_id", "cultivar", "ano_plantio", "area_ha"]].merge(resumo, on="talhao_id").merge(
    z_int[["talhao_id", "mean", "std"]].rename(columns={"mean": "raster_ndvi_medio_interior", "std": "raster_ndvi_desvio_interior"}), on="talhao_id")
(config.DATA_PROCESSED).mkdir(parents=True, exist_ok=True)
saida.to_csv(config.DATA_PROCESSED / "estatisticas_talhoes.csv", index=False)
print("Salvo em data/processed/estatisticas_talhoes.csv", saida.shape)
""")
    n.md("""
## 6. Exercícios
1. Calcule o CV por talhão no raster (`z_full["cv"]`). Qual talhão é mais heterogêneo *na imagem sintética*? O que isso significaria no campo (hipóteses, não conclusões)?
2. Rode `zonal_stats_raster(..., all_touched=True)`. Por que o nº de pixels aumenta e o que acontece com a média?
3. Substitua a média por **mediana** e **P10** no ranking. O ranking muda? Qual métrica é mais robusta a lacunas e pixels ruins?
""")
    return n
