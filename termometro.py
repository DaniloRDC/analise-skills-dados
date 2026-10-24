import os
import matplotlib.pyplot as plt

# Pontos conhecidos: (0, 4) e (100, 20)
x1, y1 = 0, 4
x2, y2 = 100, 20

# Cálculo de A (inclinação) e B (ponto onde corta o eixo Y) na equação y = ax + b
a = (y2 - y1) / (x2 - x1)
b = y1 - (a * x1)

# Cálculo do valor de y (corrente em mA) quando x = 50 graus
x = 50
y = (a * x) + b

# Exibindo os resultados na tela
print(f"Valor de A: {a}")
print(f"Valor de B: {b}")
print(f"Resultado de y (corrente) em x = {x} °C: {y} mA")

# Aviso caso a temperatura esteja fora de 0 a 100 °C
if x < 0 or x > 100:
    print("AVISO: A temperatura está fora da faixa de 0 a 100 °C!")

# Aviso quando a corrente estiver fora de 4 a 20 mA
if y < 4 or y > 20:
    print("AVISO: A corrente elétrica está fora da faixa de 4 a 20 mA!")

# Classificação da temperatura
if x <= 30:
    classificacao = "Baixa"
elif x <= 60:
    classificacao = "Média"
else:
    classificacao = "Alta"

print(f"Classificação da temperatura: {classificacao}")

# Criando o gráfico (Temperatura no eixo X e Corrente elétrica no eixo Y)
os.makedirs("resultados", exist_ok=True)

temperaturas = [x1, x, x2]
correntes = [y1, y, y2]

plt.figure(figsize=(8, 5))
plt.plot([x1, x2], [y1, y2], label="Reta do termômetro (y = ax + b)", color="blue")
plt.scatter(temperaturas, correntes, color="red", zorder=5, label="Pontos (0°C, 50°C, 100°C)")

plt.title("Corrente Elétrica vs Temperatura")
plt.xlabel("Temperatura (°C)")
plt.ylabel("Corrente Elétrica (mA)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()

caminho_grafico = "resultados/grafico_termometro.png"
plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
plt.close()
print(f"Gráfico salvo em: {caminho_grafico}")

