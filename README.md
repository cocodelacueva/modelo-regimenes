# Proyecto Modelo Regimes

Este proyecto esta creado como aprendizaje. La idea era armar un modelo de IA desde cero para aprender como se arman. No es un llm porque era imposible entrenar ese tipo de modelos en mi máquina, asi que pense en este modelo. 
La idea es crear un modelo como termómetro económico. Considera variables locales y de USA. 

## Datos recolectados
En el pdf y contexto hay más data.

### ¿De dónde salen?

- FRED: Reserva Federal de St. Louis. https://fred.stlouisfed.org/ - API key: https://fred.stlouisfed.org/docs/api/api_key.html

### Glosario de datos

* **T10Y2Y**: es la tasa del bono del Tesoro a 10 años menos la del bono a 2 años. Normalmente prestar a largo plazo paga más, así que el número da positivo. Cuando se da vuelta (curva invertida, valor negativo), el mercado está apostando a que la Fed va a tener que bajar tasas porque viene una desaceleración.

## Gl


## Armando paso a paso

### Fase 0 Entorno y Primeros pasos

#### UNO: Usamos uv en vez de pip para que arme sola la .venv y que sea más rápido

```bash
uv init --bare --python 3.12   # crea solo el pyproject.toml, sin archivos de ejemplo
uv python pin 3.12             # crea .python-version (como un .nvmrc)
```

#### DOS: Agregamos las librerías base: 
- pandas maneja tablas y series de tiempo
- matplotlib grafica
- fredapi habla con FRED 
- python-dotenv lee el .env
```bash
uv add pandas matplotlib fredapi python-dotenv
uv add --dev ipykernel         # para correr notebooks en VS Code con este entorno
```
Y la librería dev ipykernel: es una librería de utilidad para correr notebook con vs code.

#### TRES: Verificar que funcione. 

Si devuelve ok, y la versión el entorno esta funcionando.

```bash
uv run python -c "import pandas, fredapi; print('ok', pandas.__version__)"
```

#### CUATRO: parket

Es un formato de tablas comprimido y con tipos de datos, más prolijo que CSV

```bash
uv add pyarrow # libreria para guardar en Parquet
```

#### QUINTO: Primer notebook

Al crearlo se agrega un markdown en la primer celda para explicar. Se crea el archivo .ipynb y se elige .venv como kernel.
Leer el primero notebook para más detalle.

### d





```bash

```