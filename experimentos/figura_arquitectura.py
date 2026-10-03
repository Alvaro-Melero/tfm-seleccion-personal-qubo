"""Genera F1_arquitectura.png (Figura 1 de la memoria)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AZUL, NARANJA, VERDE, BORDE = "#e7eef8", "#fcf1e0", "#e4f2e8", "#4a4a4a"

fig, ax = plt.subplots(figsize=(13, 6.6))
ax.set_xlim(0, 13.4); ax.set_ylim(0, 6.6); ax.axis("off")


def caja(x, y, w, h, color, titulo, texto):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=color, ec=BORDE, lw=1.6))
    ax.text(x + w / 2, y + h - 0.45, titulo, ha="center", va="center", fontsize=17, weight="bold")
    ax.text(x + w / 2, y + (h - 0.6) / 2, texto, ha="center", va="center", fontsize=14.5, linespacing=1.5)


def flecha(puntos, etiqueta=None, pos=None):
    for (x0, y0), (x1, y1) in zip(puntos[:-2], puntos[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=BORDE, lw=2)
    ax.annotate("", xy=puntos[-1], xytext=puntos[-2],
                arrowprops=dict(arrowstyle="-|>", color=BORDE, lw=2, mutation_scale=22))
    if etiqueta:
        ax.text(*pos, etiqueta, ha="center", va="center", fontsize=14.5, style="italic")


caja(0.2, 3.7, 3.4, 2.6, AZUL, "Entradas del\nreclutador", "Puesto: pesos λ₁…λ₇\nRestricciones R1–R8")
caja(0.2, 0.3, 3.4, 2.6, AZUL, "Currículos (PDF)", "Extracción de los\n13 criterios")
caja(4.6, 2.6, 3.8, 3.7, NARANJA, "Núcleo de\noptimización", "Objetivo + penalizaciones\nCQM → QUBO (dimod)\nRecocido simulado (neal)")
caja(9.4, 2.6, 3.4, 3.7, VERDE, "Selección por\ndistancia", "Distancia de cada CV\nal perfil ideal\nRanking y desglose\npor criterio")

flecha([(3.6, 5.0), (4.6, 5.0)], "λ, R", (4.1, 5.35))
flecha([(8.4, 4.45), (9.4, 4.45)], "perfil\nideal", (8.9, 4.95))
# los CV van por debajo del núcleo, sin cruzarlo
flecha([(3.6, 1.6), (10.2, 1.6), (10.2, 2.6)], "vector de 13 criterios de cada CV", (6.9, 1.95))
ax.annotate("", xy=(11.95, 1.55), xytext=(11.95, 2.6),
            arrowprops=dict(arrowstyle="-|>", color="#1f6f3a", lw=2, mutation_scale=22))
ax.text(11.95, 1.05, "Candidato recomendado\ny explicación", ha="center", va="center",
        fontsize=15, weight="bold", color="#1f6f3a")

fig.tight_layout()
fig.savefig(Path(__file__).resolve().parent.parent / "figuras" / "F1_arquitectura.png", dpi=200)
print("OK -> F1_arquitectura.png")
