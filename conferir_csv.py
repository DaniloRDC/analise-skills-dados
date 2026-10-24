import csv
import os

caminho_csv = "dados/fornecedores_erro.csv"
caminho_saida = "resultados/qualidade.md"

# 1. Descobrir o separador e ler todas as linhas brutas (sem alterar o arquivo original)
with open(caminho_csv, mode="r", encoding="utf-8") as f:
    conteudo = f.read()

linhas_brutas = [linha for linha in conteudo.splitlines() if linha != ""]
separador = "," if "," in linhas_brutas[0] else ";"

with open(caminho_csv, mode="r", encoding="utf-8", newline="") as f:
    leitor = list(csv.reader(f, delimiter=separador))

cabecalho = leitor[0]
linhas_dados = leitor[1:]

num_linhas = len(linhas_dados)
num_colunas = len(cabecalho)

# 2. Contagem de linhas duplicadas e duplicidade de identificadores (fornecedor)
tuplas_linhas = [tuple(l) for l in linhas_dados]
linhas_duplicadas = num_linhas - len(set(tuplas_linhas))

nomes_fornecedores = [l[0].strip() for l in linhas_dados if len(l) > 0 and l[0].strip() != ""]
fornecedores_duplicados = len(nomes_fornecedores) - len(set(nomes_fornecedores))

# 3. Verificação por coluna: tipos esperados, valores ausentes (vazios ou só espaços),
#    números guardados como texto inválido e valores fora de sentido (ex: negativos, nota > 10)
colunas_numericas = ["preco_unitario", "prazo_dias", "defeitos_pct", "suporte_nota"]

resumo_colunas = []
problemas_detalhados = []

for idx_col, nome_col in enumerate(cabecalho):
    ausentes = 0
    invalidos_texto = 0
    fora_de_sentido = 0
    valores_validos = []
    linhas_com_ausencia = []
    linhas_com_erro_tipo = []
    linhas_fora_sentido = []

    esperado = "Numérico (float/int)" if nome_col in colunas_numericas else "Texto (identificador)"

    for idx_linha, linha in enumerate(linhas_dados, start=2):  # Linha 2 em diante no arquivo CSV
        valor_bruto = linha[idx_col] if idx_col < len(linha) else ""
        valor_limpo = valor_bruto.strip()

        fornecedor_linha = linha[0].strip() if len(linha) > 0 and linha[0].strip() else f"Linha {idx_linha}"

        # Regra 4 da skill: textos vazios ou só com espaços contam como ausência (diferente de zero)
        if valor_limpo == "":
            ausentes += 1
            linhas_com_ausencia.append(f"linha {idx_linha} (fornecedor `{fornecedor_linha}`)")
            continue

        if nome_col in colunas_numericas:
            try:
                num = float(valor_limpo)
                valores_validos.append(num)
                # Regra 5: procurar valores que não fazem sentido para a coluna
                if nome_col in ("preco_unitario", "prazo_dias") and num <= 0:
                    fora_de_sentido += 1
                    linhas_fora_sentido.append(f"linha {idx_linha} (`{fornecedor_linha}` = {num})")
                elif nome_col == "defeitos_pct" and (num < 0 or num > 100):
                    fora_de_sentido += 1
                    linhas_fora_sentido.append(f"linha {idx_linha} (`{fornecedor_linha}` = {num}%)")
                elif nome_col == "suporte_nota" and (num < 0 or num > 10):
                    fora_de_sentido += 1
                    linhas_fora_sentido.append(f"linha {idx_linha} (`{fornecedor_linha}` = {num})")
            except ValueError:
                invalidos_texto += 1
                linhas_com_erro_tipo.append(f"linha {idx_linha} (`{fornecedor_linha}` = '{valor_bruto}')")
        else:
            valores_validos.append(valor_limpo)

    resumo_colunas.append({
        "coluna": nome_col,
        "tipo_esperado": esperado,
        "preenchidos": len(valores_validos),
        "ausentes": ausentes,
        "invalidos_texto": invalidos_texto,
        "fora_de_sentido": fora_de_sentido,
    })

    if ausentes > 0:
        problemas_detalhados.append(
            f"- **Valor ausente na coluna `{nome_col}`:** {ausentes} ocorrência(s) — {', '.join(linhas_com_ausencia)}."
        )
    if invalidos_texto > 0:
        problemas_detalhados.append(
            f"- **Número guardado como texto inválido na coluna `{nome_col}`:** {invalidos_texto} ocorrência(s) — {', '.join(linhas_com_erro_tipo)}."
        )
    if fora_de_sentido > 0:
        problemas_detalhados.append(
            f"- **Valor fora de sentido na coluna `{nome_col}`:** {fora_de_sentido} ocorrência(s) — {', '.join(linhas_fora_sentido)}."
        )

total_ausentes = sum(c["ausentes"] for c in resumo_colunas)
total_invalidos = sum(c["invalidos_texto"] for c in resumo_colunas)
total_fora_sentido = sum(c["fora_de_sentido"] for c in resumo_colunas)

# 4. Salvar o relatório em resultados/qualidade.md conforme exige a skill conferir-csv
os.makedirs("resultados", exist_ok=True)

linhas_md = [
    "# Relatório de Qualidade dos Dados (`conferir-csv`)\n",
    "## 1. Identificação do Arquivo e Finalidade",
    f"- **Arquivo analisado:** `{caminho_csv}` (arquivo original mantido intacto).",
    "- **Finalidade da análise:** Avaliação comparativa de fornecedores (Matriz de Decisão), onde cada linha representa um fornecedor avaliado em preço, prazo, taxa de defeitos e suporte.",
    "- **Observação sobre predição (Item 7 da skill):** Esta base é de tomada de decisão multicritério (não possui coluna-alvo de Machine Learning, sendo `fornecedor` apenas o identificador da linha).\n",
    "## 2. Estrutura Geral do CSV",
    f"- **Separador identificado:** `{separador}` (vírgula)",
    f"- **Quantidade de linhas de dados:** `{num_linhas}` linhas (além de 1 linha de cabeçalho)",
    f"- **Quantidade de colunas:** `{num_colunas}` colunas (`{', '.join(cabecalho)}`)",
    f"- **Linhas inteiras duplicadas:** `{linhas_duplicadas}`",
    f"- **Fornecedores repetidos:** `{fornecedores_duplicados}`\n",
    "## 3. Diagnóstico por Coluna",
    "| Coluna | Tipo Esperado | Valores Válidos | Valores Ausentes (Vazios) | Texto Inválido em Coluna Numérica | Valores Fora de Sentido |",
    "|---|---|---:|---:|---:|---:|",
]

for c in resumo_colunas:
    linhas_md.append(
        f"| `{c['coluna']}` | {c['tipo_esperado']} | {c['preenchidos']} | **{c['ausentes']}** | {c['invalidos_texto']} | {c['fora_de_sentido']} |"
    )

linhas_md.append("\n## 4. Problemas Encontrados e Evidências")
if problemas_detalhados:
    linhas_md.append(f"Foram encontrados **{total_ausentes + total_invalidos + total_fora_sentido}** problema(s) na base:")
    linhas_md.extend(problemas_detalhados)
else:
    linhas_md.append("- Nenhum problema encontrado.")

linhas_md.extend([
    "\n## 5. Tratamentos Propostos (Sem alterar o arquivo original)",
    "1. **Solicitar a cotação/dado real faltante (Recomendado):** Como a base tem apenas 4 fornecedores, preencher um valor ausente com média ou zero distorceria a matriz de decisão (por exemplo, ausência em `preco_unitario` do fornecedor `Delta` impediria a divisão `Menor Preço / Preço`, e ausência em `suporte_nota` do fornecedor `Beta` zeraria injustamente sua nota de suporte).",
    "2. **Conferência com a base íntegra (`dados/fornecedores.csv`):** Caso se trate de falha de exportação, recuperar os valores reais documentados (`Beta` com `suporte_nota = 9` e `Delta` com `preco_unitario = 110`) em um arquivo tratado separado em `resultados/`, mantendo `dados/fornecedores_erro.csv` inalterado.",
    "3. **Exclusão temporária ou bloqueio de cálculo:** Não rodar a matriz de decisão diretamente sobre linhas incompletas antes do tratamento explícito.",
])

with open(caminho_saida, mode="w", encoding="utf-8") as arq_saida:
    arq_saida.write("\n".join(linhas_md))

print(f"Linhas de dados: {num_linhas} | Colunas: {num_colunas}")
print(f"Linhas duplicadas: {linhas_duplicadas}")
print(f"Total de valores ausentes: {total_ausentes}")
print(f"Total de erros de tipo: {total_invalidos} | Fora de sentido: {total_fora_sentido}")
for p in problemas_detalhados:
    print(p)
print(f"Resumo salvo em: {caminho_saida}")

