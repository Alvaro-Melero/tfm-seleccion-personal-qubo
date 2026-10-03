"""Figura 2 de la memoria en dos paneles, a partir de resumen_perfiles_puesto.csv (semilla 42)."""
import csv
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RANGOS = {"x_ex_total": 15, "x_ex_stack": 10, "x_tech": 5, "x_test": 100, "x_senior": 5,
          "x_lead": 5, "x_cert": 10, "x_ingles": 5, "x_soft": 5, "x_salary": 10}
ETIQ = {"x_ex_total": "Experiencia\ntotal", "x_ex_stack": "Experiencia\nen el stack", "x_tech": "Nivel\ntécnico",
        "x_test": "Prueba\ntécnica", "x_senior": "Seniority", "x_lead": "Liderazgo", "x_cert": "Certificaciones",
        "x_ingles": "Inglés", "x_soft": "Habilidades\nblandas", "x_salary": "Desviación\nsalarial"}
PUESTOS = {"backend": "Backend (configuración validada)", "lider": "Líder técnico", "tecnico": "Especialista técnico"}
COLORES = ["#2b6cb0", "#dd6b20", "#2f855a"]
PANELES = [("a) Criterios que alcanzan su máximo en los tres puestos",
            ["x_ex_total", "x_test", "x_senior", "x_lead", "x_cert"]),
           ("b) Criterios en los que el perfil ideal cambia según el puesto",
            ["x_ex_stack", "x_tech", "x_ingles", "x_soft", "x_salary"])]

filas = {r["puesto"]: r for r in csv.DictReader(open(RAIZ / "datos" / "resumen_perfiles_puesto.csv", encoding="utf-8")) if r["seed"] == "42"}
plt.rcParams.update({"font.size": 14, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 1, figsize=(12, 9.5))
ancho = 0.26
for ax, (titulo, vars_) in zip(axes, PANELES):
    for i, (p, nombre) in enumerate(PUESTOS.items()):
        ax.bar([j + (i - 1) * ancho for j in range(len(vars_))],
               [float(filas[p][v]) / RANGOS[v] for v in vars_], ancho, color=COLORES[i],
               label=f"{nombre}: CV elegido {filas[p]['ganador']}")
    ax.set_xticks(range(len(vars_)), [ETIQ[v] for v in vars_], fontsize=14)
    ax.set_ylim(0, 1.1); ax.set_ylabel("Valor del perfil ideal\n(0 = mínimo, 1 = máximo)", fontsize=13.5)
    ax.set_title(titulo, fontsize=15.5, loc="left", pad=10)
    ax.grid(axis="y", alpha=0.3)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=2, fontsize=13, frameon=False)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(RAIZ / "figuras" / "F5_perfiles_por_puesto.png", dpi=200)
print("OK", {p: filas[p]["ganador"] for p in PUESTOS})
