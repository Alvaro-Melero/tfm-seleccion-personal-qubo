"""
Protocolo sistematico pedido por el director: (1) cada restriccion R1-R8
aislada (todas las demas apagadas), (2) todas las combinaciones de a pares.
Se registra todo para el anexo de la memoria.
"""
import csv
from itertools import combinations
from modelo_bajo_nivel_iterable import construir_y_resolver

LAMBDA_TEST = 100.0
NUM_READS = 1000
SEED = 42
LAMBDAS_OBJ = {"l1":1.0,"l2":1.0,"l3":1.0,"l4":1.0,"l5":6.0,"l6":1.0,"l7":1.0}

resultados = []

print("="*70)
print("FASE 1 — CADA RESTRICCION AISLADA (las demas en 0)")
print("="*70)
for i in range(1, 9):
    ri = f"R{i}"
    lambdas_R = {f"R{j}": (LAMBDA_TEST if j == i else 0.0) for j in range(1, 9)}
    r = construir_y_resolver(lambdas_R, lambdas_obj=LAMBDAS_OBJ, num_reads=NUM_READS,
                              seed=SEED, etiqueta=f"aislada_{ri}", csv_path="registro_protocolo.csv")
    ok = r["restricciones_ok"][ri]
    print(f"  {ri} sola: {'OK' if ok else 'FALLA'}")
    resultados.append({"fase":"aislada","combinacion":ri,"resultado":"OK" if ok else "FALLA"})

print("\n" + "="*70)
print("FASE 2 — TODOS LOS PARES (28 combinaciones)")
print("="*70)
fallos_pares = []
for i, j in combinations(range(1, 9), 2):
    ri, rj = f"R{i}", f"R{j}"
    lambdas_R = {f"R{k}": (LAMBDA_TEST if k in (i, j) else 0.0) for k in range(1, 9)}
    r = construir_y_resolver(lambdas_R, lambdas_obj=LAMBDAS_OBJ, num_reads=NUM_READS,
                              seed=SEED, etiqueta=f"par_{ri}_{rj}", csv_path="registro_protocolo.csv")
    ok_i = r["restricciones_ok"][ri]
    ok_j = r["restricciones_ok"][rj]
    ambas_ok = ok_i and ok_j
    estado = "OK" if ambas_ok else f"FALLA ({ri}={'OK' if ok_i else 'X'}, {rj}={'OK' if ok_j else 'X'})"
    print(f"  {ri}+{rj}: {estado}")
    resultados.append({"fase":"par","combinacion":f"{ri}+{rj}","resultado":estado})
    if not ambas_ok:
        fallos_pares.append((ri, rj, ok_i, ok_j))

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
fallos_aisladas = [r for r in resultados if r["fase"]=="aislada" and r["resultado"]=="FALLA"]
print(f"Aisladas que fallan: {[r['combinacion'] for r in fallos_aisladas] or 'NINGUNA'}")
print(f"Pares con conflicto: {len(fallos_pares)} de 28")
for ri, rj, oki, okj in fallos_pares:
    print(f"  {ri}+{rj}: {ri} {'bien' if oki else 'MAL'}, {rj} {'bien' if okj else 'MAL'}")

with open("resumen_protocolo_sistematico.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["fase","combinacion","resultado"])
    w.writeheader()
    w.writerows(resultados)
print("\nResumen guardado en resumen_protocolo_sistematico.csv")
print("Detalle completo (perfiles, lambdas) en registro_protocolo.csv")
