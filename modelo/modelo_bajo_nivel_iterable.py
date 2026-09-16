"""
Implementacion a bajo nivel (QUBO manual, R1-R8) — version ITERABLE.

Envuelve el modelo del director en funciones reutilizables:
- construir_y_resolver(...): corre una prueba con los lambdas que le pases.
- evaluar_restricciones(...): comprueba, sobre el resultado real, si cada
  restriccion R1-R8 se cumple de verdad (independiente de si la penalizacion
  crey0 estar cumpliendola: valida sobre los valores finales, no sobre la energia).
- auto_tune(...): AUTOMATIZA el ajuste: arranca con lambdas iguales y va
  duplicando el lambda de cualquier restriccion que siga incumplida, ronda
  a ronda, hasta que todas se satisfacen (o se alcanza el limite de rondas).
- Cada corrida se registra en registro_bajo_nivel.csv.

Incluye los 2 parches ya verificados (x_tech lower_bound=0; s8_int con
granularidad reducida para evitar el overflow de dimod).
"""
import csv
import os
from datetime import datetime

import dimod
import neal

PROXY_R8 = 7.0  # AJUSTADO de 4.5 -> 5.5 -> 7.0 (15-08-2026).
                # Con 4.5: R8 aislada necesitaba lambda>=4000 y aun asi fallaba.
                # Con 5.5: robusto (5/5 seeds), pero el presupuesto solo alcanza para
                # UNA de las dos interacciones del objetivo a la vez (trade-off fuerte;
                # ver 4.2.6 de la memoria, queda documentado como ejemplo valido).
                # Con 7.0: robusto (5/5 seeds, mismos lambdas), y AMBAS interacciones se
                # realizan a la vez con un perfil mas repartido entre las 13 variables.
                # Se adopta 7.0 como configuracion final; 5.5 se mantiene documentado
                # como ejemplo de trade-off extremo bajo escasez mas severa.
                # Ver registro_protocolo.csv y resumen_protocolo_sistematico.csv.


def construir_y_resolver(lambdas_R, lambdas_obj=None, num_reads=1000, seed=None,
                          etiqueta="", registrar=True, csv_path="registro_bajo_nivel.csv"):
    """
    lambdas_R: dict con claves 'R1'..'R8' (peso de cada restriccion).
    lambdas_obj: dict con claves 'l1'..'l7' (peso de cada termino del objetivo).
                 Por defecto, todos en 1.0.
    Devuelve dict con energia, perfil decodificado y verificacion de restricciones.
    """
    if lambdas_obj is None:
        lambdas_obj = {}
    l1 = lambdas_obj.get("l1", 1.0)
    l2 = lambdas_obj.get("l2", 1.0)
    l3 = lambdas_obj.get("l3", 1.0)
    l4 = lambdas_obj.get("l4", 1.0)
    l5 = lambdas_obj.get("l5", 1.0)
    l6 = lambdas_obj.get("l6", 1.0)
    l7 = lambdas_obj.get("l7", 1.0)

    cqm = dimod.ConstrainedQuadraticModel()

    x_ex_total = dimod.Integer('x_ex_total', lower_bound=0, upper_bound=15)
    x_ex_stack = dimod.Integer('x_ex_stack', lower_bound=0, upper_bound=10)
    x_tech     = dimod.Integer('x_tech', lower_bound=0, upper_bound=5)   # PARCHE
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

    F_obj = (
        -l1*(x_ex_total*x_cert) - l2*x_ex_stack - l3*x_tech - l4*x_test
        -l5*(x_senior*x_lead) - l6*x_ingles - l7*x_soft
    )

    R1 = lambdas_R.get("R1", 50.0)
    R2 = lambdas_R.get("R2", 50.0)
    R3 = lambdas_R.get("R3", 50.0)
    R4 = lambdas_R.get("R4", 50.0)
    R5 = lambdas_R.get("R5", 50.0)
    R6 = lambdas_R.get("R6", 50.0)
    R7 = lambdas_R.get("R7", 50.0)
    R8 = lambdas_R.get("R8", 50.0)

    P_R1 = R1 * (y_lead * (1 - y_cert))

    s2 = dimod.Integer('s2', lower_bound=0, upper_bound=5)
    P_R2 = R2 * (x_lead + s2 - x_senior)**2

    s3a = dimod.Integer('s3a', lower_bound=0, upper_bound=5)
    s3b = dimod.Integer('s3b', lower_bound=0, upper_bound=5)
    P_R3 = R3 * ((x_tech - x_soft + s3a - 1)**2 + (x_soft - x_tech + s3b - 1)**2)

    alpha, U_min = 0.3, 0.6
    s4_int = dimod.Integer('s4_int', lower_bound=0, upper_bound=100)
    P_R4 = R4 * ((x_test/100.0) + alpha*(x_ex_total/15.0) - (s4_int/100.0) - U_min)**2

    s5 = dimod.Integer('s5', lower_bound=0, upper_bound=3)
    P_R5 = R5 * (x_ingles - s5 - 2)**2

    b0, k = 1, 1
    s6 = dimod.Integer('s6', lower_bound=0, upper_bound=6)
    P_R6 = R6 * (x_salary + s6 - b0 - k*x_senior)**2

    P_R7 = R7 * (x_sobre * y_rotacion)

    proxy = PROXY_R8
    s8_int = dimod.Integer('s8_int', lower_bound=0, upper_bound=90)  # PARCHE: granularidad 0.05
    suma_capacidades = (
        (x_ex_total/15.0) + (x_ex_stack/10.0) + (x_tech/5.0) + (x_test/100.0) +
        (x_senior/5.0) + (x_lead/5.0) + (x_cert/10.0) + (x_ingles/5.0) + (x_soft/5.0)
    )
    P_R8 = R8 * (suma_capacidades + (s8_int/20.0) - proxy)**2   # PARCHE: /20 en vez de /100

    F_total = F_obj + P_R1 + P_R2 + P_R3 + P_R4 + P_R5 + P_R6 + P_R7 + P_R8
    cqm.set_objective(F_total)

    bqm, invert_mapping = dimod.cqm_to_bqm(cqm)
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads, seed=seed)

    best_sample = sampleset.first.sample
    best_energy = sampleset.first.energy
    decoded = dict(invert_mapping(best_sample))

    perfil = {k: (int(v) if k != "x_sobre" or True else v) for k, v in decoded.items()
              if k in ["x_ex_total","x_ex_stack","x_tech","x_test","x_senior","x_lead",
                        "x_cert","x_ingles","x_soft","x_salary","y_lead","y_cert",
                        "x_sobre","y_rotacion"]}
    perfil = {k: int(round(v)) for k, v in perfil.items()}

    checks = evaluar_restricciones(perfil)

    resultado = {
        "energia_minima": best_energy, "perfil": perfil, "restricciones_ok": checks,
        "num_incumplidas": sum(1 for ok in checks.values() if not ok),
        "lambdas_R": lambdas_R, "lambdas_obj": {"l1":l1,"l2":l2,"l3":l3,"l4":l4,"l5":l5,"l6":l6,"l7":l7},
        "num_reads": num_reads, "seed": seed, "etiqueta": etiqueta,
    }
    if registrar:
        _registrar(resultado, csv_path)
    return resultado


def evaluar_restricciones(perfil):
    """Verifica cada restriccion R1-R8 SOBRE LOS VALORES FINALES, de forma
    independiente al mecanismo de penalizacion. Devuelve dict R->bool (True=cumple)."""
    p = perfil
    proxy = PROXY_R8
    suma_cap = (p["x_ex_total"]/15 + p["x_ex_stack"]/10 + p["x_tech"]/5 + p["x_test"]/100 +
                p["x_senior"]/5 + p["x_lead"]/5 + p["x_cert"]/10 + p["x_ingles"]/5 + p["x_soft"]/5)
    return {
        "R1": not (p["y_lead"] == 1 and p["y_cert"] == 0),
        "R2": p["x_lead"] <= p["x_senior"],
        "R3": abs(p["x_tech"] - p["x_soft"]) <= 1,
        "R4": (p["x_test"]/100 + 0.3*p["x_ex_total"]/15) >= 0.6 - 1e-9,
        "R5": p["x_ingles"] >= 2,
        "R6": p["x_salary"] <= 1 + 1*p["x_senior"],
        "R7": not (p["x_sobre"] == 1 and p["y_rotacion"] == 1),
        "R8": suma_cap <= proxy + 1e-9,
    }


def _registrar(resultado, csv_path):
    perfil = resultado["perfil"]; checks = resultado["restricciones_ok"]
    fieldnames = (["fecha","etiqueta","num_reads","seed","energia_minima","num_incumplidas"]
                  + [f"lam_{k}" for k in resultado["lambdas_R"]]
                  + [f"ok_{k}" for k in checks]
                  + list(perfil.keys()))
    fila = {"fecha": datetime.now().isoformat(timespec="seconds"), "etiqueta": resultado["etiqueta"],
            "num_reads": resultado["num_reads"], "seed": resultado["seed"],
            "energia_minima": resultado["energia_minima"], "num_incumplidas": resultado["num_incumplidas"],
            **{f"lam_{k}": v for k, v in resultado["lambdas_R"].items()},
            **{f"ok_{k}": v for k, v in checks.items()}, **perfil}
    existe = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not existe: w.writeheader()
        w.writerow(fila)


def auto_tune(lambda_inicial=50.0, factor=2.0, max_rondas=6, num_reads=1000, seed=42,
              lambdas_obj=None, csv_path="registro_bajo_nivel.csv", graficar=True,
              grafico_path="auto_tune_evolucion.png"):
    """
    AUTOMATIZA el ajuste de los 8 lambdas de restriccion: arranca con todos
    iguales y, en cada ronda, DUPLICA el lambda de cualquier restriccion que
    siga incumplida en el resultado. Para cuando todas se cumplen o se agotan
    las rondas. Metodo simple y auditable (no una caja negra).
    lambdas_obj: opcional, lambdas del objetivo (l1..l7) a usar en cada ronda.
    graficar: si True, guarda un grafico de la evolucion de cada lambda y del
    numero de restricciones incumplidas por ronda (pedido explicito del director).
    """
    lambdas_R = {f"R{i}": lambda_inicial for i in range(1, 9)}
    historial = []
    for ronda in range(1, max_rondas + 1):
        r = construir_y_resolver(lambdas_R, lambdas_obj=lambdas_obj, num_reads=num_reads, seed=seed,
                                  etiqueta=f"autotune_ronda{ronda}", csv_path=csv_path)
        incumplidas = [k for k, ok in r["restricciones_ok"].items() if not ok]
        historial.append((ronda, dict(lambdas_R), incumplidas, r["energia_minima"]))
        print(f"Ronda {ronda}: incumplidas={incumplidas or 'NINGUNA'}  energia={r['energia_minima']:.1f}")
        if not incumplidas:
            print(f"\nConvergido en la ronda {ronda}. Lambdas finales: {lambdas_R}")
            if graficar:
                _graficar_autotune(historial, grafico_path)
            return lambdas_R, r, historial
        for k in incumplidas:
            lambdas_R[k] *= factor
    print(f"\nNo convergio en {max_rondas} rondas. Ultimo estado: {lambdas_R}")
    if graficar:
        _graficar_autotune(historial, grafico_path)
    return lambdas_R, r, historial


def _graficar_autotune(historial, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rondas = [h[0] for h in historial]
    claves_R = sorted(historial[0][1].keys())
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

    for k in claves_R:
        valores = [h[1][k] for h in historial]
        ax1.plot(rondas, valores, marker="o", label=k)
    ax1.set_ylabel("Valor del lambda")
    ax1.set_yscale("log")
    ax1.set_title("Evolución de los lambdas de restricción por ronda (auto_tune)")
    ax1.legend(ncol=4, fontsize=8)
    ax1.grid(alpha=0.3)

    num_incumplidas = [len(h[2]) for h in historial]
    ax2.bar(rondas, num_incumplidas, color="#c0392b")
    ax2.set_xlabel("Ronda")
    ax2.set_ylabel("Restricciones incumplidas")
    ax2.set_title("Restricciones incumplidas por ronda")
    ax2.set_xticks(rondas)
    ax2.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(path, dpi=140)
    print(f"Gráfico guardado: {path}")


if __name__ == "__main__":
    print("="*70)
    print("AJUSTE AUTOMATICO DE LAMBDAS (R1-R8)")
    print("="*70)
    lambdas_finales, resultado_final, historial = auto_tune(lambda_inicial=50.0, factor=2.0,
                                                              max_rondas=6, num_reads=1000, seed=42)
    print("\nPerfil final:")
    for k, v in resultado_final["perfil"].items():
        print(f"  {k}: {v}")
    print(f"\nRegistro completo de la busqueda en registro_bajo_nivel.csv")
