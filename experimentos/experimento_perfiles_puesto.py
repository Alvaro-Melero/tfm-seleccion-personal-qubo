"""Tres presets de puesto (mismas R1-R8, distinto lambda del objetivo) x 5 semillas.
Genera F5_perfiles_por_puesto.png y resumen_perfiles_puesto.csv."""
import csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import app_demo

SEEDS = [1, 7, 42, 123, 2024]
VARS = ["x_ex_total", "x_ex_stack", "x_tech", "x_test", "x_senior", "x_lead", "x_cert", "x_ingles", "x_soft", "x_salary"]
filas = app_demo.cvs_de_ejemplo()
res = {}
with open("resumen_perfiles_puesto.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["puesto", "seed", "restricciones_ok", "ganador", "distancia", "segundo"] + VARS)
    for p in app_demo.PUESTOS:
        for s in SEEDS:
            ideal, restr, rank, _ = app_demo.ejecutar(filas, p, 5000, s)
            w.writerow([p, s, sum(restr.values()), rank[0][0], round(rank[0][1], 3), rank[1][0]] + [ideal[v] for v in VARS])
            res.setdefault(p, []).append((ideal, restr, rank))
        print(p, [(sum(r.values()), k[0][0]) for _, r, k in res[p]])

fig, ax = plt.subplots(figsize=(10, 4.2))
ancho = 0.26
for i, (p, (nombre, *_)) in enumerate(app_demo.PUESTOS.items()):
    ideal = res[p][2][0]  # semilla 42, la de la configuracion reportada
    ax.bar([j + (i - 1) * ancho for j in range(len(VARS))],
           [ideal[v] / app_demo.RANGOS[v] for v in VARS], ancho, label=f"{nombre} → {res[p][2][2][0][0]}")
ax.set_xticks(range(len(VARS))); ax.set_xticklabels([app_demo.ETIQUETAS[v] for v in VARS], rotation=30, ha="right")
ax.set_ylabel("Valor del perfil ideal (normalizado 0–1)"); ax.set_ylim(0, 1.45); ax.legend(title="Puesto → CV seleccionado (semilla 42)", fontsize=8.5, ncol=3, loc="upper center")
ax.set_title("Perfil ideal según el énfasis del puesto (λ del objetivo), mismas restricciones R1–R8")
fig.tight_layout(); fig.savefig("F5_perfiles_por_puesto.png", dpi=160)
