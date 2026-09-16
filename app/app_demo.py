"""
Demo web local del TFM: carga de CVs en PDF -> extraccion de criterios ->
perfil ideal por optimizacion combinatoria (QUBO) -> ranking por distancia.

Uso:  .venv/bin/python app_demo.py     ->  http://localhost:8765
"""
import csv
import html
import io
import re
import webbrowser
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, HTTPServer

from pypdf import PdfReader

from modelo_bajo_nivel_iterable import construir_y_resolver, PROXY_R8
from pipeline_perfil_ideal_vs_candidatos import mapear_candidato, distancia, RANGOS

R_BASE = {f"R{i}": 100.0 for i in range(1, 8)} | {"R8": 300.0}

# Presets de puesto: mismas restricciones, distinto enfasis en el objetivo (lambdas l1..l7).
PUESTOS = {
    "backend": ("Backend (configuración validada)", R_BASE, {"l5": 6.0},
                "Énfasis equilibrado; interacción seniority×liderazgo reforzada (λ₅=6)."),
    "lider":   ("Líder técnico", R_BASE, {"l5": 12.0, "l7": 3.0},
                "Prima la interacción seniority×liderazgo (λ₅=12) y las habilidades blandas (λ₇=3)."),
    "tecnico": ("Especialista técnico", R_BASE, {"l3": 4.0, "l4": 3.0, "l5": 1.0},
                "Prima el nivel técnico (λ₃=4) y la prueba técnica (λ₄=3); liderazgo neutro."),
}

ETIQUETAS = {
    "x_ex_total": "Experiencia total", "x_ex_stack": "Exp. en el stack", "x_tech": "Nivel técnico",
    "x_test": "Prueba técnica", "x_senior": "Seniority", "x_lead": "Liderazgo", "x_cert": "Certificaciones",
    "x_ingles": "Inglés", "x_soft": "Soft skills", "x_salary": "Desv. salarial", "y_lead": "Asume liderazgo",
    "y_cert": "Certificado", "x_sobre": "Sobrecualificado", "y_rotacion": "Riesgo rotación",
}

# ---------------------------------------------------------------- extraccion
CAMPOS = {  # clave CSV -> regex sobre el texto del PDF
    "c1_exp_total": r"Experiencia total:\s*(\d+)",
    "c2_exp_stack": r"stack requerido:\s*(\d+)",
    "c3_nivel_python": r"Nivel en Python:\s*(\d)",
    "c4_cobertura": r"Cobertura del stack del rol:\s*(\d+)",
    "c5_prueba_tecnica": r"prueba técnica:\s*(\d+)",
    "c6_seniority": r"Seniority:\s*(\w+)",
    "c7_liderazgo": r"Liderazgo / mentoring:\s*(\d)",
    "c8_certificaciones": r"Certificaciones relevantes:\s*(\d+)",
    "c9_ingles": r"Inglés:\s*([ABC][12])",
    "c10_soft_skills": r"Soft skills:\s*(\d)",
    "_salario_pen": r"Pretensión salarial:\s*S/\s*(\d+)",
    "c12_permanencia_meses": r"Permanencia media por empleo:\s*(\d+)",
    "c13_sobrecualificacion": r"sobrecualificación:\s*([\d.]+)",
}
BANDA_SALARIAL = 8000


def extraer_cv(nombre, datos):
    """PDF -> fila con las columnas del CSV. Lanza ValueError si falta un campo."""
    texto = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(datos)).pages)
    fila = {"id": (re.search(r"Candidato\s+(\w+)", texto) or [None, nombre])[1],
            "perfil": (re.search(r"Backend\s+(\w+)", texto) or [None, "-"])[1]}
    for k, rx in CAMPOS.items():
        m = re.search(rx, texto, flags=re.I)
        if not m:
            raise ValueError(f"{nombre}: no se encontró «{k}»")
        fila[k] = m.group(1)
    fila["c4_cobertura"] = str(int(fila["c4_cobertura"]) / 100)
    fila["c11_desviacion_salarial_pct"] = str((int(fila["_salario_pen"]) - BANDA_SALARIAL) / BANDA_SALARIAL * 100)
    return fila


def cvs_de_ejemplo():
    with open("candidatos_TI_peru.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- modelo
def ejecutar(filas, puesto="backend", num_reads=5000, seed=42):
    _, lam_r, lam_obj, _ = PUESTOS[puesto]
    res = construir_y_resolver(lam_r, lam_obj, num_reads=num_reads, seed=seed,
                               etiqueta=f"demo_{puesto}", registrar=False)
    ideal = res["perfil"]
    cands = {r["id"]: mapear_candidato(r) for r in filas}
    ranking = sorted(((cid, distancia(ideal, v)) for cid, v in cands.items()), key=lambda t: t[1])
    return ideal, res["restricciones_ok"], ranking, cands


def desglose(ideal, cand):
    """Aporte de cada variable a la distancia² (normalizado por rango)."""
    return {k: ((ideal.get(k, 0) - cand.get(k, 0)) / r) ** 2 for k, r in RANGOS.items()}


# ---------------------------------------------------------------- vista
CSS = """
 body{font:15px/1.5 system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222;background:#fafafa}
 h1{font-size:1.45rem;margin-bottom:.2rem} h2{font-size:1.05rem;margin:1.8rem 0 .5rem;color:#333}
 .sub{color:#666;margin-top:0}
 .card{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:1rem 1.2rem;margin:1rem 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
 .paso{display:inline-block;background:#1f4e79;color:#fff;border-radius:50%;width:1.6rem;height:1.6rem;text-align:center;line-height:1.6rem;font-size:.85rem;margin-right:.5rem}
 table{border-collapse:collapse;width:100%;margin:.5rem 0;font-size:.93rem}
 th,td{border-bottom:1px solid #eee;padding:.4rem .6rem;text-align:left;vertical-align:middle}
 th{background:#f3f5f8;font-weight:600} tr.win{background:#eaf5ec;font-weight:600}
 .bar{display:inline-block;height:.75rem;background:#1f4e79;border-radius:3px;vertical-align:middle}
 .bar.g{background:#2e8b57} .bar.o{background:#e67e22}
 .chip{display:inline-block;padding:.15rem .6rem;border-radius:1rem;font-size:.85rem;margin:.15rem}
 .ok{background:#e3f4e8;color:#1a7f37} .bad{background:#fbe4e1;color:#c0392b}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.6rem}
 .kv{background:#f3f5f8;border-radius:6px;padding:.5rem .7rem} .kv b{display:block;font-size:1.3rem;color:#1f4e79}
 .kv span{font-size:.8rem;color:#555}
 label{display:block;margin:.5rem 0 .2rem;font-weight:600} select,input{padding:.35rem;font-size:.95rem}
 button{padding:.5rem 1.2rem;font-size:1rem;background:#1f4e79;color:#fff;border:0;border-radius:6px;cursor:pointer;margin-top:1rem}
 .dz{border:2px dashed #b8c4d0;border-radius:8px;padding:1.2rem;text-align:center;background:#fff;color:#555}
 .cfg{color:#666;font-size:.85rem}
 .files{font-size:.9rem;color:#333;margin-top:.5rem}
"""

CABECERA = """<!doctype html><meta charset="utf-8"><title>Selección de personal · perfil ideal QUBO</title>
<style>{css}</style>
<h1>Sistema de recomendación para la selección de personal</h1>
<p class="sub">Perfil de candidato ideal por optimización combinatoria (QUBO, recocido simulado) y selección del CV más próximo.</p>
"""

INICIO = CABECERA + """
<form method="post" action="/analizar" enctype="multipart/form-data" class="card">
 <h2><span class="paso">1</span>Cargar currículos (PDF)</h2>
 <div class="dz"><input type="file" name="cv" accept="application/pdf" multiple required
   onchange="document.getElementById('f').textContent=[...this.files].map(x=>x.name).join(' · ')">
   <div class="files" id="f"></div></div>
 <h2><span class="paso">2</span>Definir el puesto</h2>
 <label>Perfil buscado</label>
 <select name="puesto">{opciones}</select>
 <p class="cfg">Los pesos λ del objetivo cambian con el perfil; las restricciones R1–R8 (λ=100, λ(R8)=300, proxy={proxy}) se mantienen.</p>
 <label>Lecturas del recocido (num_reads)</label>
 <input type="number" name="reads" value="5000" min="100" max="20000" step="100">
 &nbsp; <label style="display:inline">semilla</label> <input type="number" name="seed" value="42" style="width:5rem">
 <br><button>Analizar candidatos</button>
</form>
<p class="cfg">Sin PDFs a mano: <a href="/analizar?puesto=backend">ejecutar con los 15 CV de ejemplo</a>.</p>
"""

RESULTADO = CABECERA + """
<p class="cfg"><a href="/">← nueva consulta</a> · puesto: <b>{puesto}</b> · {desc} · num_reads={reads} · semilla={seed}</p>
<div class="card"><h2><span class="paso">1</span>Currículos procesados ({n})</h2>
<table><tr><th>CV</th><th>Perfil</th><th>Exp.</th><th>Stack</th><th>Python</th><th>Prueba</th><th>Lid.</th><th>Cert.</th><th>Inglés</th><th>Soft</th><th>Salario</th></tr>{cvs}</table></div>
<div class="card"><h2><span class="paso">2</span>Perfil ideal generado</h2>
<p>Restricciones: {restr}</p><div class="grid">{ideal}</div></div>
<div class="card"><h2><span class="paso">3</span>Candidatos más próximos al perfil ideal</h2>
<table><tr><th>#</th><th>CV</th><th>Distancia</th><th style="width:45%">Afinidad</th></tr>{ranking}</table></div>
<div class="card"><h2><span class="paso">4</span>Por qué {c1} y no {c2}</h2>
<p class="cfg">Aporte de cada criterio a la distancia² al perfil ideal (menor es mejor). En verde, el criterio en que gana cada candidato.</p>
<table><tr><th>Criterio</th><th>Ideal</th><th>{c1}</th><th></th><th>{c2}</th><th></th></tr>{expl}
<tr class="win"><td>Total</td><td></td><td>{t1:.2f}</td><td></td><td>{t2:.2f}</td><td></td></tr></table></div>
"""


def render_resultado(filas, puesto, reads, seed):
    ideal, restr, ranking, cands = ejecutar(filas, puesto, reads, seed)
    e = html.escape
    cvs = "".join(
        f"<tr><td>{e(r['id'])}</td><td>{e(r['perfil'])}</td><td>{r['c1_exp_total']} a</td><td>{r['c2_exp_stack']} a</td>"
        f"<td>{r['c3_nivel_python']}/5</td><td>{r['c5_prueba_tecnica']}</td><td>{r['c7_liderazgo']}/5</td>"
        f"<td>{r['c8_certificaciones']}</td><td>{e(r['c9_ingles'])}</td><td>{r['c10_soft_skills']}/5</td>"
        f"<td>S/ {r['_salario_pen']}</td></tr>" for r in filas)
    restr_html = "".join(f'<span class="chip {"ok" if v else "bad"}">{k} {"✓" if v else "✗"}</span>' for k, v in restr.items())
    ideal_html = "".join(f'<div class="kv"><b>{v}</b><span>{ETIQUETAS[k]} (0–{RANGOS[k]})</span></div>'
                         for k, v in ((k, ideal[k]) for k in ETIQUETAS if k in ideal))
    dmax = ranking[-1][1]
    rank_html = "".join(
        f'<tr class="{"win" if i == 0 else ""}"><td>{i+1}</td><td>{e(cid)}</td><td>{d:.2f}</td>'
        f'<td><span class="bar {"g" if i == 0 else ""}" style="width:{max(4, 100 * (1 - d / (dmax * 1.15))):.0f}%"></span></td></tr>'
        for i, (cid, d) in enumerate(ranking))
    c1, c2 = ranking[0][0], ranking[1][0]
    d1, d2 = desglose(ideal, cands[c1]), desglose(ideal, cands[c2])
    expl = "".join(
        f"<tr><td>{ETIQUETAS[k]}</td><td>{ideal.get(k, 0)}</td>"
        f'<td>{cands[c1][k]}</td><td><span class="bar {"g" if d1[k] < d2[k] else "o"}" style="width:{d1[k]*120:.0f}px"></span> {d1[k]:.2f}</td>'
        f'<td>{cands[c2][k]}</td><td><span class="bar {"g" if d2[k] < d1[k] else "o"}" style="width:{d2[k]*120:.0f}px"></span> {d2[k]:.2f}</td></tr>'
        for k in RANGOS if d1[k] or d2[k])
    return RESULTADO.format(css=CSS, puesto=e(PUESTOS[puesto][0]), desc=e(PUESTOS[puesto][3]), reads=reads, seed=seed,
                            n=len(filas), cvs=cvs, restr=restr_html, ideal=ideal_html, ranking=rank_html,
                            c1=e(c1), c2=e(c2), expl=expl, t1=sum(d1.values()), t2=sum(d2.values()))


def render_inicio():
    ops = "".join(f'<option value="{k}">{html.escape(v[0])}</option>' for k, v in PUESTOS.items())
    return INICIO.format(css=CSS, opciones=ops, proxy=PROXY_R8)


# ---------------------------------------------------------------- servidor
class Handler(BaseHTTPRequestHandler):
    def _responder(self, cuerpo, codigo=200):
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def _params(self, q):
        puesto = q.get("puesto", "backend") if q.get("puesto") in PUESTOS else "backend"
        try:
            reads = max(100, min(20000, int(q.get("reads", 5000))))
            seed = int(q.get("seed", 42))
        except ValueError:
            reads, seed = 5000, 42
        return puesto, reads, seed

    def do_GET(self):
        ruta, _, qs = self.path.partition("?")
        if ruta == "/analizar":  # atajo con los CV de ejemplo
            q = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
            self._responder(render_resultado(cvs_de_ejemplo(), *self._params(q)))
        elif ruta == "/":
            self._responder(render_inicio())
        else:
            self.send_error(404)

    def do_POST(self):
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        msg = BytesParser(policy=email_policy).parsebytes(
            f"Content-Type: {self.headers['Content-Type']}\r\n\r\n".encode() + cuerpo)
        q, filas, errores = {}, [], []
        for parte in msg.iter_parts():
            nombre = parte.get_param("name", header="content-disposition")
            if nombre == "cv" and parte.get_filename():
                try:
                    filas.append(extraer_cv(parte.get_filename(), parte.get_payload(decode=True)))
                except Exception as ex:  # PDF ilegible o sin los campos
                    errores.append(str(ex))
            elif nombre:
                q[nombre] = parte.get_payload(decode=True).decode().strip()
        if len(filas) < 2:
            self._responder(render_inicio() + "<p class='chip bad'>Se necesitan al menos 2 CV legibles. "
                            + html.escape("; ".join(errores)) + "</p>", 400)
            return
        self._responder(render_resultado(filas, *self._params(q)))

    def log_message(self, *a):
        pass  # ponytail: sin log de acceso, es una demo local


if __name__ == "__main__":
    print("Demo en http://localhost:8765  (Ctrl+C para salir)")
    webbrowser.open("http://localhost:8765")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
