# Explicação das fórmulas

## Reflectância
ρ = DN / 10 000. Exemplo: DN = 3 800 → ρ = 0,38.

## NDVI
NDVI = (ρ_NIR − ρ_RED) / (ρ_NIR + ρ_RED)

Por que dividir pela soma? Normaliza pela intensidade total: duas cenas com iluminação diferente, mas mesma proporção NIR/vermelho, dão o mesmo NDVI. Exemplo: NIR = 0,50 e RED = 0,10 → (0,40)/(0,60) = **0,667**. O fator 1/10 000 cancela (numerador e denominador), mas o *offset* de +1000 não — daí a coleção HARMONIZED.

Quando ρ_NIR + ρ_RED = 0 o índice é indefinido; `indices.normalized_difference` devolve NaN.

## NDRE
NDRE = (ρ_NIR − ρ_RE) / (ρ_NIR + ρ_RE). Exemplo: NIR = 0,40, RE = 0,20 → 0,20/0,60 = **0,333**.

## Área
A(ha) = A(m²) / 10 000, com A calculada em CRS métrico.

## Buffer
Buffer de d metros expande (d > 0) ou encolhe (d < 0) o polígono. Para um quadrado de lado L: A = L² + 4·L·d + π·d² (d > 0). Para L = 100 m, d = 10 m: 10 000 + 4 000 + 314,16 = 14 314,16 m² (verificado em `tests/test_gis.py`).

## Compacidade (Polsby–Popper)
PP = 4πA / P². Círculo = 1; quadrado = π/4 ≈ 0,785.

## Estatísticas zonais
- Média μ = Σxᵢ/n; desvio-padrão amostral σ (ddof = 1).
- **Coeficiente de variação** CV = σ/μ.
- Percentis P10/P90: robustos a valores extremos.

## Fração de interseção
f = A(talhão ∩ máscara) / A(talhão), 0 ≤ f ≤ 1.

## Climatologia e anomalia temporal
- clim(talhão, mês) = média das observações válidas desse mês do ano no período-base.
- anom = x − clim; z = anom / σ_clim(mês).

## Anomalia relativa
1. (opcional) xᵢ′(t) = xᵢ(t) − média_baseline(xᵢ).
2. ref(t) = mediana_i xᵢ′(t).
3. anom_rel_i(t) = xᵢ′(t) − ref(t).
4. (opcional) média móvel centrada de `window_days`.

## z-score robusto
MAD = mediana(|x − mediana(x)|); z_rob = (x − mediana)/(1,4826·MAD). O fator 1,4826 torna o MAD comparável ao desvio-padrão sob normalidade.

## Interpolação linear no tempo (limitada)
x(t) = x₀ + (x₁ − x₀)·(t − t₀)/(t₁ − t₀) entre observações válidas adjacentes; não aplicada se t₁ − t₀ > `max_gap_days`.

## Kruskal–Wallis
Teste não paramétrico de ranks entre k grupos: H = 12/(N(N+1)) Σ Rᵢ²/nᵢ − 3(N+1). Pressupõe independência; séries temporais violam isso (autocorrelação), logo o p-valor é apenas exploratório.
