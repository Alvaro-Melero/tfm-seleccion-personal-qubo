# Selección de personal con optimización combinatoria de inspiración cuántica

Código y datos del Trabajo de Fin de Máster **«RRHH: Sistema de recomendación inteligente
para la selección de personal con algoritmia de inspiración cuántica»**.

Máster Universitario en Inteligencia Artificial Aplicada — Universidad Europea
Autor: Álvaro Alejandro Melero Maguiña · Director: Dr. Ezequiel Luis Murina Moreno
Curso 2025-2026

## Qué hace

El sistema no aprende de contrataciones pasadas. Parte de la descripción del puesto
—qué criterios importan, cuánto pesan, cómo interactúan y qué reglas no pueden romperse—
y construye el **perfil del candidato ideal** resolviendo un problema QUBO por recocido
simulado. Después ordena los CV disponibles por su distancia a ese perfil y desglosa,
criterio a criterio, por qué prefiere a un postulante sobre otro.

El modelo tiene 13 variables, un objetivo con dos interacciones y ocho restricciones
(R1–R8), siendo R8 la restricción de escasez de recursos: el hallazgo central del trabajo
es que **sin ella el enfoque combinatorio no se diferencia de una suma ponderada simple**,
ya que el perfil ideal satura todas las variables.

## Estructura

```
modelo/         formulación QUBO (objetivo + R1-R8) y selección por distancia
experimentos/   protocolo de calibración, escalado de interacciones, perfiles por puesto
datos/          15 candidatos (recopilación propia, anonimizados), sus CV en PDF y los
                registros fila a fila de cada corrida, incluidas las fallidas
app/            interfaz web local: carga de CV en PDF -> ranking explicado
figuras/        figuras de la memoria (calibración y resultados)
```

## Instalación

Requiere Python 3.12 y el [Ocean SDK](https://docs.ocean.dwavesys.com/) de D-Wave.

```bash
python -m venv .venv && source .venv/bin/activate
pip install dimod dwave-neal numpy scipy matplotlib pandas pypdf reportlab
```

## Uso

Generar el perfil ideal y el ranking sobre los 15 candidatos:

```bash
python modelo/pipeline_perfil_ideal_vs_candidatos.py
```

Levantar la interfaz web (http://localhost:8765):

```bash
python app/app_demo.py
```

Reproducir el experimento de sensibilidad al puesto (3 configuraciones × 5 semillas):

```bash
python experimentos/experimento_perfiles_puesto.py
```

## Reproducibilidad

Los resultados de la memoria se obtuvieron con `num_reads=5000` y `seed=42`, configuración
con la que se satisfacen las 8 restricciones y el candidato seleccionado es C05
(distancia 1,79).

Conviene advertir que en la configuración *backend* los tres criterios que compiten por el
presupuesto tienen el mismo peso, por lo que **el óptimo no es único**: varios perfiles
alcanzan exactamente la misma energía (−415,0) y la semilla del recocido decide entre
ellos. No se trata de un problema de convergencia, sino de un empate genuino del modelo;
está documentado como limitación en la memoria. Las configuraciones *líder* y
*especialista*, con pesos distintos, sí son estables entre semillas.

## Datos

El conjunto de 15 candidatos es de recopilación y elaboración propia, anonimizado: no
contiene datos personales identificables ni atributos protegidos (sexo, edad, origen),
excluidos por diseño del modelo.

## Licencia

MIT
