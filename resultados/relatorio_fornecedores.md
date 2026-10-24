# Relatório de Matriz de Decisão: Escolha de Fornecedor

## 1. Contexto da Decisão
- **Decisão:** Selecionar o melhor fornecedor entre 4 opções analisadas a partir de `dados/fornecedores.csv`.
- **Alternativas avaliadas:** Alfa, Beta, Gama e Delta.
- **Método utilizado:** Skill `decision-matrix` combinada com a skill `chart-image` para visualização com escalas explícitas e revisão visual.

## 2. Critérios de Avaliação e Pesos
| Critério | Coluna no CSV | Regra de Pontuação (1 a 10) | Peso (%) |
|---|---|---|---|
| **Preço Unitário** | `preco_unitario` | Menor é melhor: `10 × (Menor Preço / Preço)` | 30% |
| **Qualidade (Defeitos %)** | `defeitos_pct` | Menor é melhor: `10 × (Menor Defeito / Defeito)` | 30% |
| **Prazo de Entrega (dias)** | `prazo_dias` | Menor é melhor: `10 × (Menor Prazo / Prazo)` | 25% |
| **Nota de Suporte** | `suporte_nota` | Maior é melhor: nota direta na escala 1–10 | 15% |
| **Total** | — | — | **100%** |

## 3. Dados Originais dos Fornecedores
| Fornecedor | Preço Unitário (R$) | Prazo (dias) | Defeitos (%) | Suporte (Nota) |
|---|---:|---:|---:|---:|
| Alfa | 90.00 | 8 | 2.0% | 8.0 |
| Beta | 100.00 | 5 | 1.0% | 9.0 |
| Gama | 85.00 | 12 | 4.0% | 6.0 |
| Delta | 110.00 | 4 | 0.5% | 9.5 |

## 4. Resultados da Matriz de Decisão (Notas Brutas e Ponderadas)
| Posição | Fornecedor | Preço (30%) | Defeitos (30%) | Prazo (25%) | Suporte (15%) | **Total Ponderado** |
|:---:|---|---:|---:|---:|---:|---:|
| 1º | **Delta** | 7.73 (2.32) | 10.00 (3.00) | 10.00 (2.50) | 9.50 (1.43) | **9.24** |
| 2º | Beta | 8.50 (2.55) | 5.00 (1.50) | 8.00 (2.00) | 9.00 (1.35) | 7.40 |
| 3º | Alfa | 9.44 (2.83) | 2.50 (0.75) | 5.00 (1.25) | 8.00 (1.20) | 6.03 |
| 4º | Gama | 10.00 (3.00) | 1.25 (0.38) | 3.33 (0.83) | 6.00 (0.90) | 5.11 |

## 5. Análise de Sensibilidade
- **Margem do 1º para o 2º colocado:** `Delta` (9.24) venceu `Beta` (7.40) por uma margem de **24.91%**.
- **Nível de Confiança:** Alta (margem > 10%).

### Simulação em diferentes cenários de prioridade:
| Cenário | 1º Lugar | 2º Lugar | 3º Lugar | 4º Lugar |
|---|---|---|---|---|
| Matriz Principal (30/30/25/15) | **Delta** (9.24) | Beta (7.40) | Alfa (6.03) | Gama (5.11) |
| Pesos Iguais (25% cada) | **Delta** (9.31) | Beta (7.62) | Alfa (6.24) | Gama (5.15) |
| Foco em Custo (Preço 55%) | **Delta** (8.68) | Beta (7.98) | Alfa (7.52) | Gama (7.09) |
| Foco em Qualidade/Prazo | **Delta** (9.58) | Beta (7.02) | Alfa (5.12) | Gama (3.90) |

## 6. Recomendação Final e Trade-offs
- **Fornecedor Recomendado:** **Delta** (Pontuação Final: **9.24 / 10**)
- **Pontos Fortes do Vencedor:** Melhor prazo de entrega (4 dias), menor índice de defeitos (0.5%) e maior nota de suporte (9.5).
- **Trade-offs (Compensações):** O fornecedor `Delta` possui o maior preço unitário (R$ 110.00), enquanto `Gama` (R$ 85,00) e `Alfa` (R$ 90,00) têm preços menores, mas apresentam prazos mais longos e taxas de defeitos maiores.

## 7. Gráficos de Análise (Gerados com a Skill `chart-image`)
### 7.1 Ranking Ponderado e Notas Normalizadas por Critério
![Gráfico de Análise dos Fornecedores](grafico_fornecedores.png)

### 7.2 Comparação das Métricas Originais (Unidades Reais)
![Gráfico das Métricas Originais](grafico_metricas_originais.png)

### 7.3 Análise de Sensibilidade e Trade-off (Preço vs Desempenho)
![Gráfico de Sensibilidade e Trade-off](grafico_sensibilidade_fornecedores.png)
