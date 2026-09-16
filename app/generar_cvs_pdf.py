"""Genera un PDF de CV por fila de candidatos_TI_peru.csv en cvs_pdf/ (para la demo de carga)."""
import csv, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

os.makedirs("cvs_pdf", exist_ok=True)
BANDA = 8000

def cv(row):
    ruta = f"cvs_pdf/CV_{row['id']}.pdf"
    c = canvas.Canvas(ruta, pagesize=A4)
    w, h = A4
    y = h - 2.5 * cm
    def linea(txt, tam=10.5, salto=0.6, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", tam)
        c.drawString(2.5 * cm, y, txt)
        y -= salto * cm
    def seccion(t):
        nonlocal y
        y -= 0.3 * cm; linea(t.upper(), 11, 0.65, bold=True)
        c.line(2.5 * cm, y + 0.45 * cm, w - 2.5 * cm, y + 0.45 * cm)

    salario = int(row["_salario_pen"]); desv = round((salario - BANDA) / BANDA * 100)
    linea(f"Candidato {row['id']}", 18, 0.9, bold=True)
    linea(f"Desarrollador/a Backend {row['perfil']} · {row['ubicacion']}, Lima", 11, 0.9)
    seccion("Perfil")
    linea(f"Experiencia total: {row['c1_exp_total']} años")
    linea(f"Experiencia en el stack requerido: {row['c2_exp_stack']} años")
    linea(f"Seniority: {row['c6_seniority']}")
    linea(f"Liderazgo / mentoring: {row['c7_liderazgo']}/5")
    seccion("Tecnologías")
    linea(f"Stack: {row['_tecnologias'].replace(';', ', ')}")
    linea(f"Nivel en Python: {row['c3_nivel_python']}/5")
    linea(f"Cobertura del stack del rol: {round(float(row['c4_cobertura'])*100)}%")
    linea(f"Resultado de prueba técnica: {row['c5_prueba_tecnica']}/100")
    seccion("Formación y certificaciones")
    linea(f"Universidad: {row['universidad']}")
    linea(f"Certificaciones relevantes: {row['c8_certificaciones']}")
    seccion("Idiomas y habilidades")
    linea(f"Inglés: {row['c9_ingles']}")
    linea(f"Soft skills: {row['c10_soft_skills']}/5")
    seccion("Condiciones")
    linea(f"Pretensión salarial: S/ {salario} mensuales")
    linea(f"Permanencia media por empleo: {row['c12_permanencia_meses']} meses")
    linea(f"Índice de sobrecualificación: {row['c13_sobrecualificacion']}")
    c.save()
    return ruta

if __name__ == "__main__":
    with open("candidatos_TI_peru.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            print(cv(r))
