"""
Pipeline completo: correr el modelo (perfil ideal) + elegir candidato por
distancia sobre los 15 CVs sinteticos, con revision de estabilidad.
"""
import csv
import math
import statistics as stats

import dimod
import neal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from modelo_seleccion_iterable import ejecutar_modelo, construir_modelo

LAMBDAS_BASE = {"l1":1.0,"l2":1.0,"l3":1.0,"l4":1.0,"l5":1.0,"l6":1.0,"l7":1.0}

SENIOR_MAP = {"junior": 1, "mid": 3, "senior": 5}
ING_MAP = {"A1":0,"A2":1,"B1":2,"B2":3,"C1":4,"C2":5}

def mapear_candidato(row):
    salario_units = min(10, max(0, round(float(row["c11_desviacion_salarial_pct"]) / 10)))
    liderazgo = int(row["c7_liderazgo"])
    certs = int(row["c8_certificaciones"])
    sobre = float(row["c13_sobrecualificacion"])
    perman = float(row["c12_permanencia_meses"])
    return {
        "x_ex_total": int(row["c1_exp_total"]),
        "x_ex_stack": int(row["c2_exp_stack"]),
        "x_tech":     int(row["c3_nivel_python"]),
        "x_test":     int(row["c5_prueba_tecnica"]),
        "x_senior":   SENIOR_MAP[row["c6_seniority"]],
        "x_lead":     liderazgo,
        "x_cert":     min(10, certs),
        "x_ingles":   ING_MAP[row["c9_ingles"]],
        "x_soft":     int(row["c10_soft_skills"]),
        "x_salary":   salario_units,
        "y_lead":     1 if liderazgo > 0 else 0,
        "y_cert":     1 if certs >= 1 else 0,
        "x_sobre":    1 if sobre > 0.5 else 0,
        "y_rotacion": 1 if perman < 24 else 0,
    }

RANGOS = {
    "x_ex_total":15, "x_ex_stack":10, "x_tech":5, "x_test":100, "x_senior":5,
    "x_lead":5, "x_cert":10, "x_ingles":5, "x_soft":5, "x_salary":10,
    "y_lead":1, "y_cert":1, "x_sobre":1, "y_rotacion":1,
}

def distancia(ideal, candidato):
    total = 0.0
    for k, rango in RANGOS.items():
        diff = (ideal.get(k,0) - candidato.get(k,0)) / rango
        total += diff**2
    return math.sqrt(total)

def score_lineal(cand_vec):
    pos = ["x_ex_total","x_ex_stack","x_tech","x_test","x_senior","x_lead",
           "x_cert","x_ingles","x_soft"]
    neg = ["x_salary","x_sobre","y_rotacion"]
    return sum(cand_vec[k]/RANGOS[k] for k in pos) - sum(cand_vec[k]/RANGOS[k] for k in neg)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import statistics as stats

    # ------------------------------------------------------------------
    # 1. ESTABILIDAD: correr el mismo modelo (lambdas base) con varias seeds
    # ------------------------------------------------------------------
    print("="*70)
    print("PASO 1 — ESTABILIDAD DEL SOLVER (5 seeds, mismos lambdas)")
    print("="*70)
    energias = []
    y_lead_vals, x_lead_vals = [], []
    for s in range(5):
        r = ejecutar_modelo(LAMBDAS_BASE, seed=s, num_reads=1000, etiqueta=f"estabilidad_seed{s}_nr1000", registrar=True)
        energias.append(r["energia_minima"])
        y_lead_vals.append(r["perfil"].get("y_lead"))
        x_lead_vals.append(r["perfil"].get("x_lead"))
        print(f" seed={s}: energia={r['energia_minima']:.2f}  x_lead={r['perfil'].get('x_lead')}  y_lead={r['perfil'].get('y_lead')}  y_cert={r['perfil'].get('y_cert')}")

    print(f"\nEnergia: media={stats.mean(energias):.2f}  desv.est={stats.pstdev(energias):.2f}  rango=[{min(energias):.2f}, {max(energias):.2f}]")
    print(f"y_lead observado en las 5 corridas: {y_lead_vals}  (x_lead siempre en {set(x_lead_vals)})")
    print("-> Si y_lead varia entre 0 y 1 con x_lead siempre alto, confirma el problema de fondo ya reportado (variables no ligadas).")

    # ------------------------------------------------------------------
    # 2. PERFIL IDEAL definitivo (fijamos una seed para reproducibilidad)
    # ------------------------------------------------------------------
    print("\n" + "="*70)
    print("PASO 2 — PERFIL IDEAL (lambdas base, seed=42, referencia)")
    print("="*70)
    ideal = ejecutar_modelo(LAMBDAS_BASE, seed=42, num_reads=1000, etiqueta="ideal_referencia_nr1000", registrar=True)["perfil"]
    for k, v in ideal.items():
        print(f"  {k}: {v}")

    # ------------------------------------------------------------------
    # 3. CARGA Y RANKING DE LOS 15 CANDIDATOS
    # ------------------------------------------------------------------
    candidatos = list(csv.DictReader(open("candidatos_TI_peru.csv", encoding="utf-8")))
    resultados = []
    for row in candidatos:
        cand_vec = mapear_candidato(row)
        d = distancia(ideal, cand_vec)
        resultados.append((row["id"], row["perfil"], d, cand_vec))
    resultados.sort(key=lambda t: t[2])

    print("\n" + "="*70)
    print("PASO 3 — RANKING POR DISTANCIA AL PERFIL IDEAL (los 15 CVs)")
    print("="*70)
    print(f"{'ID':5} {'Perfil':8} {'Distancia':10}")
    for cid, perfil, d, _ in resultados:
        print(f"{cid:5} {perfil:8} {d:.4f}")
    ganador = resultados[0]
    print(f"\n>>> Candidato mas cercano al ideal: {ganador[0]} ({ganador[1]}), distancia={ganador[2]:.4f}")

    # ------------------------------------------------------------------
    # 4. BASELINE simple
    # ------------------------------------------------------------------
    scores = [(row["id"], row["perfil"], score_lineal(mapear_candidato(row))) for row in candidatos]
    scores.sort(key=lambda t: -t[2])
    print("\n" + "="*70)
    print("PASO 4 — BASELINE LINEAL (sin interacciones, para comparar)")
    print("="*70)
    for cid, perfil, s in scores[:5]:
        print(f"{cid:5} {perfil:8} score={s:.3f}")
    print(f"\n>>> Mejor candidato segun baseline lineal: {scores[0][0]} ({scores[0][1]})")

    # ------------------------------------------------------------------
    # 5. Grafico
    # ------------------------------------------------------------------
    ids = [r[0] for r in resultados]
    dists = [r[2] for r in resultados]
    colors = ["#c0392b" if i==0 else "#2b6cb0" for i in range(len(ids))]
    plt.figure(figsize=(9,4.5))
    plt.bar(ids, dists, color=colors)
    plt.ylabel("Distancia al perfil ideal (normalizada)")
    plt.title("Distancia de cada candidato al perfil ideal generado por QUBO")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("distancia_candidatos_ideal.png", dpi=140)
    print("\nGrafico guardado: distancia_candidatos_ideal.png")
