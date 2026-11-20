# CONTEXTO — Modelo de regímenes económicos (global + Argentina)

> Archivo para pasarle a Claude al empezar cada sesión de trabajo en este proyecto.
> Actualizar la sección **Estado actual** al terminar cada sesión.

## 1. Qué es el proyecto

Proyecto de aprendizaje de Coco (dev full-stack, Node/TS + Swift, sin experiencia previa en ML).
Objetivo doble:

1. **Aprender a construir modelos chicos de ML** (no LLMs): datos → features → modelo → evaluación → visualización.
2. Construir una herramienta que, mirando el contexto macro **global (EE.UU.) y argentino**, diga
   *en qué régimen económico estamos* y *qué clases de activos anduvieron mejor/peor históricamente en regímenes parecidos*
   (bonos, acciones por sector, dólar, oro, inmuebles, etc.), incluyendo **cómo se contagian a Argentina las crisis de EE.UU.**

**No es** un modelo para predecir precios de activos individuales. Es un "mapa con probabilidades", no un oráculo.
No reemplaza asesoramiento financiero profesional.

## 2. Cómo trabajar con Coco (reglas para Claude)

- Coco quiere **aprender**, no solo tener el resultado. Explicar el *por qué* de cada paso, en español rioplatense (voseo), conciso.
- Preferir que Coco escriba el código con guía; cuando Claude escriba código, que sea corto, comentado y paso a paso.
- Un concepto nuevo por vez. Antes de una técnica nueva, explicar la intuición en 3–5 líneas.
- Nada de magia: evitar librerías "todo en uno" que oculten lo que pasa.
- **Honestidad estadística obligatoria**: señalar siempre riesgo de *look-ahead bias*, *data leakage* y *overfitting*.
  Toda evaluación debe ser **walk-forward / out-of-sample**.
- Recordar que los datos macro se **revisan** y se **publican con rezago** (ej. el IPC de un mes sale a mediados del siguiente). Usar fechas de publicación, no de referencia, cuando importe.
- Para datos argentinos: siempre trabajar en **USD (CCL) o en términos reales (ajustado por IPC)**, nunca en pesos nominales.

## 3. Stack

- Python 3.12, entorno con `uv` (o `venv` + `pip`)
- Jupyter / VS Code notebooks para explorar; módulos en `src/` para lo reutilizable
- `pandas`, `numpy`, `pyarrow` (guardar en Parquet)
- `matplotlib` / `plotly` para gráficos
- `scikit-learn` (KMeans, GaussianMixture, LogisticRegression, métricas)
- `hmmlearn` (Hidden Markov Models)
- `statsmodels` (Granger, correlaciones, regresiones)
- `yfinance` (precios de mercado), `fredapi` (FRED), `requests` (APIs argentinas)
- Dashboard: `streamlit` primero; más adelante opcional API Node/TS + front propio
- Git desde el día 1

## 4. Fuentes de datos

### 4.1 Global — FRED (Reserva Federal de St. Louis)
- Web: https://fred.stlouisfed.org — API key gratis: https://fred.stlouisfed.org/docs/api/api_key.html
- Descarga sin key (CSV): `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`
- Librería: `fredapi` (`Fred(api_key=...).get_series('T10Y2Y')`)

| Serie | Qué mide | Frecuencia / desde aprox. |
|---|---|---|
| `T10Y2Y` | Curva de tasas 10a − 2a (inversión ≈ señal de recesión) | diaria, 1976 |
| `T10Y3M` | Curva 10a − 3m | diaria, 1982 |
| `FEDFUNDS` | Tasa de la Fed | mensual, 1954 |
| `CPIAUCSL` | Inflación EE.UU. (IPC) → calcular variación interanual | mensual, 1947 |
| `UNRATE` | Desempleo | mensual, 1948 |
| `INDPRO` | Producción industrial | mensual, 1919 |
| `BAA10Y` | Spread crédito corporativo Baa vs Tesoro (estrés crediticio) | diaria, 1986 |
| `NFCI` | Índice de condiciones financieras (Chicago Fed) | semanal, 1971 |
| `VIXCLS` | VIX, "índice del miedo" | diaria, 1990 |
| `DTWEXBGS` | Índice amplio del dólar | diaria, 2006 |
| `USREC` | Recesiones oficiales NBER (0/1) — **solo para validar, nunca como feature** | mensual |

> Nota: las series de spreads ICE BofA (`BAMLH0A0HYM2`) en FRED tienen historia limitada por licencia; usar `BAA10Y`.

### 4.2 Argentina
- **API BCRA – Estadísticas monetarias v4.0** (oficial, gratis, sin key):
  `https://api.bcra.gob.ar/estadisticas/v4.0/monetarias` (lista variables) y `.../monetarias/{idVariable}?desde=AAAA-MM-DD&hasta=...`
  Doc: https://www.bcra.gob.ar/archivos/Catalogo/Content/files/pdf/principales-variables-v4.pdf
  Usar para: reservas internacionales, base monetaria, tasas, tipo de cambio oficial (A3500), CER.
  (Puede requerir desactivar verificación SSL en algunos entornos por el certificado del BCRA: preferir pasar el CA correcto.)
- **ArgentinaDatos** (API comunitaria, gratis): https://argentinadatos.com/docs
  - Riesgo país histórico: `https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais`
  - Dólar por tipo: `https://api.argentinadatos.com/v1/cotizaciones/dolares/{casa}` (`oficial`, `blue`, `contadoconliqui`, `bolsa`…)
  - Inflación mensual: `https://api.argentinadatos.com/v1/finanzas/indices/inflacion`
  - **Verificar cobertura histórica de cada serie** al bajarla y documentarla.
- **Series de Tiempo de Argentina (datos.gob.ar)**: https://apis.datos.gob.ar/series/api/ — buscador: https://datos.gob.ar/series
  Usar para IPC INDEC, EMAE (actividad), salarios, etc.
- **INDEC**: https://www.indec.gob.ar (fuente primaria, para validar).

### 4.3 Mercados (precios) — `yfinance`
| Ticker | Uso |
|---|---|
| `^GSPC`, `SPY` | Acciones EE.UU. |
| `XLK`, `XLP`, `XLV`, `XLU`, `XLE`, `XLF` | Sectores (tech, consumo básico, salud, utilities, energía, financieras), desde 1998 |
| `IEF`, `TLT`, `SHY` | Bonos del Tesoro EE.UU. (medianos, largos, cortos) |
| `GLD` / `GC=F` | Oro |
| `VNQ` | REITs — proxy de bienes raíces EE.UU. |
| `EEM` | Mercados emergentes |
| `DX-Y.NYB` | Índice dólar |
| `^MERV` | Merval (en pesos → convertir a USD con CCL) |
| `ARGT` | ETF Argentina en USD (desde 2011) |
| `GGAL`, `YPF`, `BMA`, `PAM` | ADRs argentinos en USD (historia larga) |

**Limitaciones conocidas:** bonos argentinos tienen historia corta y quiebres por defaults/reestructuraciones (usar riesgo país como proxy); precio del m² en Argentina tiene pocos datos públicos confiables (tratar inmuebles AR como análisis cualitativo/aparte).

## 5. Estructura del repo

```
modelo-regimenes/
├── CONTEXTO.md            ← este archivo
├── README.md
├── pyproject.toml
├── .env                   ← FRED_API_KEY (no commitear)
├── data/
│   ├── raw/               ← descargas tal cual (Parquet/CSV), no editar
│   └── processed/         ← series limpias, mensuales, alineadas
├── notebooks/
│   ├── 01_exploracion_fred.ipynb
│   ├── 02_regimenes_globales.ipynb
│   ├── 03_argentina.ipynb
│   ├── 04_contagio.ipynb
│   └── 05_backtest.ipynb
├── src/
│   ├── data/      (fred.py, argentina.py, mercados.py)
│   ├── features/  (build.py)
│   ├── models/    (regimenes.py, contagio.py)
│   └── backtest/  (walkforward.py)
└── app/           (dashboard Streamlit)
```

## 6. Fases (roadmap)

Cada fase termina con algo que funciona + un concepto aprendido.

### Fase 0 — Setup (1 sesión)
Python + `uv`, repo git, estructura de carpetas, key de FRED, primer notebook que baja `T10Y2Y` y lo grafica.
**Listo cuando:** el gráfico muestra la curva y las recesiones `USREC` sombreadas.

### Fase 1 — Datos y exploración global (1–2 semanas)
Bajar las series de 4.1, guardarlas en `data/raw`, pasarlas a frecuencia **mensual**, alinear, tratar faltantes.
Features: inflación interanual, cambio de desempleo a 12m, curva, spread, VIX, NFCI. Estandarizar (z-score).
**Conceptos:** pandas, resampling, transformaciones (niveles vs. cambios), estacionariedad, correlaciones.
**Listo cuando:** hay un `features_global.parquet` mensual y gráficos de cada feature con recesiones marcadas.

### Fase 2 — Regímenes globales (2 semanas)
1. Base: `KMeans` y `GaussianMixture` sobre las features → ver qué grupos salen.
2. Modelo principal: `hmmlearn.GaussianHMM` (3–5 estados), elegir cantidad con BIC + interpretabilidad.
3. Interpretar cada estado por sus medias (ej. "expansión", "sobrecalentamiento", "recesión", "estanflación") y nombrarlo.
4. Validar: ¿los estados de estrés coinciden con `USREC`? (solo validación).
5. Probabilidades filtradas (solo con datos hasta t), **no** suavizadas, para evitar look-ahead.
**Conceptos:** aprendizaje no supervisado, matriz de transición, probabilidades de estado, BIC.

### Fase 3 — Argentina (2–3 semanas)
Bajar 4.2, limpiar, pasar a USD/real. Features: riesgo país, brecha (CCL/oficial − 1), variación de reservas, inflación mensual, Merval en USD, tasa real.
Modelo de regímenes propio (HMM), con el **régimen global como input** adicional.
Bonus supervisado: `LogisticRegression` que estime P(estrés argentino en próximos 6 meses), definiendo "estrés" explícitamente (ej. riesgo país +30% o CCL +25% en 3 meses).
**Conceptos:** limpieza de datos sucios, quiebres estructurales, clasificación supervisada, desbalance de clases, métricas (precision/recall, ROC).

### Fase 4 — Contagio EE.UU. → Argentina (1–2 semanas)
- **Estudios de evento**: 2008 (crisis financiera), 2013 (taper tantrum), 2018 (suba de tasas Fed + crisis cambiaria local), 2020 (COVID), 2022 (suba agresiva de tasas).
  Para cada uno: qué pasó con riesgo país, CCL, Merval USD, ADRs, en ventanas −3/+12 meses.
- **Rezagos**: correlación cruzada y causalidad de Granger (`statsmodels`) entre variables globales y argentinas.
- Matriz: régimen global × régimen argentino → probabilidad de transición a estrés local.
**Conceptos:** series de tiempo, rezagos, causalidad estadística vs. real, tamaño de muestra chico.

### Fase 5 — Régimen → activos + backtest honesto (2 semanas)
- Tabla: retorno real/USD promedio, volatilidad y drawdown de cada activo de 4.3 **por régimen**.
- Estrategia simple: en cada mes, asignar según el régimen estimado *con datos disponibles hasta ese mes*.
- Backtest **walk-forward** (reentrenar periódicamente), con costos de transacción, contra benchmarks: 60/40 y buy & hold.
**Conceptos:** backtesting, walk-forward, sesgo de supervivencia, overfitting de estrategias, Sharpe, drawdown.

### Fase 6 — Dashboard (1–2 semanas)
Streamlit: régimen global y argentino actuales con probabilidad, evolución histórica, tabla de activos por régimen, riesgo de contagio, actualización mensual automática.
Opcional después: exponer resultados por API (Node/TS) y front con diseño propio.

## 7. Reglas técnicas

- Frecuencia base: **mensual** (fin de mes).
- Guardar crudos en `data/raw` con fecha de descarga; nunca sobrescribir sin versionar.
- Todo split de entrenamiento/prueba es **temporal**, nunca aleatorio.
- Fijar semillas (`random_state`) para reproducibilidad.
- Cada notebook arranca con un bloque Markdown: objetivo, conceptos, conclusiones.
- Documentar cada decisión de diseño en `README.md` (sección "Decisiones").

## 8. Estado actual

- [ ] Fase 0 — Setup
- [ ] Fase 1 — Datos globales
- [ ] Fase 2 — Regímenes globales
- [ ] Fase 3 — Argentina
- [ ] Fase 4 — Contagio
- [ ] Fase 5 — Activos + backtest
- [ ] Fase 6 — Dashboard

**Última sesión:** (completar)
**Próximo paso:** Fase 0.
**Notas / dudas abiertas:** (completar)
