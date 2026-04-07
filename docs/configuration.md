# Configuración del proyecto

Este documento describe las rutas del proyecto, los parámetros por defecto de análisis, el diccionario de sinónimos de keywords y la stoplist de keywords excluidas. Todo lo relevante vive en dos módulos:

- `src/co_occurrence/config.py` — rutas y modelo Pydantic `GraphDefaults`
- `src/co_occurrence/synonyms.py` — diccionario `KEYWORD_SYNONYMS` y conjunto `KEYWORD_STOPLIST`

---

## 1. Rutas del proyecto

Las rutas se calculan automáticamente a partir de la ubicación del propio módulo instalado, de modo que no dependen de dónde se invoque el paquete.

| Constante | Valor relativo a la raíz | Descripción |
|-----------|--------------------------|-------------|
| `PROJECT_ROOT` | `.` | Raíz del repositorio. Se resuelve como el directorio dos niveles por encima de `config.py` (es decir, `src/co_occurrence/` → `src/` → raíz). |
| `DATA_DIR` | `data/` | Carpeta donde se deposita el fichero fuente de WoS. No mover ni renombrar. |
| `DATA_FILE` | `data/anal multiv 331 artic completo.xlsx` | Fichero Excel con los 331 artículos exportados desde WoS. La hoja relevante es `savedrecs`. |
| `OUTPUT_DIR` | `output/` | Destino de todos los artefactos intermedios: grafos `.gexf`, CSVs de centralidades, matrices de co-ocurrencia, etc. Se crea automáticamente si no existe. |
| `VAULT_DIR` | `vault_bibliometria/` | Raíz del vault de Obsidian generado por `obsidian.py`. Contiene subcarpetas `keywords/`, `authors/`, `journals/` y `communities/`. |

Adicionalmente existe la constante `SHEET_NAME = "savedrecs"` y `MULTIVALUE_SEP = ";"`, que indica el separador usado por WoS en campos multi-valor (autores, keywords, países, referencias, etc.).

---

## 2. Modelo `GraphDefaults` (Pydantic)

`GraphDefaults` es un modelo Pydantic que centraliza todos los parámetros numéricos que controlan la construcción de grafos, la detección de comunidades y la reducción dimensional. Se instancia una única vez al importar el módulo:

```python
DEFAULTS = GraphDefaults()
```

### Campos

| Campo | Tipo | Valor por defecto | Descripción |
|-------|------|-------------------|-------------|
| `min_cooccurrence_weight` | `int` | `2` | Peso mínimo de una arista en el grafo de co-ocurrencia de keywords. Aristas con peso 1 se descartan porque pueden deberse a coincidencias espurias en un corpus pequeño (331 artículos). Subir este valor produce grafos más densos pero menos ruidosos. |
| `min_cocitation_weight` | `int` | `5` | Peso mínimo en la red de co-citación. Se usa un umbral más alto porque el espacio de referencias es mucho mayor que el de keywords, y los pares de co-citación esporádicos son muy abundantes. |
| `louvain_resolution` | `float` | `1.0` | Parámetro de resolución del algoritmo Louvain (y Leiden). Valores mayores que 1.0 tienden a producir más comunidades y más pequeñas; valores menores que 1.0 favorecen comunidades más grandes y genéricas. |
| `temporal_window_years` | `int` | `5` | Tamaño de la ventana deslizante (en años) para el análisis de evolución temporal. Cada ventana solapa con la anterior, lo que suaviza la detección de keywords emergentes o en declive. |
| `top_keywords_per_community` | `int` | `5` | Número de keywords representativas que se extraen por comunidad para el etiquetado semántico automático. Se seleccionan por centralidad de grado dentro de la comunidad. |
| `dimred_n_components` | `int` | `2` | Número de componentes (dimensiones) en la reducción dimensional (MDS, t-SNE, UMAP, CA). El valor 2 produce visualizaciones 2D directamente graficables con Plotly. |
| `dimred_random_state` | `int` | `42` | Semilla aleatoria para los algoritmos no deterministas (t-SNE, UMAP). Garantiza reproducibilidad entre ejecuciones. |

---

## 3. Diccionario de sinónimos (`KEYWORD_SYNONYMS`)

### Propósito

WoS recoge las keywords tal como las escriben los autores, lo que genera múltiples variantes ortográficas y abreviaciones para un mismo concepto. El diccionario `KEYWORD_SYNONYMS` en `synonyms.py` mapea cada variante a su forma canónica (siempre en minúsculas), de modo que el grafo de co-ocurrencia trate esas variantes como un único nodo.

La normalización se aplica en `preprocessing/normalize.py` antes de cualquier construcción de grafo. La forma canónica es la que aparece en los nodos, en el vault de Obsidian y en todas las tablas de salida.

### Estructura del diccionario

```python
KEYWORD_SYNONYMS: dict[str, str] = {
    "variante": "forma canónica",
    ...
}
```

Las claves son las variantes a reemplazar; los valores son las formas canónicas a las que se normalizan.

### Entradas por grupo temático

#### Modelado de ecuaciones estructurales (SEM)

| Variante | Forma canónica |
|----------|----------------|
| `"sem"` | `"structural equation modeling"` |
| `"structural equation model"` | `"structural equation modeling"` |
| `"structural equation modelling"` | `"structural equation modeling"` |
| `"structural equations"` | `"structural equation modeling"` |
| `"structural equations model"` | `"structural equation modeling"` |

#### PLS-SEM

| Variante | Forma canónica |
|----------|----------------|
| `"pls-sem"` | `"partial least squares"` |
| `"pls"` | `"partial least squares"` |
| `"partial least squares sem"` | `"partial least squares"` |
| `"partial least squares variant"` | `"partial least squares"` |

#### Análisis factorial

| Variante | Forma canónica |
|----------|----------------|
| `"efa"` | `"exploratory factor analysis"` |
| `"factor analysis"` | `"exploratory factor analysis"` |
| `"principle factor analysis"` | `"exploratory factor analysis"` |
| `"cfa"` | `"confirmatory factor analysis"` |

#### Análisis de componentes principales

| Variante | Forma canónica |
|----------|----------------|
| `"pca"` | `"principal component analysis"` |
| `"categorical principal components analysis"` | `"principal component analysis"` |

#### Clustering

| Variante | Forma canónica |
|----------|----------------|
| `"clustering"` | `"cluster analysis"` |
| `"clustering methods"` | `"cluster analysis"` |
| `"multivariate clustering"` | `"cluster analysis"` |
| `"cluster fuzzy k-means"` | `"cluster analysis"` |
| `"k-means"` | `"cluster analysis"` |
| `"model-based cluster analysis"` | `"cluster analysis"` |
| `"hierarchical clustering"` | `"hierarchical cluster analysis"` |

#### Análisis discriminante

| Variante | Forma canónica |
|----------|----------------|
| `"fisher discriminant analysis"` | `"discriminant analysis"` |

#### Análisis de varianza

| Variante | Forma canónica |
|----------|----------------|
| `"manova"` | `"multivariate analysis of variance"` |
| `"anova"` | `"analysis of variance"` |

#### Regresión (general)

| Variante | Forma canónica |
|----------|----------------|
| `"regression"` | `"regression analysis"` |
| `"linear regression"` | `"regression analysis"` |
| `"multiple regression analysis"` | `"multiple regression"` |
| `"multiple linear regression"` | `"multiple regression"` |
| `"multivariate linear regression"` | `"multiple regression"` |
| `"multivariate linear regression model"` | `"multiple regression"` |
| `"multivariate linear regression analysis"` | `"multiple regression"` |
| `"multivariate regression"` | `"multiple regression"` |
| `"multivariate regression models"` | `"multiple regression"` |
| `"multivariate regression analyses"` | `"multiple regression"` |
| `"multivariate multiple regression"` | `"multiple regression"` |
| `"multivariate regression analysis"` | `"multiple regression"` |
| `"panel data multivariate regression analyses"` | `"multiple regression"` |

#### Regresión logística

| Variante | Forma canónica |
|----------|----------------|
| `"logistic regression"` | `"logistic regression analysis"` |
| `"logit"` | `"logistic regression analysis"` |
| `"multinominal logit model"` | `"logistic regression analysis"` |
| `"multinomial logistic regression"` | `"logistic regression analysis"` |
| `"probit"` | `"logistic regression analysis"` |
| `"multivariate probit analysis"` | `"logistic regression analysis"` |

#### Regresión cuantílica

| Variante | Forma canónica |
|----------|----------------|
| `"quantile regression analysis"` | `"quantile regression"` |

#### Análisis de correspondencias

| Variante | Forma canónica |
|----------|----------------|
| `"multi-correspondence analysis"` | `"multiple correspondence analysis"` |
| `"mca"` | `"multiple correspondence analysis"` |
| `"ca"` | `"correspondence analysis"` |

#### Escalado multidimensional

| Variante | Forma canónica |
|----------|----------------|
| `"mds"` | `"multidimensional scaling"` |
| `"multidimensional analysis"` | `"multidimensional scaling"` |

#### Análisis envolvente de datos (DEA)

| Variante | Forma canónica |
|----------|----------------|
| `"dea"` | `"data envelopment analysis"` |
| `"data envelopment analysis (dea)"` | `"data envelopment analysis"` |

#### Eficiencia

| Variante | Forma canónica |
|----------|----------------|
| `"efficiency assessment"` | `"efficiency"` |
| `"labor efficiency"` | `"efficiency"` |

#### VAR / series temporales

| Variante | Forma canónica |
|----------|----------------|
| `"vector autoregressive model"` | `"vector autoregression"` |
| `"vector autoregression model"` | `"vector autoregression"` |
| `"unrestricted vector autoregressive model"` | `"vector autoregression"` |
| `"var"` | `"vector autoregression"` |
| `"vecm"` | `"vector autoregression"` |

#### Singular Spectrum Analysis

| Variante | Forma canónica |
|----------|----------------|
| `"multivariate singular spectrum analysis"` | `"singular spectrum analysis"` |
| `"mssa"` | `"singular spectrum analysis"` |
| `"ssa"` | `"singular spectrum analysis"` |

#### Cointegración y datos de panel

| Variante | Forma canónica |
|----------|----------------|
| `"cointegration test"` | `"cointegration"` |
| `"panel data analysis"` | `"panel data"` |
| `"panel data model"` | `"panel data"` |

#### Causalidad de Granger

| Variante | Forma canónica |
|----------|----------------|
| `"asymmetric granger causality"` | `"granger causality"` |
| `"symmetric and asymmetric granger causality test"` | `"granger causality"` |
| `"bootstrap multivariate asymmetric panel granger causality test"` | `"granger causality"` |
| `"panel causality"` | `"granger causality"` |

#### Importance-Performance Analysis

| Variante | Forma canónica |
|----------|----------------|
| `"ipa"` | `"importance-performance analysis"` |
| `"importance performance analysis"` | `"importance-performance analysis"` |

#### AHP / ANP

| Variante | Forma canónica |
|----------|----------------|
| `"ahp"` | `"analytic hierarchy process"` |
| `"anp"` | `"analytic network process"` |
| `"anp and improved-topsis"` | `"analytic network process"` |

#### Redes neuronales

| Variante | Forma canónica |
|----------|----------------|
| `"neural network"` | `"artificial neural network"` |
| `"ann"` | `"artificial neural network"` |
| `"lssvm"` | `"support vector machine"` |
| `"two-stage hybrid sem-ann"` | `"artificial neural network"` |

#### Fuzzy QCA / QCA

| Variante | Forma canónica |
|----------|----------------|
| `"fsqca"` | `"fuzzy-set qualitative comparative analysis"` |
| `"fuzzy set"` | `"fuzzy-set qualitative comparative analysis"` |
| `"fuzzy set/qualitative comparative analysis (fs/qca)"` | `"fuzzy-set qualitative comparative analysis"` |
| `"clear-set qualitative comparative analysis (csqca)"` | `"qualitative comparative analysis"` |
| `"configurational analysis"` | `"qualitative comparative analysis"` |

#### Social Network Analysis

| Variante | Forma canónica |
|----------|----------------|
| `"sna"` | `"social network analysis"` |
| `"network approach"` | `"social network analysis"` |

#### Mediación / Moderación

| Variante | Forma canónica |
|----------|----------------|
| `"mediation analysis"` | `"mediation"` |
| `"multi-group analysis"` | `"moderation"` |

#### Calidad de servicio

| Variante | Forma canónica |
|----------|----------------|
| `"servqual"` | `"service quality"` |

#### Análisis multivariado (genérico)

| Variante | Forma canónica |
|----------|----------------|
| `"multivariate statistical analysis"` | `"multivariate analysis"` |
| `"multivariate statistics"` | `"multivariate analysis"` |
| `"multivariate statistical"` | `"multivariate analysis"` |
| `"multivariate statistical data analysis"` | `"multivariate analysis"` |
| `"multivariate statistical techniques"` | `"multivariate analysis"` |
| `"multivariate analyses"` | `"multivariate analysis"` |
| `"spatial multivariate analysis"` | `"multivariate analysis"` |
| `"quantitative methods"` | `"multivariate analysis"` |
| `"statistical analysis"` | `"multivariate analysis"` |
| `"multivariate time-series"` | `"multivariate time series"` |
| `"multivariate time series clustering"` | `"multivariate time series"` |

#### Demanda y previsión turística

| Variante | Forma canónica |
|----------|----------------|
| `"tourism demand"` | `"tourism demand forecasting"` |
| `"demand forecasting"` | `"tourism demand forecasting"` |
| `"demand"` | `"tourism demand forecasting"` |
| `"short term tourism demand forecast"` | `"tourism demand forecasting"` |
| `"interpretable tourism demand forecasting"` | `"tourism demand forecasting"` |
| `"tourism demands"` | `"tourism demand forecasting"` |

#### COVID-19

| Variante | Forma canónica |
|----------|----------------|
| `"covid-19 pandemic"` | `"covid-19"` |
| `"pandemic covid-19"` | `"covid-19"` |
| `"after covid-19 tourism"` | `"covid-19"` |
| `"coronavirus"` | `"covid-19"` |
| `"covid-19 vaccination"` | `"covid-19"` |
| `"covid-19 vaccine"` | `"covid-19"` |

#### Satisfacción

| Variante | Forma canónica |
|----------|----------------|
| `"tourist satisfaction"` | `"satisfaction"` |
| `"customer satisfaction"` | `"satisfaction"` |
| `"trip satisfaction"` | `"satisfaction"` |
| `"visitors' satisfaction"` | `"satisfaction"` |

#### Motivación

| Variante | Forma canónica |
|----------|----------------|
| `"motivations"` | `"motivation"` |
| `"generic motivation"` | `"motivation"` |
| `"travelmotivation"` | `"motivation"` |
| `"recreation motivation"` | `"motivation"` |
| `"protection motivation"` | `"motivation"` |

#### Lealtad

| Variante | Forma canónica |
|----------|----------------|
| `"destination loyalty"` | `"loyalty"` |
| `"loyalty programmes"` | `"loyalty"` |

#### Segmentación

| Variante | Forma canónica |
|----------|----------------|
| `"market segmentation"` | `"segmentation"` |
| `"customer segmentation"` | `"segmentation"` |
| `"visitor segmentation"` | `"segmentation"` |
| `"activity-based segmentation"` | `"segmentation"` |
| `"tourism segmentation"` | `"segmentation"` |

#### Imagen de destino

| Variante | Forma canónica |
|----------|----------------|
| `"affective image"` | `"destination image"` |
| `"destination brand perception"` | `"destination image"` |
| `"touristic image"` | `"destination image"` |

#### Competitividad

| Variante | Forma canónica |
|----------|----------------|
| `"tourism competitiveness"` | `"competitiveness"` |
| `"destinations' competitiveness"` | `"competitiveness"` |

#### Hostelería

| Variante | Forma canónica |
|----------|----------------|
| `"hospitality industry"` | `"hospitality"` |
| `"hotel industry"` | `"hospitality"` |
| `"hospitality and tourism"` | `"hospitality"` |
| `"hospitality and tourism management"` | `"hospitality"` |
| `"hospitality and tourism employees"` | `"hospitality"` |

#### Reseñas online

| Variante | Forma canónica |
|----------|----------------|
| `"user-generated reviews"` | `"online reviews"` |

#### Comportamiento del consumidor

| Variante | Forma canónica |
|----------|----------------|
| `"consumer behaviour"` | `"consumer behavior"` |
| `"consuming behavior"` | `"consumer behavior"` |

#### Ecoturismo

| Variante | Forma canónica |
|----------|----------------|
| `"ecotourism development"` | `"ecotourism"` |
| `"ecotourismintention"` | `"ecotourism"` |

#### Turismo rural / agroturismo

| Variante | Forma canónica |
|----------|----------------|
| `"agri-tourism"` | `"agritourism"` |
| `"agritourism operations"` | `"agritourism"` |

#### Turismo gastronómico

| Variante | Forma canónica |
|----------|----------------|
| `"gastronomy tourism"` | `"gastronomy"` |
| `"gastronomic tourism"` | `"gastronomy"` |
| `"culinary tourism"` | `"gastronomy"` |
| `"food tourism"` | `"gastronomy"` |

#### Patrimonio

| Variante | Forma canónica |
|----------|----------------|
| `"world heritage site"` | `"world heritage sites"` |
| `"whs"` | `"world heritage sites"` |
| `"historical and cultural heritage"` | `"cultural heritage"` |
| `"unesco heritage"` | `"cultural heritage"` |

#### Intención de comportamiento

| Variante | Forma canónica |
|----------|----------------|
| `"travel intention"` | `"behavioral intention"` |
| `"travel intentions"` | `"behavioral intention"` |
| `"intention"` | `"behavioral intention"` |
| `"revisit intention"` | `"behavioral intention"` |
| `"revisit intentions"` | `"behavioral intention"` |
| `"travelers' intention"` | `"behavioral intention"` |
| `"green travel intention"` | `"behavioral intention"` |
| `"entrepreneurial intention"` | `"behavioral intention"` |

#### Percepción

| Variante | Forma canónica |
|----------|----------------|
| `"residents' perceptions"` | `"perception"` |
| `"impact perception"` | `"perception"` |

#### Bienestar / Calidad de vida

| Variante | Forma canónica |
|----------|----------------|
| `"wellbeing"` | `"well-being"` |
| `"quality of life"` | `"well-being"` |
| `"quality of life (qol)"` | `"well-being"` |
| `"happiness"` | `"well-being"` |

#### Teoría del comportamiento planificado

| Variante | Forma canónica |
|----------|----------------|
| `"theory of planned behaviour (tpb)"` | `"theory of planned behavior"` |

#### Otros

| Variante | Forma canónica |
|----------|----------------|
| `"conjoint"` | `"conjoint analysis"` |
| `"som"` | `"self-organizing maps"` |
| `"perceptual maps"` | `"biplot"` |
| `"co2 emissions"` | `"carbon emissions"` |
| `"carbon dioxide emission"` | `"carbon emissions"` |
| `"sustainable development goals"` | `"sustainable development"` |
| `"revenue management"` | `"revenue management"` |

### Total de entradas

El diccionario contiene **~160 entradas** distribuidas en los grupos anteriores.

### Detección de nuevos candidatos

Para detectar posibles nuevas variantes en el corpus, ejecutar:

```bash
python -c "from co_occurrence.preprocessing.normalize import build_synonym_candidates; build_synonym_candidates()"
```

Esto genera una lista de pares de keywords con alta similitud léxica que podrían unificarse.

---

## 4. Stoplist de keywords (`KEYWORD_STOPLIST`)

### Propósito

`KEYWORD_STOPLIST` es un conjunto (`set[str]`) exportado desde `synonyms.py` que recoge keywords que **no deben aparecer como nodos** en ningún grafo de co-ocurrencia. La función `normalize_keyword` de `preprocessing/normalize.py` devuelve la cadena vacía `""` cuando la keyword normalizada está en la stoplist; el pipeline descarta automáticamente cualquier keyword cuya forma normalizada sea vacía.

Los criterios de inclusión en la stoplist son:

- **Ruido geográfico**: nombres de países, regiones, ciudades o accidentes geográficos que solo indican el contexto espacial del estudio y no tienen contenido temático-metodológico relevante para el corpus.
- **Términos demasiado genéricos**: palabras como `"study"`, `"quality"` o `"impact"` que aparecen en tantos contextos distintos que no aportan estructura semántica al grafo.

### Estructura

```python
KEYWORD_STOPLIST: set[str] = {
    "china",
    "spain",
    "study",
    ...
}
```

Todas las entradas están en minúsculas. La normalización se aplica antes de la consulta, por lo que no es necesario añadir variantes en mayúsculas.

### Entradas por categoría

#### Nombres geográficos

Países, regiones, ciudades y accidentes geográficos identificados en el corpus. Ejemplos representativos:

| Entrada |
|---------|
| `"asia"` |
| `"asia pacific"` |
| `"brazil"` |
| `"canada"` |
| `"china"` |
| `"china's provinces"` |
| `"colombia"` |
| `"croatia"` |
| `"eastern europe"` |
| `"ecuador"` |
| `"europe"` |
| `"greece"` |
| `"iceland"` |
| `"india"` |
| `"indonesia"` |
| `"italy"` |
| `"jordan"` |
| `"kazakhstan"` |
| `"korea"` |
| `"latin america"` |
| `"mediterranean"` |
| `"mexico"` |
| `"new zealand"` |
| `"poland"` |
| `"portugal"` |
| `"south africa"` |
| `"spain"` |
| `"taiwan"` |
| `"thailand"` |
| `"the philippines"` |
| `"turkey"` |
| `"uk"` |
| `"united kingdom"` |
| `"united states"` |
| `"vietnam"` |
| `"andaman sea"` |
| `"huangshan"` |
| `"mekong delta"` |
| `"rio de janeiro"` |
| `"washington, dc"` |

La lista completa incluye también topónimos más específicos (comarcas, ríos, parques naturales) detectados en el corpus.

#### Términos genéricos y de ruido

Palabras que aparecen con alta frecuencia transversal pero no articulan estructura temática:

| Entrada | Motivo de exclusión |
|---------|---------------------|
| `"study"` | Metapalabra sin contenido disciplinar |
| `"keywords"` | Artefacto del campo WoS |
| `"factor"` | Demasiado genérico |
| `"assessment"` | Sin precisión metodológica |
| `"validation"` | Proceso transversal a múltiples métodos |
| `"modeling"` | Genérico; los métodos concretos ya tienen entrada propia |
| `"set"` | Ambiguo |
| `"impact"` | Omnipresente, no discrimina tema |
| `"nodes"` | Artefacto de análisis de redes |
| `"space"` | Polisémico |
| `"region"` | Geográfico genérico |
| `"challenges"` | No metodológico |
| `"determinant factors"` | Redundante con otras entradas |
| `"key factors"` | Redundante con otras entradas |
| `"influencing factors"` | Redundante con otras entradas |
| `"trends"` | Genérico |
| `"quality"` | Polisémico (calidad hotelera, calidad metodológica, etc.) |
| `"interest"` | Genérico |
| `"driver"` | Genérico |
| `"experiences"` | Polisémico |
| `"experience"` | Polisémico |

### Total de entradas

La stoplist contiene **~90 entradas** (~65 geográficas y ~20 genéricas).

---

## 5. Cómo modificar la configuración

### Cambiar parámetros de análisis en tiempo de ejecución

`DEFAULTS` es un singleton de nivel de módulo. Se puede modificar antes de llamar a cualquier función del pipeline para sobreescribir los valores por defecto sin tocar el código fuente:

```python
from co_occurrence.config import DEFAULTS

# Ejemplo: exigir más evidencia en co-ocurrencia y más comunidades
DEFAULTS.min_cooccurrence_weight = 3
DEFAULTS.louvain_resolution = 1.2
DEFAULTS.temporal_window_years = 3
```

Todos los módulos que aceptan parámetros opcionales los leen de `DEFAULTS` si no se les pasa un valor explícito, por lo que el cambio se propaga automáticamente al resto del pipeline.

### Cambiar parámetros de forma permanente

Editar directamente los valores por defecto en `src/co_occurrence/config.py`:

```python
class GraphDefaults(BaseModel):
    min_cooccurrence_weight: int = 3   # cambiado de 2 a 3
    ...
```

### Ampliar o corregir el diccionario de sinónimos

Editar `src/co_occurrence/synonyms.py` directamente. El archivo está separado del resto del código precisamente para facilitar esta edición sin necesidad de tocar lógica de negocio. Convenciones a respetar:

- Las claves (variantes) deben estar en minúsculas.
- Los valores (formas canónicas) deben estar en minúsculas.
- Agrupar las entradas por tema con un comentario de sección.
- No duplicar claves; Python conservará solo la última si se repiten.

Ejemplo de nueva entrada:

```python
# Análisis de componentes principales
"pca": "principal component analysis",
"principal components": "principal component analysis",
```

Tras modificar el diccionario, volver a ejecutar el pipeline desde el paso de normalización para que los grafos reflejen los cambios.

### Ampliar la stoplist

Añadir entradas directamente al conjunto `KEYWORD_STOPLIST` en `src/co_occurrence/synonyms.py`. Convenciones a respetar:

- Las entradas deben estar en minúsculas (la normalización se aplica antes de la consulta).
- Agrupar por categoría (geográficas / genéricas) respetando los comentarios de sección existentes.
- Una keyword que ya tiene una entrada en `KEYWORD_SYNONYMS` no necesita estar también en la stoplist; son mecanismos complementarios.

Tras modificar la stoplist, volver a ejecutar el pipeline desde el paso de normalización.
