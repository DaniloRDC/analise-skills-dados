# Relatório de Qualidade dos Dados (`conferir-csv`)

## 1. Identificação do Arquivo e Finalidade
- **Arquivo analisado:** `dados/fornecedores_erro.csv` (arquivo original mantido intacto).
- **Finalidade da análise:** Avaliação comparativa de fornecedores (Matriz de Decisão), onde cada linha representa um fornecedor avaliado em preço, prazo, taxa de defeitos e suporte.
- **Observação sobre predição (Item 7 da skill):** Esta base é de tomada de decisão multicritério (não possui coluna-alvo de Machine Learning, sendo `fornecedor` apenas o identificador da linha).

## 2. Estrutura Geral do CSV
- **Separador identificado:** `,` (vírgula)
- **Quantidade de linhas de dados:** `4` linhas (além de 1 linha de cabeçalho)
- **Quantidade de colunas:** `5` colunas (`fornecedor, preco_unitario, prazo_dias, defeitos_pct, suporte_nota`)
- **Linhas inteiras duplicadas:** `0`
- **Fornecedores repetidos:** `0`

## 3. Diagnóstico por Coluna
| Coluna | Tipo Esperado | Valores Válidos | Valores Ausentes (Vazios) | Texto Inválido em Coluna Numérica | Valores Fora de Sentido |
|---|---|---:|---:|---:|---:|
| `fornecedor` | Texto (identificador) | 4 | **0** | 0 | 0 |
| `preco_unitario` | Numérico (float/int) | 3 | **1** | 0 | 0 |
| `prazo_dias` | Numérico (float/int) | 4 | **0** | 0 | 0 |
| `defeitos_pct` | Numérico (float/int) | 4 | **0** | 0 | 0 |
| `suporte_nota` | Numérico (float/int) | 3 | **1** | 0 | 0 |

## 4. Problemas Encontrados e Evidências
Foram encontrados **2** problema(s) na base:
- **Valor ausente na coluna `preco_unitario`:** 1 ocorrência(s) — linha 5 (fornecedor `Delta`).
- **Valor ausente na coluna `suporte_nota`:** 1 ocorrência(s) — linha 3 (fornecedor `Beta`).

## 5. Tratamentos Propostos (Sem alterar o arquivo original)
1. **Solicitar a cotação/dado real faltante (Recomendado):** Como a base tem apenas 4 fornecedores, preencher um valor ausente com média ou zero distorceria a matriz de decisão (por exemplo, ausência em `preco_unitario` do fornecedor `Delta` impediria a divisão `Menor Preço / Preço`, e ausência em `suporte_nota` do fornecedor `Beta` zeraria injustamente sua nota de suporte).
2. **Conferência com a base íntegra (`dados/fornecedores.csv`):** Caso se trate de falha de exportação, recuperar os valores reais documentados (`Beta` com `suporte_nota = 9` e `Delta` com `preco_unitario = 110`) em um arquivo tratado separado em `resultados/`, mantendo `dados/fornecedores_erro.csv` inalterado.
3. **Exclusão temporária ou bloqueio de cálculo:** Não rodar a matriz de decisão diretamente sobre linhas incompletas antes do tratamento explícito.