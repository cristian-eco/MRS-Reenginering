# 🎬 MRS - Movie Recommendation System (Reingeniería)

Proyecto de reingeniería de software sobre un sistema legado de recomendación de películas, desarrollado como parte del Proyecto Final de Reingeniería. Este documento consolida el análisis del sistema legado (documentación inicial y complementaria) y describe la arquitectura propuesta para su modernización.

---

## 📌 Descripción General

El sistema legado corresponde a una aplicación web desarrollada en **Python** con el framework **Flask**, cuyo objetivo es recomendar películas a los usuarios a partir de una base de datos local. Combina dos enfoques de recomendación:

- **Filtrado demográfico**: recomienda las películas mejor calificadas usando una fórmula ponderada (IMDB weighted rating).
- **Filtrado basado en contenido**: recomienda películas similares a partir de su sinopsis, reparto, director, palabras clave y género, usando `TF-IDF` y similitud de coseno (`Scikit-Learn`).

El proyecto sigue una arquitectura modular que separa rutas, lógica de negocio, procesamiento de datos, modelos y configuración.

---

## 🏗️ Arquitectura del Sistema Legado

```
MRS-main/
│
├── app/
│   ├── data_processing/     # Filtrado demográfico y basado en contenido
│   ├── models/               # Modelo Movie (acceso a SQLite)
│   ├── routes/                # Blueprint de recomendaciones
│   ├── services/             # Lógica intermedia entre rutas y procesamiento
│   ├── utils/                 # Conexión a base de datos
│   └── __init__.py           # Application factory (create_app)
│
├── config/
│   └── config.py             # Rutas de archivos y configuración centralizada
│
├── data/                     # Base de datos SQLite y datasets CSV (no versionados)
├── scripts/
│   └── database_setup.py     # Script de inicialización de la base de datos
├── static/                   # CSS, JS y assets
├── templates/                # Vistas HTML (Jinja2)
├── run.py                    # Punto de entrada de la aplicación
└── requirements.txt
```

**Componentes principales:**

| Componente | Rol |
|---|---|
| Flask | Framework web y enrutamiento (Blueprints) |
| SQLite | Almacenamiento local de películas y calificaciones |
| Scikit-Learn | TF-IDF, CountVectorizer y similitud de coseno para recomendaciones |
| Pandas / NumPy | Procesamiento y limpieza de los datasets |
| Requests | Consumo de la API externa de TMDB (pósters, sinopsis, detalles) |

### Dependencias originales (`requirements.txt`)

```
Flask==2.0.1
scikit-learn==0.24.2
numpy==1.21.0
```

Estas versiones fueron desarrolladas para Python 3.7–3.9 y **no son compatibles** con entornos modernos (Python 3.11+).

### Entorno de pruebas utilizado

- Sistema Operativo: Windows 11
- Python: 3.11.9
- pip: 24.0 → actualizado a 26.1.2

---

## 🐞 Errores Detectados y Solucionados

Durante la puesta en marcha del sistema legado se identificaron y resolvieron los siguientes errores, en orden cronológico:

### 1. Fallo de instalación de dependencias
```
ModuleNotFoundError: No module named 'pkg_resources'
```
**Causa:** `scikit-learn==0.24.2` es incompatible con `setuptools`/Python 3.11.
**Solución:** actualización de `pip`, `setuptools` y `wheel`, e instalación de versiones modernas de las librerías (`Flask 3.x`, `scikit-learn 1.9.x`, `numpy 2.x`, `pandas 3.x`) dentro de un entorno virtual (`venv`).

### 2. Dependencia no declarada
```
ModuleNotFoundError: No module named 'requests'
```
**Causa:** `requests` es usado por `app/routes/recommendations.py` para consumir la API de TMDB, pero no estaba listado en `requirements.txt`.
**Solución:** instalación manual y posterior actualización del archivo de dependencias.

### 3. Archivos de datos faltantes
```
FileNotFoundError: tmdb_5000_credits.csv
```
**Causa:** el `.gitignore` original excluía `data/*.csv` y `data/*.db`, por lo que el repositorio no incluía los datasets requeridos por `config/config.py`.
**Solución:** se obtuvieron los datasets `tmdb_5000_movies.csv` y `tmdb_5000_credits.csv` (dataset de TMDB en Kaggle) y se colocaron en `data/`.

### 4. Inconsistencia de columnas entre datasets
```
KeyError: 'id'
```
**Causa:** el código asumía que `tmdb_5000_credits.csv` tenía una columna `id`, cuando en realidad se llama `movie_id`.
**Solución:** ajuste del merge para usar `left_on='id', right_on='movie_id'` entre ambos dataframes.

### 5. Firma de función inconsistente
```
TypeError: get_recommendations() takes from 0 to 3 positional arguments but 5 were given
```
**Causa:** `app/routes/recommendations.py` invocaba `get_recommendations()` con 5 argumentos posicionales (`genre, n, start_year, end_year, min_rating`), pero la función en `recommendation_service.py` solo aceptaba `genre, n, min_rating`.
**Solución:** alineación de la firma de la función con los parámetros realmente utilizados por la ruta.

### 6. Timeouts en llamadas a la API externa
```
Error searching movies: HTTPSConnectionPool(host='api.themoviedb.org', port=443): Read timed out.
```
**Causa:** latencia de red al consultar la API de TMDB sin manejo robusto de reintentos.
**Impacto:** actualmente manejado con `try/except` y `timeout=5`, pero sin reintento ni caché — señalado como punto de mejora.

---

## 🔎 Hallazgos Adicionales del Análisis

- **Documentación de instalación incompleta:** el `README.md` original no indicaba que debían descargarse los datasets, ni dónde obtenerlos ni dónde colocarlos.
- **`.gitignore` demasiado restrictivo:** excluía `data/*.db` y `data/*.csv`, dejando el repositorio incompleto e imposible de ejecutar solo con `git clone`.
- **Manejo deficiente de errores:** no existía validación previa de la existencia de los archivos CSV antes de intentar leerlos, ni mensajes descriptivos para el usuario.
- **Inconsistencia entre documentación y código:** el README mencionaba *"The Movies Dataset"* de forma genérica, mientras que el código requiere específicamente los archivos `tmdb_5000_movies.csv` y `tmdb_5000_credits.csv`, lo que puede llevar a descargar el dataset incorrecto.
- **Ausencia de automatización:** no había scripts que verificaran la integridad del entorno (dependencias, datasets, base de datos) antes de ejecutar la aplicación.

### Resumen de obsolescencia de dependencias

| Librería | Versión original | Situación |
|---|---|---|
| Flask | 2.0.1 | Desactualizada |
| Scikit-Learn | 0.24.2 | Incompatible con Python 3.11 |
| NumPy | 1.21.0 | Obsoleta para versiones recientes |

---

## 🚀 Arquitectura Propuesta (Reingeniería)

La modernización del sistema se aborda en 6 fases incrementales. Esta primera fase se enfoca en refactorización y organización del código; las siguientes (documentadas en fases posteriores del repositorio) cubren contenedorización, pruebas y despliegue.

**Cambios ya aplicados en esta fase:**

- ✅ Actualización de dependencias a versiones compatibles con Python 3.11+ (Flask 3.x, scikit-learn 1.9.x, numpy 2.x, pandas 3.x).
- ✅ `requirements.txt` corregido para incluir todas las dependencias reales del proyecto (`requests` incluido).
- ✅ Corrección de la firma de `get_recommendations()` para alinear rutas y servicios.
- ✅ Corrección del merge de datasets (`id` vs `movie_id`).
- ✅ Repositorio modular subido a GitHub, con separación clara entre `routes`, `services`, `data_processing`, `models` y `config`.

**Próximos pasos dentro del alcance de reingeniería:**

- 🔲 Centralizar toda la configuración sensible (API keys) en variables de entorno (`.env`), eliminando claves hardcodeadas de `config/config.py`.
- 🔲 Añadir validación de existencia de archivos de datos antes de iniciar la app, con mensajes de error claros.
- 🔲 Documentar y automatizar la descarga/colocación de los datasets (Kaggle - TMDB 5000 Movie Dataset).
- 🔲 Contenedorización con Docker (Fase 2).
- 🔲 Suite de pruebas unitarias con Pytest y cobertura ≥ 80% (Fase 3).
- 🔲 Pruebas E2E con Selenium (Fase 4).
- 🔲 Pipeline de CI/CD con GitHub Actions (Fase 5).
- 🔲 Endpoint de salud `/api/health` y despliegue en producción (Fase 6).

---

## ✨ Mejoras Funcionales Propuestas (Alcance Propio)

Además de los entregables obligatorios de la rúbrica, se identificó una limitación funcional en el sistema legado: el motor de búsqueda actual exige combinar múltiples filtros (título, género, calificación mínima) para generar una recomendación, lo cual con frecuencia **no arroja resultados** si el cruce de criterios es demasiado estricto. A partir de este hallazgo, se propone la siguiente mejora de experiencia de usuario y funcionalidad, como decisión propia fuera del alcance mínimo solicitado:

1. **Rediseño visual** de la interfaz hacia una estética moderna, tipo "sala de premiación" (inspirada en los Oscars), reemplazando el estilo genérico actual.
2. **Catálogo inicial visible**: la página mostrará una lista de películas destacadas desde el primer momento, sin necesidad de usar el buscador. Se aprovechará la función `get_top_movies()` (filtrado demográfico), actualmente implementada pero no conectada a la vista principal.
3. **Búsqueda por título con resultado + recomendaciones**: al buscar una película por nombre, la interfaz mostrará la película encontrada junto con sus recomendaciones asociadas (el motor de contenido/TMDB ya existente), en lugar de mostrar únicamente las recomendaciones.
4. **Búsqueda flexible por criterio único**: se ampliará el motor de búsqueda para permitir:
   - Buscar **solo por género**, listando todas las películas disponibles de esa categoría (aprovechando `Movie.get_movies_by_genre()`, ya definido en el modelo pero no expuesto en las rutas).
   - Buscar **solo por título**, sin exigir género ni calificación mínima como filtros obligatorios.

**Cambios técnicos que implica:**

| Cambio | Componente afectado |
|---|---|
| Nuevo endpoint / modificación de `/recommendations` para catálogo inicial | `app/routes/recommendations.py` |
| Exposición de `Movie.get_movies_by_genre()` en las rutas | `app/routes/recommendations.py`, `app/models/movie.py` |
| Parámetros de búsqueda opcionales e independientes (título y/o género) | `app/routes/recommendations.py` |
| Renderizado de la película buscada junto a sus recomendaciones | `static/js/main.js`, `templates/index.html` |
| Rediseño de estilos (paleta, tipografía, layout tipo alfombra roja) | `static/css/style.css` |

Este apartado se documentará con más detalle (capturas, decisiones de diseño) conforme avance su implementación.

---

## ⚙️ Instalación y Ejecución (Actualizada)

### 1. Clonar el repositorio

```bash
git clone https://github.com/cristian-eco/MRS-Reenginering.git
cd MRS-Reenginering
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Descargar los datasets

Este proyecto requiere el dataset **TMDB 5000 Movie Dataset** de Kaggle:
- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

Colocar ambos archivos dentro de la carpeta `data/`.

### 5. Crear la base de datos

```bash
python scripts/database_setup.py
```

### 6. Ejecutar la aplicación

```bash
python run.py
```

Visitar [http://localhost:5000](http://localhost:5000) en el navegador.

---

## 📚 Dataset

TMDB 5000 Movie Dataset (Kaggle) — incluye metadatos de películas (género, sinopsis, popularidad, calificación) y créditos (reparto y equipo técnico).

---

## 📄 Licencia

Este proyecto está licenciado bajo MIT License. Ver [LICENSE](LICENSE) para más detalles.
