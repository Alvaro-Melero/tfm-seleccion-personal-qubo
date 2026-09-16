# Dataset de candidatos de TI (contexto peruano)

**Álvaro Alejandro Melero Maguiña** · TFM · Prueba de concepto

> Conjunto de **15 perfiles de candidatos de TI del mercado peruano (Lima), de recopilación y elaboración propia**, anonimizados: identificadores `C01`–`C15`, sin datos personales ni personas identificables. Los datos de contexto (universidad, ubicación) son ilustrativos y **no** se usan como criterio de mérito.

## Rol objetivo
Formar un **equipo backend de k = 4** para una fintech en Lima. **Stack requerido (5):** Python, FastAPI/Django, PostgreSQL, AWS, Docker. **Banda salarial del rol (mid):** punto medio S/ 8 000 mensuales. El objetivo es seleccionar la mejor combinación de 4 candidatos que maximice ajuste y complementariedad, penalice redundancia y sobrecualificación, y cubra el stack dentro de presupuesto.

## Codificación de los criterios
| # | Criterio | Cómo se puntúa |
|---|---|---|
| c1 | Años de experiencia total | años (0–15) |
| c2 | Años en el stack requerido | años (0–10) |
| c3 | Nivel en Python | 1–5 (autoevaluado/entrevista) |
| c4 | Cobertura de tecnologías del rol | nº de las 5 requeridas que domina / 5 (0–1) |
| c5 | Resultado de prueba técnica | 0–100 |
| c6 | Seniority | junior / mid / senior |
| c7 | Liderazgo / mentoring | 0–5 |
| c8 | Certificaciones relevantes | conteo (p. ej. AWS) |
| c9 | Inglés | MCER A1–C2 |
| c10 | Soft skills | 0–5 |
| c11 | Desviación salarial vs banda | % sobre S/ 8 000 (positivo = por encima → penaliza) |
| c12 | Historial de permanencia | meses medios por empleo |
| c13 | Sobrecualificación respecto al rol | índice 0–1 (alto → riesgo de rotación) |

## Matriz candidatos × criterios

| ID | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | 10 | 7 | 5 | 1.0 | 88 | senior | 5 | 2 | B2 | 4 | 75 | 40 | 0.7 |
| C02 | 8 | 6 | 5 | 0.8 | 82 | senior | 4 | 1 | C1 | 5 | 56 | 55 | 0.5 |
| C03 | 5 | 4 | 4 | 0.8 | 75 | mid | 2 | 0 | B1 | 4 | 2 | 30 | 0.1 |
| C04 | 4 | 3 | 4 | 0.6 | 70 | mid | 1 | 0 | B2 | 3 | -5 | 26 | 0.1 |
| C05 | 6 | 4 | 3 | 0.8 | 72 | mid | 3 | 2 | B2 | 4 | 9 | 34 | 0.2 |
| C06 | 5 | 4 | 3 | 0.6 | 68 | mid | 1 | 0 | A2 | 3 | 0 | 22 | 0.1 |
| C07 | 2 | 2 | 3 | 0.4 | 62 | junior | 0 | 0 | B1 | 4 | -40 | 14 | 0.0 |
| C08 | 2 | 1 | 3 | 0.4 | 58 | junior | 0 | 0 | A2 | 3 | -48 | 10 | 0.0 |
| C09 | 2 | 2 | 3 | 0.4 | 60 | junior | 0 | 0 | B1 | 5 | -44 | 16 | 0.0 |
| C10 | 5 | 2 | 3 | 0.2 | 55 | mid | 1 | 0 | B2 | 4 | 0 | 24 | 0.1 |
| C11 | 12 | 9 | 5 | 1.0 | 90 | senior | 5 | 3 | C1 | 3 | 100 | 60 | 0.9 |
| C12 | 4 | 3 | 4 | 0.6 | 71 | mid | 1 | 1 | B1 | 4 | -4 | 28 | 0.1 |
| C13 | 7 | 5 | 4 | 0.8 | 78 | mid | 3 | 0 | B2 | 4 | 10 | 44 | 0.3 |
| C14 | 3 | 2 | 3 | 0.6 | 65 | junior | 0 | 0 | A2 | 3 | -35 | 18 | 0.0 |
| C15 | 6 | 4 | 4 | 0.6 | 74 | mid | 2 | 1 | C1 | 5 | 5 | 36 | 0.2 |

## Perfiles

**C01** — Senior · PUCP · San Isidro. 10 años de experiencia (7 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL, AWS, Docker. Python 5/5, prueba técnica 88/100, inglés B2, soft skills 4/5. Pretensión S/ 14000 (75% vs banda), permanencia media 40 meses.

**C02** — Senior · UNI · Miraflores. 8 años de experiencia (6 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL, AWS. Python 5/5, prueba técnica 82/100, inglés C1, soft skills 5/5. Pretensión S/ 12500 (56% vs banda), permanencia media 55 meses.

**C03** — Mid · UPC · Surco. 5 años de experiencia (4 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL, Docker. Python 4/5, prueba técnica 75/100, inglés B1, soft skills 4/5. Pretensión S/ 8200 (2% vs banda), permanencia media 30 meses.

**C04** — Mid · UNMSM · San Miguel. 4 años de experiencia (3 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL. Python 4/5, prueba técnica 70/100, inglés B2, soft skills 3/5. Pretensión S/ 7600 (-5% vs banda), permanencia media 26 meses.

**C05** — Mid · UTEC · Jesús María. 6 años de experiencia (4 en el stack). Tecnologías: Python, PostgreSQL, AWS, Docker. Python 3/5, prueba técnica 72/100, inglés B2, soft skills 4/5. Pretensión S/ 8700 (9% vs banda), permanencia media 34 meses.

**C06** — Mid · Cibertec · Los Olivos. 5 años de experiencia (4 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL. Python 3/5, prueba técnica 68/100, inglés A2, soft skills 3/5. Pretensión S/ 8000 (0% vs banda), permanencia media 22 meses.

**C07** — Junior · UNMSM · Comas. 2 años de experiencia (2 en el stack). Tecnologías: Python, PostgreSQL. Python 3/5, prueba técnica 62/100, inglés B1, soft skills 4/5. Pretensión S/ 4800 (-40% vs banda), permanencia media 14 meses.

**C08** — Junior · TECSUP · Callao. 2 años de experiencia (1 en el stack). Tecnologías: Python, Docker. Python 3/5, prueba técnica 58/100, inglés A2, soft skills 3/5. Pretensión S/ 4200 (-48% vs banda), permanencia media 10 meses.

**C09** — Junior · USIL · Lince. 2 años de experiencia (2 en el stack). Tecnologías: Python, FastAPI/Django. Python 3/5, prueba técnica 60/100, inglés B1, soft skills 5/5. Pretensión S/ 4500 (-44% vs banda), permanencia media 16 meses.

**C10** — Mid · U. de Lima · San Borja. 5 años de experiencia (2 en el stack). Tecnologías: Python. Python 3/5, prueba técnica 55/100, inglés B2, soft skills 4/5. Pretensión S/ 8000 (0% vs banda), permanencia media 24 meses.

**C11** — Senior · UNI · Miraflores. 12 años de experiencia (9 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL, AWS, Docker. Python 5/5, prueba técnica 90/100, inglés C1, soft skills 3/5. Pretensión S/ 16000 (100% vs banda), permanencia media 60 meses.

**C12** — Mid · UNSA (Arequipa) · Remoto. 4 años de experiencia (3 en el stack). Tecnologías: Python, PostgreSQL, AWS. Python 4/5, prueba técnica 71/100, inglés B1, soft skills 4/5. Pretensión S/ 7700 (-4% vs banda), permanencia media 28 meses.

**C13** — Mid · PUCP · Pueblo Libre. 7 años de experiencia (5 en el stack). Tecnologías: Python, FastAPI/Django, PostgreSQL, Docker. Python 4/5, prueba técnica 78/100, inglés B2, soft skills 4/5. Pretensión S/ 8800 (10% vs banda), permanencia media 44 meses.

**C14** — Junior · UNT (Trujillo) · Remoto. 3 años de experiencia (2 en el stack). Tecnologías: Python, PostgreSQL, Docker. Python 3/5, prueba técnica 65/100, inglés A2, soft skills 3/5. Pretensión S/ 5200 (-35% vs banda), permanencia media 18 meses.

**C15** — Mid · UPC · San Miguel. 6 años de experiencia (4 en el stack). Tecnologías: Python, FastAPI/Django, AWS. Python 4/5, prueba técnica 74/100, inglés C1, soft skills 5/5. Pretensión S/ 8400 (5% vs banda), permanencia media 36 meses.

## Nota de diseño (estructura del conjunto)
El conjunto está construido para que la selección de equipo sea un problema real y no trivial:

- **Cobertura complementaria:** ningún candidato mid/junior cubre solo el stack; C05 y C12 aportan AWS/Docker que a C03/C04/C06 les falta, de modo que el valor de un equipo depende de **combinar** perfiles.
- **Redundancia:** C04 y C06 tienen perfiles muy solapados; elegir a ambos aporta poco frente a elegir uno y complementar.
- **Sobrecualificación y rotación:** C11 (y en menor grado C01) son muy fuertes pero caros y con alto riesgo de rotación (c13 alto, c11 muy positivo); el modelo debería penalizarlos pese a su ajuste individual.
- **Bajo ajuste:** C10 tiene perfil frontend y baja cobertura backend; debería quedar descartado.
- **Juniors económicos:** C07–C09, C14 aportan cobertura parcial a bajo coste y buenas soft skills.

Esta estructura permite comparar la selección combinatoria (que capta interacciones) frente a un baseline que solo suma puntuaciones individuales.

> Los atributos protegidos (edad, género, origen) **no** figuran como criterios. El archivo de datos para el algoritmo es `candidatos_TI_peru.csv`.
