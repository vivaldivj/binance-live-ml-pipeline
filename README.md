# Binance LIVE ML — Pipeline ETL + Machine Learning para trading algorítmico

Proyecto en Python que implementa un flujo automatizado para obtener datos de mercado desde Binance Futures, transformarlos en variables técnicas, aplicar modelos de Machine Learning previamente entrenados y ejecutar decisiones operativas sobre el mercado.

> **Nota:** este repositorio se presenta con fines técnicos, educativos y de portafolio. No constituye recomendación financiera ni sistema listo para operar con capital real sin revisión, pruebas y control de riesgos adicionales.

---

## Objetivo del proyecto

Construir un pipeline automatizado que conecte tres áreas principales:

1. **Ingeniería de datos / ETL**
   - Extracción de velas desde la API de Binance Futures.
   - Limpieza, transformación y generación de variables técnicas.
   - Creación de datasets intermedios para inferencia.

2. **Machine Learning aplicado a series financieras**
   - Carga de modelos entrenados previamente.
   - Aplicación de escaladores, PCA y Random Forest.
   - Evaluación de señales de entrada mediante umbrales por patrón.

3. **Automatización operativa**
   - Generación de órdenes LONG/SHORT.
   - Seguimiento de órdenes pendientes.
   - Colocación posterior de Stop Loss y Take Profit.
   - Registro de resultados en archivos de monitoreo y Excel.

---

## Flujo general del sistema

```text
main.py
  │
  ├── 1Parte/ObtenerDatos.py
  │     ├── Extrae datos desde Binance Futures
  │     ├── Calcula indicadores y patrones técnicos
  │     └── Exporta CSVs temporales en Archivos/
  │
  ├── 2Aplanar/Aplanador.py
  │     ├── Lee datasets generados
  │     ├── Convierte ventanas de velas en una fila plana
  │     └── Genera dataset listo para inferencia
  │
  ├── 3CargarModelo/Buy|Sell/CargarModelox.py
  │     ├── Carga scaler + PCA + Random Forest
  │     ├── Aplica transformación ML
  │     ├── Evalúa probabilidad contra umbral
  │     └── Decide si se abre operación
  │
  └── 4AbrirOperaciones/LONG|SHORT/
        ├── Calcula entrada, riesgo, SL y TP
        ├── Coloca orden en Binance Futures
        └── Genera archivo de monitoreo
```

---

## Estructura del proyecto

```text
Binance LIVE ML/
├── main.py
├── 1Parte/
│   └── ObtenerDatos.py
├── 2Aplanar/
│   └── Aplanador.py
├── 3CargarModelo/
│   ├── Buy/
│   │   ├── CargarModelo.py
│   │   └── CargarModelox.py
│   ├── Sell/
│   │   ├── CargarModelo.py
│   │   └── CargarModelox.py
│   └── Modelos/
│       ├── BNB/
│       │   ├── scaler*.pkl
│       │   ├── pca*.pkl
│       │   └── random_forest*.pkl
│       └── modelos_umbrales_*.csv
├── 4AbrirOperaciones/
│   ├── LONG/
│   └── SHORT/
├── ARCHIVOS_APOYO_EMPAREJAMIENTO_DE_DATOS/
└── Archivos/
```

---

## Componentes técnicos

### 1. Extracción de datos

El módulo `1Parte/ObtenerDatos.py` consume la API pública de Binance Futures para obtener velas de mercado. A partir de esos datos genera un DataFrame con precios OHLCV, tiempos de apertura/cierre y columnas auxiliares de fecha.

### 2. Transformación y feature engineering

Sobre los datos crudos se generan variables técnicas como:

- Color de vela.
- Cuerpo de vela.
- Mechas superiores e inferiores.
- RSI.
- Medias móviles.
- ATR / volatilidad.
- Patrones técnicos como 180, RSI50, Hammer y DV.

Esta parte representa la capa de transformación del pipeline: convierte datos crudos de mercado en variables útiles para análisis e inferencia.

### 3. Aplanado de datos para Machine Learning

El módulo `2Aplanar/Aplanador.py` toma ventanas de 30 velas y las convierte en una sola fila de características. Esto permite transformar datos secuenciales en una estructura tabular compatible con modelos clásicos de Machine Learning.

### 4. Inferencia con modelos entrenados

Los módulos de `3CargarModelo/Buy/` y `3CargarModelo/Sell/` cargan tres componentes por patrón:

- `scaler`: normalización/estandarización de variables.
- `pca`: reducción de dimensionalidad.
- `random_forest`: modelo de clasificación.

El flujo de inferencia es:

```text
Dataset aplanado → scaler → PCA → Random Forest → probabilidad → umbral → decisión
```

Cada patrón utiliza modelos y umbrales específicos, almacenados en `3CargarModelo/Modelos/`.

### 5. Automatización de órdenes

Si el modelo confirma una entrada, el sistema ejecuta módulos de `4AbrirOperaciones/` para calcular parámetros de operación y colocar órdenes en Binance Futures.

El sistema también genera un archivo `ordenes_monitoreo.csv` para dar seguimiento a órdenes pendientes y colocar Stop Loss / Take Profit cuando la orden principal sea ejecutada.

---

## Instalación

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar entorno:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

El flujo principal ejecuta el proceso de análisis cada 30 minutos y monitorea órdenes pendientes en ciclos cortos.

---

## Configuración requerida

Antes de operar, se deben configurar credenciales de Binance Futures. Actualmente el código contiene placeholders:

```python
api_key = ""
api_secret = ""
```

Para una versión publicable en GitHub, se recomienda mover estas credenciales a variables de entorno o archivo `.env` excluido del repositorio.

Ejemplo sugerido:

```python
import os

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
```

---

## Archivos generados en tiempo de ejecución

El proyecto genera archivos intermedios y de monitoreo como:

```text
Archivos/{MONEDA}Data.csv
Archivos/{MONEDA}Data_Large.csv
Archivos/Ap{MONEDA}.csv
4AbrirOperaciones/ordenes_monitoreo.csv
Estadisticas.xlsx
Predicciones_0.xlsx
```

Estos archivos son salidas temporales o registros operativos. Para GitHub, normalmente deben excluirse mediante `.gitignore`, salvo que se quiera incluir una pequeña muestra de datos anonimizados.

---

## Valor técnico del proyecto

Este proyecto demuestra experiencia práctica en:

- Consumo de APIs financieras en tiempo real.
- Construcción de pipelines ETL en Python.
- Procesamiento de datos tabulares con pandas y NumPy.
- Feature engineering aplicado a series temporales financieras.
- Preparación de datos para modelos supervisados.
- Inferencia con modelos de Machine Learning serializados.
- Automatización de decisiones basada en modelos.
- Integración entre datos, modelos y acciones operativas.
- Manejo de archivos CSV/Excel como capa de persistencia ligera.
- Diseño de flujo modular por etapas.

---

## Mejoras recomendadas

Para una versión más sólida de portafolio, se recomienda:

1. Centralizar configuración en un archivo `config.py` o variables de entorno.
2. Reemplazar rutas relativas frágiles por rutas basadas en `pathlib.Path(__file__)`.
3. Sustituir `subprocess.Popen(["python3", ...])` por `subprocess.Popen([sys.executable, ...])`.
4. Agregar pruebas unitarias para funciones de transformación.
5. Separar la lógica de trading real de la lógica de análisis/inferencia.
6. Crear una carpeta `data_sample/` con datos pequeños de ejemplo.
7. Documentar entradas, salidas y columnas clave de cada etapa.
8. Agregar logs estructurados en lugar de usar únicamente `print()`.
9. Evitar subir credenciales, archivos operativos o resultados sensibles.

---

