"""
Experimento correcto para la hipotesis: variar el NUMERO de pares de
criterios que interactuan (no el peso de un par fijo), y medir si el
ranking (QUBO-ideal + distancia) diverge del baseline lineal a medida
que crecen los pares interactuantes.

Interacciones originales del asesor (siempre activas): x_ex_total*x_cert,
x_senior*x_lead (2 pares). Se van sumando pares adicionales, uno a uno,
entre variables que antes eran solo lineales: x_ex_stack, x_tech, x_test,
x_ingles, x_soft. (Los pares extra son ILUSTRATIVOS/sinteticos para este
experimento metodologico, no estan justificados por el dominio como los
originales -- eso se lo confirmara el asesor.)
"""
import csv
import statistics as stats
from scipy.stats import spearmanr
import dimod
import neal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pipeline_perfil_ideal_vs_candidatos import mapear_candidato, distancia, score_lineal

candidatos = list(csv.DictReader(open("candidatos_TI_peru.csv", encoding="utf-8")))
ids_orden = [row["id"] for row in candidatos]
base_scores = {row["id"]: score_lineal(mapear_candidato(row)) for row in candidatos}
ranking_baseline = sorted(ids_orden, key=lambda cid: -base_scores[cid])
rank_pos_baseline = {cid: i for i, cid in enumerate(ranking_baseline)}

def ranking_qubo(ideal):
    dists = {row["id"]: distancia(ideal, mapear_candidato(row)) for row in candidatos}
    return sorted(ids_orden, key=lambda cid: dists[cid])

def construir_y_resolver(n_pares_extra, seed, num_reads=1500, presupuesto=None):
    cqm = dimod.ConstrainedQuadraticModel()
    x_ex_total = dimod.Integer('x_ex_total', lower_bound=0, upper_bound=15)
    x_ex_stack = dimod.Integer('x_ex_stack', lower_bound=0, upper_bound=10)
    x_tech     = dimod.Integer('x_tech', lower_bound=0, upper_bound=5)
    x_test     = dimod.Integer('x_test', lower_bound=0, upper_bound=100)
    x_senior   = dimod.Integer('x_senior', lower_bound=0, upper_bound=5)
    x_lead     = dimod.Integer('x_lead', lower_bound=0, upper_bound=5)
    x_cert     = dimod.Integer('x_cert', lower_bound=0, upper_bound=10)
    x_ingles   = dimod.Integer('x_ingles', lower_bound=0, upper_bound=5)
    x_soft     = dimod.Integer('x_soft', lower_bound=0, upper_bound=5)
    x_salary   = dimod.Integer('x_salary', lower_bound=0, upper_bound=10)
    y_lead     = dimod.Binary('y_lead')
    y_cert     = dimod.Binary('y_cert')
    x_sobre    = dimod.Binary('x_sobre')
    y_rotacion = dimod.Binary('y_rotacion')

    # Objetivo base: 2 interacciones originales + 5 terminos lineales
    objective = -1.0*(x_ex_total*x_cert) - 1.0*(x_senior*x_lead)

    # Variables normalizadas [0,1] para poder sumar peras con peras al armar pares extra
    norm = {"x_ex_stack": x_ex_stack/10.0, "x_tech": x_tech/5.0, "x_test": x_test/100.0,
            "x_ingles": x_ingles/5.0, "x_soft": x_soft/5.0}
    orden_vars = ["x_ex_stack","x_tech","x_test","x_ingles","x_soft"]

    # pares extra candidatos (ilustrativos), en orden de activacion
    pares_extra = [("x_ex_stack","x_tech"), ("x_test","x_ingles"),
                   ("x_soft","x_ex_stack"), ("x_tech","x_ingles"), ("x_test","x_soft")]

    usados_en_interaccion = set()
    for i in range(n_pares_extra):
        a, b = pares_extra[i]
        objective += -1.0 * (norm[a] * norm[b])
        usados_en_interaccion.add(a); usados_en_interaccion.add(b)

    # las variables lineales que NO estan (todavia) en una interaccion, se premian solas
    for v in orden_vars:
        if v not in usados_en_interaccion:
            objective += -1.0 * norm[v]
        else:
            # si ya esta en interaccion, se mantiene un pequeno termino lineal
            # para que siga siendo "deseable" individualmente tambien (igual que ex_total/cert/senior/lead)
            objective += -0.3 * norm[v]

    cqm.set_objective(objective)

    # Restricciones R1-R7 (identicas)
    cqm.add_constraint(y_lead - y_cert <= 0, label='R1')
    cqm.add_constraint(x_lead - x_senior <= 0, label='R2')
    cqm.add_constraint(x_tech - x_soft <= 1, label='R3a')
    cqm.add_constraint(x_soft - x_tech <= 1, label='R3b')
    cqm.add_constraint((x_test/100.0) + 0.3*(x_ex_total/15.0) >= 0.6, label='R4')
    cqm.add_constraint(x_ingles >= 2, label='R5')
    cqm.add_constraint(x_salary - 1*x_senior <= 1, label='R6')
    cqm.add_constraint(x_sobre + y_rotacion <= 1, label='R7')

    # Restriccion de PRESUPUESTO (opcional, para el diagnostico de saturacion)
    if presupuesto is not None:
        total_normalizado = (x_ex_total/15.0 + x_ex_stack/10.0 + x_tech/5.0 + x_test/100.0 +
                              x_senior/5.0 + x_lead/5.0 + x_cert/10.0 + x_ingles/5.0 + x_soft/5.0)
        cqm.add_constraint(total_normalizado <= presupuesto, label='R8_presupuesto')

    bqm, invert = dimod.cqm_to_bqm(cqm, lagrange_multiplier=50.0)
    sampler = neal.SimulatedAnnealingSampler()
    ss = sampler.sample(bqm, num_reads=num_reads, seed=seed)
    return dict(invert(ss.first.sample))


SEEDS = list(range(8))
NPARES = [0, 1, 2, 3, 4, 5]

print("="*60)
print("A) SIN restriccion de presupuesto (variables libres hasta su techo)")
print("="*60)
resumen_libre = []
for k in NPARES:
    corr = []
    for s in SEEDS:
        ideal = construir_y_resolver(k, seed=s, presupuesto=None)
        rk = ranking_qubo(ideal)
        rho, _ = spearmanr([rank_pos_baseline[c] for c in ids_orden], [rk.index(c) for c in ids_orden])
        corr.append(rho)
    m, sd = stats.mean(corr), stats.pstdev(corr)
    resumen_libre.append((k, m, sd))
    print(f"  pares extra={k}  (total interacciones={2+k})  Spearman medio={m:.3f}  desv={sd:.3f}")

print("\n" + "="*60)
print("B) CON restriccion de presupuesto (fuerza tradeoffs reales)")
print("="*60)
PRESUPUESTO = 4.5  # de un maximo posible de 9.0 (9 variables normalizadas a 1.0 cada una)
resumen_budget = []
for k in NPARES:
    corr = []
    for s in SEEDS:
        ideal = construir_y_resolver(k, seed=s, presupuesto=PRESUPUESTO)
        rk = ranking_qubo(ideal)
        rho, _ = spearmanr([rank_pos_baseline[c] for c in ids_orden], [rk.index(c) for c in ids_orden])
        corr.append(rho)
    m, sd = stats.mean(corr), stats.pstdev(corr)
    resumen_budget.append((k, m, sd))
    print(f"  pares extra={k}  (total interacciones={2+k})  Spearman medio={m:.3f}  desv={sd:.3f}")

# Grafico comparativo
fig, ax = plt.subplots(figsize=(8.5,5))
for resumen, label, color in [(resumen_libre, "Sin restriccion de presupuesto", "#2b6cb0"),
                                (resumen_budget, f"Con presupuesto (<= {PRESUPUESTO})", "#c0392b")]:
    xs = [2+r[0] for r in resumen]
    ys = [r[1] for r in resumen]
    errs = [r[2] for r in resumen]
    ax.errorbar(xs, ys, yerr=errs, marker="o", label=label, color=color, capsize=4)
ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
ax.set_xlabel("Numero total de pares de criterios interactuantes")
ax.set_ylabel("Correlacion de Spearman\n(ranking QUBO vs. ranking baseline lineal)")
ax.set_title("Efecto del numero de interacciones, con y sin restriccion de recursos\n(8 seeds por punto, media ± desv.est.)")
ax.set_ylim(-0.2, 1.15)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("numero_interacciones_vs_presupuesto.png", dpi=140)
print("\nGrafico guardado: numero_interacciones_vs_presupuesto.png")
