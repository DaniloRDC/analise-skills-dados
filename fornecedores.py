import csv
import os
import matplotlib.pyplot as plt

# 1. Leitura dos dados originais (sem alterar dados/fornecedores.csv)
caminho_entrada = "dados/fornecedores.csv"
fornecedores = []

with open(caminho_entrada, mode="r", encoding="utf-8") as arquivo:
    leitor = csv.DictReader(arquivo)
    for linha in leitor:
        fornecedores.append({
            "fornecedor": linha["fornecedor"],
            "preco_unitario": float(linha["preco_unitario"]),
            "prazo_dias": float(linha["prazo_dias"]),
            "defeitos_pct": float(linha["defeitos_pct"]),
            "suporte_nota": float(linha["suporte_nota"]),
        })

# 2. Definição dos critérios e pesos (somando 100% conforme a skill decision-matrix)
pesos = {
    "preco": 0.30,
    "defeitos": 0.30,
    "prazo": 0.25,
    "suporte": 0.15,
}

# 3. Conversão dos dados objetivos para escala de 1 a 10 (10 = melhor desempenho)
melhor_preco = min(f["preco_unitario"] for f in fornecedores)
melhor_prazo = min(f["prazo_dias"] for f in fornecedores)
melhor_defeito = min(f["defeitos_pct"] for f in fornecedores)
melhor_suporte = max(f["suporte_nota"] for f in fornecedores)

for f in fornecedores:
    f["nota_preco"] = 10.0 * (melhor_preco / f["preco_unitario"])
    f["nota_prazo"] = 10.0 * (melhor_prazo / f["prazo_dias"])
    f["nota_defeitos"] = 10.0 * (melhor_defeito / f["defeitos_pct"])
    f["nota_suporte"] = f["suporte_nota"]

    # Cálculo das notas ponderadas (Nota * Peso)
    f["pond_preco"] = f["nota_preco"] * pesos["preco"]
    f["pond_prazo"] = f["nota_prazo"] * pesos["prazo"]
    f["pond_defeitos"] = f["nota_defeitos"] * pesos["defeitos"]
    f["pond_suporte"] = f["nota_suporte"] * pesos["suporte"]

    # Nota final ponderada
    f["nota_final"] = (
        f["pond_preco"]
        + f["pond_prazo"]
        + f["pond_defeitos"]
        + f["pond_suporte"]
    )

# 4. Ordenação do ranking (do maior para o menor)
ranking = sorted(fornecedores, key=lambda x: x["nota_final"], reverse=True)
for indice, f in enumerate(ranking, start=1):
    f["posicao"] = indice

vencedor = ranking[0]
segundo = ranking[1]
margem_pct = ((vencedor["nota_final"] - segundo["nota_final"]) / segundo["nota_final"]) * 100.0

# 5. Análise de Sensibilidade (testando diferentes cenários de pesos)
cenarios_sensibilidade = {
    "Matriz Principal (30/30/25/15)": pesos,
    "Pesos Iguais (25% cada)": {"preco": 0.25, "defeitos": 0.25, "prazo": 0.25, "suporte": 0.25},
    "Foco em Custo (Preço 55%)": {"preco": 0.55, "defeitos": 0.15, "prazo": 0.15, "suporte": 0.15},
    "Foco em Qualidade/Prazo": {"preco": 0.15, "defeitos": 0.40, "prazo": 0.30, "suporte": 0.15},
}

resultados_sensibilidade = {}
notas_por_cenario = { nome: {} for nome in cenarios_sensibilidade }

for nome_cenario, p in cenarios_sensibilidade.items():
    totais = []
    for f in fornecedores:
        total_cenario = (
            f["nota_preco"] * p["preco"]
            + f["nota_defeitos"] * p["defeitos"]
            + f["nota_prazo"] * p["prazo"]
            + f["nota_suporte"] * p["suporte"]
        )
        totais.append((f["fornecedor"], total_cenario))
        notas_por_cenario[nome_cenario][f["fornecedor"]] = total_cenario
    totais.sort(key=lambda item: item[1], reverse=True)
    resultados_sensibilidade[nome_cenario] = totais

# 6. Criação da pasta resultados/
os.makedirs("resultados", exist_ok=True)

# Paleta de cores acessível e com alto contraste (seguindo a skill chart-image)
COR_PRECO = "#1f77b4"     # Azul
COR_DEFEITOS = "#2ca02c"  # Verde
COR_PRAZO = "#ff7f0e"     # Laranja
COR_SUPORTE = "#9467bd"   # Roxo
COR_DESTAQUE = "#1b7837"  # Verde escuro para o melhor valor
COR_PADRAO = "#4a6fe3"    # Azul médio para os demais

# ==============================================================================
# GRÁFICO 1 (MELHORADO): resultados/grafico_fornecedores.png
# Seguindo chart-image: sem sobreposição de legendas, escalas explícitas a partir
# do zero, rótulos de dados claros, unidades nos eixos e fonte dos dados.
# ==============================================================================
nomes_ord = [f["fornecedor"] for f in ranking]
notas_finais = [f["nota_final"] for f in ranking]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.8))

# Painel 1: Nota Final Ponderada (Empilhada por critério)
p_preco = [f["pond_preco"] for f in ranking]
p_defeitos = [f["pond_defeitos"] for f in ranking]
p_prazo = [f["pond_prazo"] for f in ranking]
p_suporte = [f["pond_suporte"] for f in ranking]

ax1.bar(nomes_ord, p_preco, width=0.55, label="Preço Unitário (peso 30%)", color=COR_PRECO)
ax1.bar(nomes_ord, p_defeitos, width=0.55, bottom=p_preco, label="Baixo Índice de Defeitos (peso 30%)", color=COR_DEFEITOS)
base_prazo = [p_preco[i] + p_defeitos[i] for i in range(len(ranking))]
ax1.bar(nomes_ord, p_prazo, width=0.55, bottom=base_prazo, label="Prazo de Entrega (peso 25%)", color=COR_PRAZO)
base_suporte = [base_prazo[i] + p_prazo[i] for i in range(len(ranking))]
ax1.bar(nomes_ord, p_suporte, width=0.55, bottom=base_suporte, label="Nota de Suporte (peso 15%)", color=COR_SUPORTE)

for i, total in enumerate(notas_finais):
    ax1.text(i, total + 0.2, f"{total:.2f} pts", ha="center", va="bottom", fontweight="bold", fontsize=10)

ax1.set_title("1. Pontuação Final Ponderada (Ranking Geral)", fontsize=12, fontweight="bold", pad=12)
ax1.set_xlabel("Fornecedor (ordenado por ranking)", fontsize=10)
ax1.set_ylabel("Pontuação Ponderada Acumulada (escala 0 a 10 pontos)", fontsize=10)
ax1.set_ylim(0, 11.8)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.95, fontsize=9)

# Painel 2: Comparação das Notas (1 a 10) em cada Critério (sem sobrepor legenda!)
x_indices = list(range(len(fornecedores)))
largura = 0.19
nomes_orig = [f["fornecedor"] for f in fornecedores]

b1 = ax2.bar([x - 1.5 * largura for x in x_indices], [f["nota_preco"] for f in fornecedores], width=largura, label="Nota Preço", color=COR_PRECO)
b2 = ax2.bar([x - 0.5 * largura for x in x_indices], [f["nota_defeitos"] for f in fornecedores], width=largura, label="Nota Defeitos", color=COR_DEFEITOS)
b3 = ax2.bar([x + 0.5 * largura for x in x_indices], [f["nota_prazo"] for f in fornecedores], width=largura, label="Nota Prazo", color=COR_PRAZO)
b4 = ax2.bar([x + 1.5 * largura for x in x_indices], [f["nota_suporte"] for f in fornecedores], width=largura, label="Nota Suporte", color=COR_SUPORTE)

for barras in (b1, b2, b3, b4):
    for barra in barras:
        altura = barra.get_height()
        ax2.text(
            barra.get_x() + barra.get_width() / 2.0,
            altura + 0.15,
            f"{altura:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

ax2.set_title("2. Notas Normalizadas por Critério (10 = Melhor Desempenho)", fontsize=12, fontweight="bold", pad=12)
ax2.set_xlabel("Fornecedor", fontsize=10)
ax2.set_ylabel("Nota Padronizada no Critério (escala 0 a 10)", fontsize=10)
ax2.set_xticks(x_indices)
ax2.set_xticklabels(nomes_orig)
ax2.set_ylim(0, 12.2)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
ax2.legend(loc="upper center", ncol=4, frameon=True, facecolor="white", framealpha=0.95, fontsize=9)

plt.suptitle("Matriz de Decisão: Avaliação Comparativa dos 4 Fornecedores", fontsize=14, fontweight="bold", y=0.98)
fig.text(
    0.5, 0.01,
    "Fonte: dados/fornecedores.csv | Escalas iniciadas em 0 (sem truncamento) | Pesos: Preço 30%, Defeitos 30%, Prazo 25%, Suporte 15%",
    ha="center", fontsize=9, style="italic", color="#444444"
)
plt.tight_layout(rect=[0, 0.04, 1, 0.94])

caminho_grafico_1 = "resultados/grafico_fornecedores.png"
plt.savefig(caminho_grafico_1, dpi=150, bbox_inches="tight")
plt.close()

# ==============================================================================
# GRÁFICO 2 (NOVO): resultados/grafico_metricas_originais.png
# Painel 2x2 com as métricas originais de cada fornecedor e unidades explícitas,
# destacando em verde o melhor fornecedor de cada indicador.
# ==============================================================================
fig, eixos = plt.subplots(2, 2, figsize=(14, 9))
(ax_preco, ax_prazo), (ax_defeitos, ax_suporte) = eixos

nomes = [f["fornecedor"] for f in fornecedores]
precos = [f["preco_unitario"] for f in fornecedores]
prazos = [f["prazo_dias"] for f in fornecedores]
defeitos = [f["defeitos_pct"] for f in fornecedores]
suportes = [f["suporte_nota"] for f in fornecedores]

# Subgráfico A: Preço Unitário (R$ - menor é melhor)
cores_preco = [COR_DESTAQUE if v == melhor_preco else COR_PADRAO for v in precos]
barras_p = ax_preco.bar(nomes, precos, color=cores_preco, width=0.5)
for b in barras_p:
    h = b.get_height()
    ax_preco.text(b.get_x() + b.get_width() / 2, h + 2, f"R$ {h:.0f}", ha="center", va="bottom", fontweight="bold", fontsize=9)
ax_preco.set_title("A. Preço Unitário (R$) — Menor é Melhor", fontweight="bold")
ax_preco.set_xlabel("Fornecedor")
ax_preco.set_ylabel("Preço Unitário (R$)")
ax_preco.set_ylim(0, max(precos) * 1.18)
ax_preco.grid(axis="y", linestyle="--", alpha=0.5)

# Subgráfico B: Prazo de Entrega (dias - menor é melhor)
cores_prazo = [COR_DESTAQUE if v == melhor_prazo else COR_PADRAO for v in prazos]
barras_pr = ax_prazo.bar(nomes, prazos, color=cores_prazo, width=0.5)
for b in barras_pr:
    h = b.get_height()
    ax_prazo.text(b.get_x() + b.get_width() / 2, h + 0.3, f"{h:.0f} dias", ha="center", va="bottom", fontweight="bold", fontsize=9)
ax_prazo.set_title("B. Prazo de Entrega (dias) — Menor é Melhor", fontweight="bold")
ax_prazo.set_xlabel("Fornecedor")
ax_prazo.set_ylabel("Prazo (dias corridos)")
ax_prazo.set_ylim(0, max(prazos) * 1.22)
ax_prazo.grid(axis="y", linestyle="--", alpha=0.5)

# Subgráfico C: Taxa de Defeitos (% - menor é melhor)
cores_def = [COR_DESTAQUE if v == melhor_defeito else COR_PADRAO for v in defeitos]
barras_d = ax_defeitos.bar(nomes, defeitos, color=cores_def, width=0.5)
for b in barras_d:
    h = b.get_height()
    ax_defeitos.text(b.get_x() + b.get_width() / 2, h + 0.1, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold", fontsize=9)
ax_defeitos.set_title("C. Taxa de Defeitos (%) — Menor é Melhor", fontweight="bold")
ax_defeitos.set_xlabel("Fornecedor")
ax_defeitos.set_ylabel(" Peças com Defeito (%)")
ax_defeitos.set_ylim(0, max(defeitos) * 1.25)
ax_defeitos.grid(axis="y", linestyle="--", alpha=0.5)

# Subgráfico D: Nota de Suporte (0 a 10 - maior é melhor)
cores_sup = [COR_DESTAQUE if v == melhor_suporte else COR_PADRAO for v in suportes]
barras_s = ax_suporte.bar(nomes, suportes, color=cores_sup, width=0.5)
for b in barras_s:
    h = b.get_height()
    ax_suporte.text(b.get_x() + b.get_width() / 2, h + 0.2, f"{h:.1f} / 10", ha="center", va="bottom", fontweight="bold", fontsize=9)
ax_suporte.set_title("D. Avaliação de Suporte (0 a 10) — Maior é Melhor", fontweight="bold")
ax_suporte.set_xlabel("Fornecedor")
ax_suporte.set_ylabel("Nota de Suporte (escala 0 a 10)")
ax_suporte.set_ylim(0, 11.5)
ax_suporte.grid(axis="y", linestyle="--", alpha=0.5)

plt.suptitle("Indicadores Originais por Fornecedor (Destaque em Verde = Melhor no Critério)", fontsize=14, fontweight="bold", y=0.98)
fig.text(
    0.5, 0.01,
    "Fonte: dados/fornecedores.csv | Barras verdes indicam o fornecedor líder em cada métrica individual.",
    ha="center", fontsize=9, style="italic", color="#444444"
)
plt.tight_layout(rect=[0, 0.03, 1, 0.94])

caminho_grafico_2 = "resultados/grafico_metricas_originais.png"
plt.savefig(caminho_grafico_2, dpi=150, bbox_inches="tight")
plt.close()

# ==============================================================================
# GRÁFICO 3 (NOVO): resultados/grafico_sensibilidade_fornecedores.png
# Painel 1: Análise de Sensibilidade entre cenários de pesos
# Painel 2: Gráfico de Trade-off (Preço Unitário R$ vs Pontuação Final Ponderada)
# ==============================================================================
fig, (ax_sens, ax_trade) = plt.subplots(1, 2, figsize=(15, 6.5))

# Painel 1: Sensibilidade por Cenário
nomes_cenarios = list(cenarios_sensibilidade.keys())
x_cen = list(range(len(nomes_cenarios)))
larg = 0.18
cores_forn = {"Delta": "#1b7837", "Beta": "#1f77b4", "Alfa": "#ff7f0e", "Gama": "#d62728"}

for idx_f, nome_f in enumerate(["Delta", "Beta", "Alfa", "Gama"]):
    valores_f = [notas_por_cenario[c][nome_f] for c in nomes_cenarios]
    deslocamento = (idx_f - 1.5) * larg
    barras_c = ax_sens.bar([x + deslocamento for x in x_cen], valores_f, width=larg, label=nome_f, color=cores_forn[nome_f])
    for b in barras_c:
        h = b.get_height()
        ax_sens.text(b.get_x() + b.get_width() / 2, h + 0.15, f"{h:.1f}", ha="center", va="bottom", fontsize=8)

ax_sens.set_title("1. Análise de Sensibilidade: Nota Final em Diferentes Cenários", fontsize=12, fontweight="bold", pad=12)
ax_sens.set_xlabel("Cenário de Pesos Avaliado", fontsize=10)
ax_sens.set_ylabel("Pontuação Final Ponderada (0 a 10)", fontsize=10)
ax_sens.set_xticks(x_cen)
ax_sens.set_xticklabels(nomes_cenarios, rotation=12, ha="right", fontsize=9)
ax_sens.set_ylim(0, 11.8)
ax_sens.grid(axis="y", linestyle="--", alpha=0.5)
ax_sens.legend(title="Fornecedor", loc="upper right", frameon=True, facecolor="white")

# Painel 2: Trade-off Custo (Preço Unitário R$) vs Benefício (Nota Final Ponderada)
for f in fornecedores:
    nome_f = f["fornecedor"]
    px = f["preco_unitario"]
    py = f["nota_final"]
    ax_trade.scatter(px, py, s=160, color=cores_forn[nome_f], zorder=5, label=f"{nome_f} (R$ {px:.0f} | {py:.2f} pts)")
    ax_trade.annotate(
        f"{nome_f}\n(R$ {px:.0f}, {py:.2f} pts)",
        (px, py),
        textcoords="offset points",
        xytext=(0, 12),
        ha="center",
        fontsize=9,
        fontweight="bold",
    )

ax_trade.set_title("2. Análise de Trade-off: Preço Unitário (R$) vs Pontuação Final", fontsize=12, fontweight="bold", pad=12)
ax_trade.set_xlabel("Preço Unitário (R$) — Menor para a esquerda", fontsize=10)
ax_trade.set_ylabel("Pontuação Final Ponderada (escala 0 a 10) — Maior para cima", fontsize=10)
ax_trade.set_xlim(78, 118)
ax_trade.set_ylim(0, 11.5)
ax_trade.grid(True, linestyle="--", alpha=0.5)
ax_trade.legend(loc="lower right", frameon=True, facecolor="white", fontsize=9)

plt.suptitle("Robustez da Decisão (Sensibilidade) e Relação Custo × Desempenho", fontsize=14, fontweight="bold", y=0.98)
fig.text(
    0.5, 0.01,
    "Fonte: dados/fornecedores.csv | Nota: Eixo X do gráfico 2 recortado na faixa de R$ 78 a R$ 118 para visualização de dispersão; Eixo Y inicia em 0.",
    ha="center", fontsize=9, style="italic", color="#444444"
)
plt.tight_layout(rect=[0, 0.04, 1, 0.94])

caminho_grafico_3 = "resultados/grafico_sensibilidade_fornecedores.png"
plt.savefig(caminho_grafico_3, dpi=150, bbox_inches="tight")
plt.close()

# ==============================================================================
# 8. Atualização do Relatório em Markdown (resultados/relatorio_fornecedores.md)
# ==============================================================================
confianca = "Alta (margem > 10%)" if margem_pct > 10 else ("Moderada (margem entre 5% e 10%)" if margem_pct >= 5 else "Baixa (margem < 5%, disputa acirrada)")

linhas_md = [
    "# Relatório de Matriz de Decisão: Escolha de Fornecedor\n",
    "## 1. Contexto da Decisão",
    "- **Decisão:** Selecionar o melhor fornecedor entre 4 opções analisadas a partir de `dados/fornecedores.csv`.",
    "- **Alternativas avaliadas:** Alfa, Beta, Gama e Delta.",
    "- **Método utilizado:** Skill `decision-matrix` combinada com a skill `chart-image` para visualização com escalas explícitas e revisão visual.\n",
    "## 2. Critérios de Avaliação e Pesos",
    "| Critério | Coluna no CSV | Regra de Pontuação (1 a 10) | Peso (%) |",
    "|---|---|---|---|",
    f"| **Preço Unitário** | `preco_unitario` | Menor é melhor: `10 × (Menor Preço / Preço)` | {int(pesos['preco']*100)}% |",
    f"| **Qualidade (Defeitos %)** | `defeitos_pct` | Menor é melhor: `10 × (Menor Defeito / Defeito)` | {int(pesos['defeitos']*100)}% |",
    f"| **Prazo de Entrega (dias)** | `prazo_dias` | Menor é melhor: `10 × (Menor Prazo / Prazo)` | {int(pesos['prazo']*100)}% |",
    f"| **Nota de Suporte** | `suporte_nota` | Maior é melhor: nota direta na escala 1–10 | {int(pesos['suporte']*100)}% |",
    "| **Total** | — | — | **100%** |\n",
    "## 3. Dados Originais dos Fornecedores",
    "| Fornecedor | Preço Unitário (R$) | Prazo (dias) | Defeitos (%) | Suporte (Nota) |",
    "|---|---:|---:|---:|---:|",
]

for f in fornecedores:
    linhas_md.append(
        f"| {f['fornecedor']} | {f['preco_unitario']:.2f} | {f['prazo_dias']:.0f} | {f['defeitos_pct']:.1f}% | {f['suporte_nota']:.1f} |"
    )

linhas_md.extend([
    "\n## 4. Resultados da Matriz de Decisão (Notas Brutas e Ponderadas)",
    f"| Posição | Fornecedor | Preço ({int(pesos['preco']*100)}%) | Defeitos ({int(pesos['defeitos']*100)}%) | Prazo ({int(pesos['prazo']*100)}%) | Suporte ({int(pesos['suporte']*100)}%) | **Total Ponderado** |",
    "|:---:|---|---:|---:|---:|---:|---:|",
])

for f in ranking:
    destaque = "**" if f["posicao"] == 1 else ""
    linhas_md.append(
        f"| {f['posicao']}º | {destaque}{f['fornecedor']}{destaque} | "
        f"{f['nota_preco']:.2f} ({f['pond_preco']:.2f}) | "
        f"{f['nota_defeitos']:.2f} ({f['pond_defeitos']:.2f}) | "
        f"{f['nota_prazo']:.2f} ({f['pond_prazo']:.2f}) | "
        f"{f['nota_suporte']:.2f} ({f['pond_suporte']:.2f}) | "
        f"{destaque}{f['nota_final']:.2f}{destaque} |"
    )

linhas_md.extend([
    "\n## 5. Análise de Sensibilidade",
    f"- **Margem do 1º para o 2º colocado:** `{vencedor['fornecedor']}` ({vencedor['nota_final']:.2f}) venceu `{segundo['fornecedor']}` ({segundo['nota_final']:.2f}) por uma margem de **{margem_pct:.2f}%**.",
    f"- **Nível de Confiança:** {confianca}.",
    "\n### Simulação em diferentes cenários de prioridade:",
    "| Cenário | 1º Lugar | 2º Lugar | 3º Lugar | 4º Lugar |",
    "|---|---|---|---|---|",
])

for nome_cenario, lista_totais in resultados_sensibilidade.items():
    colunas = [f"**{item[0]}** ({item[1]:.2f})" if i == 0 else f"{item[0]} ({item[1]:.2f})" for i, item in enumerate(lista_totais)]
    linhas_md.append(f"| {nome_cenario} | {colunas[0]} | {colunas[1]} | {colunas[2]} | {colunas[3]} |")

linhas_md.extend([
    "\n## 6. Recomendação Final e Trade-offs",
    f"- **Fornecedor Recomendado:** **{vencedor['fornecedor']}** (Pontuação Final: **{vencedor['nota_final']:.2f} / 10**)",
    f"- **Pontos Fortes do Vencedor:** Melhor prazo de entrega ({vencedor['prazo_dias']:.0f} dias), menor índice de defeitos ({vencedor['defeitos_pct']:.1f}%) e maior nota de suporte ({vencedor['suporte_nota']:.1f}).",
    f"- **Trade-offs (Compensações):** O fornecedor `{vencedor['fornecedor']}` possui o maior preço unitário (R$ {vencedor['preco_unitario']:.2f}), enquanto `Gama` (R$ 85,00) e `Alfa` (R$ 90,00) têm preços menores, mas apresentam prazos mais longos e taxas de defeitos maiores.",
    "\n## 7. Gráficos de Análise (Gerados com a Skill `chart-image`)",
    "### 7.1 Ranking Ponderado e Notas Normalizadas por Critério",
    "![Gráfico de Análise dos Fornecedores](grafico_fornecedores.png)\n",
    "### 7.2 Comparação das Métricas Originais (Unidades Reais)",
    "![Gráfico das Métricas Originais](grafico_metricas_originais.png)\n",
    "### 7.3 Análise de Sensibilidade e Trade-off (Preço vs Desempenho)",
    "![Gráfico de Sensibilidade e Trade-off](grafico_sensibilidade_fornecedores.png)\n",
])

caminho_relatorio = "resultados/relatorio_fornecedores.md"
with open(caminho_relatorio, mode="w", encoding="utf-8") as arq_md:
    arq_md.write("\n".join(linhas_md))

print(f"Melhor fornecedor: {vencedor['fornecedor']} (Nota final: {vencedor['nota_final']:.2f})")
print(f"Relatório atualizado em: {caminho_relatorio}")
print(f"Gráfico 1 (melhorado) salvo em: {caminho_grafico_1}")
print(f"Gráfico 2 (métricas originais) salvo em: {caminho_grafico_2}")
print(f"Gráfico 3 (sensibilidade e trade-off) salvo em: {caminho_grafico_3}")
