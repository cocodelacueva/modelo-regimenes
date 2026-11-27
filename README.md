# Proyecto Modelo Regimes

Este proyecto esta creado como aprendizaje. La idea era armar un modelo de IA desde cero para aprender como se arman. No es un llm porque era imposible entrenar ese tipo de modelos en mi máquina, asi que pense en este modelo. 
La idea es crear un modelo como termómetro económico. Considera variables locales y de USA. 

## Datos recolectados
En el pdf y contexto hay más data.

### ¿De dónde salen?

- FRED: Reserva Federal de St. Louis. https://fred.stlouisfed.org/ - API key: https://fred.stlouisfed.org/docs/api/api_key.html

### Glosario de datos

* Parquet es un formato binario orientado a columnas ideal para análisis de grandes volúmenes de datos, mientras que CSV es un formato de texto plano orientado a filas mejor para archivos pequeños, legibles y de intercambio simple
**Tasas y curva**
* **T10Y2Y** — Tasa a 10 años − tasa a 2 años. Si se invierte (valor negativo), el mercado espera una desaceleración.
  → **Cruda.** Al ser una resta de dos tasas, es comparable entre épocas.
* **T10Y3M** — Tasa a 10 años − letra a 3 meses. Misma idea; muchos la consideran mejor señal de recesión.
  → **Cruda.**
* **DGS2** — Tasa del bono del Tesoro a 2 años. Sigue lo que se espera de la Fed.
  → **A decidir.** Un 5% no significa lo mismo en 1981 que en 2015. Opciones: cambio a 12 meses, o tasa real (tasa − inflación).
* **DGS10** — Tasa del bono a 10 años. Expectativas de crecimiento e inflación a largo plazo.
  → **A decidir.** Igual que DGS2.
* **FEDFUNDS** — Tasa de la Fed. La sube para frenar la inflación y la baja para estimular.
  → **A decidir.** Igual que DGS2.
**Economía real**
* **CPIAUCSL** — Índice de precios de EE.UU. Es un índice que siempre crece (100 en 1982, más de 300 hoy).
  → **Transformada: inflación interanual** (% de cambio contra el mismo mes del año anterior).
* **UNRATE** — Desempleo, % de la fuerza laboral.
  → **Cruda y también transformada (cambio a 12 meses).** El número dice algo, pero lo que avisa recesiones es que suba.
* **INDPRO** — Índice de producción industrial. Crece con los años.
  → **Transformada: variación a 12 meses.**
**Estrés financiero**
* **BAA10Y** — Cuánto más rinde un bono de empresa (calidad media) que el del Tesoro. Si sube, hay miedo a que las empresas no paguen.
  → **Cruda.** Sube en las crisis y vuelve.
* **NFCI** — Índice de condiciones financieras de la Fed de Chicago. 0 = normal, positivo = plata cara o difícil de conseguir.
  → **Cruda.** Ya viene armado para que 0 sea el promedio.
* **VIXCLS** — VIX, el "índice del miedo". ~12–20 es calma, >30 es estrés.
  → **Cruda.** Se dispara y vuelve a su rango.
**Dólar**
* **DTWEXBGS** — Valor del dólar contra las monedas de los socios comerciales de EE.UU. Dólar fuerte suele apretar a Argentina.
  → **Transformada: variación a 3 o 12 meses.** El 100 (enero 2006) es arbitrario.
**Solo para validar**
* **USREC** — 1 = mes en recesión según el NBER, 0 = no. Se publica con meses o años de retraso.
  → **Nunca entra al modelo.** Solo sirve para ver si el modelo detecta las recesiones.

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

**Nota:** *get_series te devuelve la última versión revisada de cada dato, no lo que se sabía en ese momento. Por ejemplo, el desempleo de marzo 2008 que ves hoy no es el que se publicó en abril 2008. Por ahora alcanza con saberlo. En la Fase 5 (backtest) eso va a importar, porque usar datos revisados es una forma sutil de look-ahead.*

### Fase 1 Datos y exploración global

#### UNO: Importamos modulos y datos
Creamos un archivo en src/data/ para traer toda la info. Se hace desde aca, un módulo, para poder utilizarlo en muchos notebook sin problemas. Es mejor asi. 
Desde el notebook 2, importamos un modulo creado en src, asi no tenemos que escribir varias veces lo mismo.

**NOTA IMPORTANTE:**
Serie = cualquier dato a lo largo del tiempo. Las 13 son series. No hay series "que no se usan".
La única pregunta es: ¿la uso cruda (tal como la bajé) o tengo que calcular algo a partir de ella?
La regla para decidir: si el número de hoy se puede comparar directamente con el de hace 30 años, va cruda. Si no, se transforma.

#### DOS: Creamos tabla mensual

Un modelo necesita una tabla donde cada fila es un mes y cada columna una variable, sin huecos de calendario. Hoy tenés series diarias (curva, VIX, spread), una semanal (NFCI) y mensuales (IPC, desempleo). resample("ME") agrupa cada serie por mes y te obliga a elegir cómo resumir cada mes. "ME" quiere decir month end, y además mueve la etiqueta al último día del mes. Eso también arregla la convención de FRED de fechar al día 1.

Decisiones: 
* "T10Y3M y BAA10Y reemplazadas por GS10−TB3MS y BAA−GS10 (desde 1953). Validadas contra las oficiales: correlación 0,9956 y 0,99998."
* tomar el promedio cuando es día a día. (mean)
* "TB3MS convertida de base descuento a rendimiento real (365·d / (360 − 91·d)) antes de calcular la curva. Sesgo medio vs. T10Y3M oficial: de +0,12 a +0,01 pp."

Instrucciones Panda: 
```python
p["GS10"]               # corchete simple → UNA columna (una Series)
p[["T10Y3M", "GS10"]]   # corchete doble → una TABLA más chica con esas columnas
p["GS10"] - p["TB3MS"] # restar columnas
p["NUEVA"] = p["GS10"] - p["TB3MS"] # crear columna nueva
nuevo = p.copy() # Sin .copy(), nuevo y p serían el mismo objeto, y agregarle una columna a uno se la agregaría al otro.
#p["TB3MS"] / 100 divide toda la columna de una vez, sin loop. Es lo mismo que la resta de antes: pandas aplica la operación fila por fila.
#La fórmula se escribe igual que con números sueltos, pero opera sobre la columna entera. Esto se llama operación vectorizada y es la forma normal de trabajar en pandas.
```

**Comparar con números:**
```python
par = p[["T10Y3M", "CURVA_10Y3M_LARGA"]].dropna()
print(par.corr())

#.dropna() → borra las filas donde falta alguna de las dos. Quedan solo los años en que existen ambas (1982 en adelante), que son los únicos comparables.
#.corr() → correlación: un número entre −1 y 1 que dice cuánto se mueven juntas. 1 = suben y bajan exactamente a la vez; 0 = no tienen nada que ver. Esperás algo como 0,99.
```

**Comparar a ojo:**

```python
par.plot(figsize=(14, 4), title="Curva 10a−3m: oficial vs. sustituta")
#Un DataFrame tiene su propio .plot(), que grafica cada columna como una línea con leyenda. Es un atajo de matplotlib. Si el sustituto anda bien, las dos líneas se tienen que casi pisar.
```


### Fase 1 Datos y exploración global


```bash

```