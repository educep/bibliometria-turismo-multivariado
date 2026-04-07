# Arquitectura de `co-occurrence-library`

## 1. Visión general

`co_occurrence` es un paquete Python para análisis bibliométrico multivariado aplicado a turismo. Opera sobre un corpus de 331 artículos exportados desde Web of Science (WoS). El análisis comprende construcción de grafos de co-ocurrencia, detección de comunidades, reducción dimensional y generación de visualizaciones interactivas para publicación web con Quarto.

El paquete sigue el layout estándar `src/` de setuptools:

```
src/
└── co_occurrence/          ← paquete instalable
```

El punto de entrada CLI es `python -m co_occurrence` (via `__main__.py`).

---

## 2. Módulos y responsabilidades

### `config.py`

Configuración central del paquete. Define el modelo Pydantic `GraphDefaults` con los parámetros por defecto del pipeline:

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `min_cooccurrence_weight` | `1` | Peso mínimo de arista en grafos de co-ocurrencia |
| `louvain_resolution` | `1.0` | Resolución del algoritmo Louvain |
| `temporal_window_years` | `5` | Tamaño de la ventana temporal en años |

También define constantes de rutas (`pathlib.Path`):

- `DATA_DIR` — directorio de datos fuente
- `OUTPUT_DIR` — directorio de salidas intermedias (grafos, CSVs)
- `VAULT_DIR` — directorio del vault Obsidian

### `synonyms.py`

Diccionario `KEYWORD_SYNONYMS` con aproximadamente 160 sinónimos para normalizar variantes ortográficas y terminológicas de keywords bibliométricos, más `KEYWORD_STOPLIST` (~90 términos) con términos genéricos que se eliminan del análisis. Está separado del código de normalización para facilitar su edición sin tocar lógica de negocio.

### `io/loader.py`

Carga y limpieza inicial de los datos WoS.

- `load_wos_data()` — lee el archivo Excel (`anal multiv 331 artic completo.xlsx`, hoja `savedrecs`) con `openpyxl`. Devuelve un `pd.DataFrame` con las columnas WoS originales.

### `preprocessing/parse.py`

Parseo de campos multi-valor propios del formato WoS.

- `parse_multivalue(series, sep=";")` — divide campos separados por punto y coma en listas de valores limpios.
- `extract_countries_from_addresses(addresses)` — extrae países a partir del campo de afiliaciones institucionales WoS.

### `preprocessing/normalize.py`

Normalización y deduplicación de keywords.

- `normalize_keyword(kw)` — aplica lowercase, strip y sustitución por sinónimos. Devuelve `""` si el término está en `KEYWORD_STOPLIST`.
- `normalize_keyword_series(series)` — aplica la normalización sobre una `pd.Series` de listas de keywords.
- `build_synonym_candidates(series)` — genera candidatos a sinónimos nuevos por similitud léxica, para ampliar `KEYWORD_SYNONYMS`.

### `graphs/cooccurrence.py`

Construcción del grafo principal del análisis.

- `build_cooccurrence_graph(keyword_lists, min_weight)` — itera sobre las listas de keywords de cada artículo, genera combinaciones de pares con `itertools.combinations` y acumula co-ocurrencias como peso de arista. Devuelve un `nx.Graph`.

### `graphs/coauthor.py`

- `build_coauthor_graph(author_lists, min_weight)` — construye la red de co-autoría. Los nodos son autores; las aristas representan artículos compartidos.

### `graphs/cocitation.py`

- `build_cocitation_graph(citation_lists, min_weight)` — construye la red de co-citación. Dos referencias co-aparecen cuando son citadas juntas en el mismo artículo.

### `graphs/bipartite.py`

Grafos bipartitos para relacionar entidades heterogéneas.

- `build_bipartite_graph(left_list, right_list)` — constructor genérico.
- Tres wrappers de conveniencia:
  - `build_author_keyword_graph()` — autores × keywords
  - `build_journal_keyword_graph()` — revistas × keywords
  - `build_country_keyword_graph()` — países × keywords

### `graphs/weights.py`

Normalización de pesos de co-ocurrencia. Todas las funciones reciben un `nx.Graph` y devuelven el mismo grafo con el atributo de arista normalizado añadido.

| Función | Fórmula | Uso recomendado |
|---|---|---|
| `association_strength(G)` | `w(a,b) / (f(a) · f(b))` | Layout de grafo |
| `jaccard_weight(G)` | `w(a,b) / (f(a) + f(b) − w(a,b))` | Detección de comunidades |
| `salton_cosine(G)` | `w(a,b) / √(f(a) · f(b))` | Similitud simétrica |
| `inclusion_index(G)` | `w(a,b) / min(f(a), f(b))` | Relaciones asimétricas |
| `apply_all_normalizations(G)` | — | Calcula las cuatro métricas de una vez |

### `analysis/communities.py`

Detección de comunidades temáticas (importaciones lazy de `igraph` y `leidenalg`).

- `detect_louvain(G, resolution)` — algoritmo Louvain via `python-louvain`. Devuelve `dict[node, community_id]`.
- `detect_leiden(G, resolution)` — convierte el grafo a `igraph` internamente y aplica el algoritmo Leiden (mejor calidad de modularidad). Devuelve `dict[node, community_id]`.
- `label_communities(G, partition)` — asigna una etiqueta semántica a cada comunidad basándose en los keywords más centrales del subgrafo.

### `analysis/centrality.py`

Métricas de centralidad de nodos.

- `compute_centralities(G)` — calcula degree, betweenness, eigenvector y PageRank. Devuelve un `pd.DataFrame` con una fila por nodo.
- `compute_structural_holes(G)` — calcula el constraint de Burt para identificar nodos con posición de puente estructural.

### `analysis/temporal.py`

Análisis de evolución temporal del corpus.

- `build_temporal_graphs(df, window_years)` — construye un grafo de co-ocurrencia por ventana temporal deslizante.
- `keyword_evolution_metrics(temporal_graphs)` — calcula frecuencia y centralidad de cada keyword a lo largo del tiempo.
- `detect_emerging_declining(evolution_metrics)` — identifica keywords emergentes (crecimiento sostenido) y en declive (caída sostenida) mediante regresión de tendencia.

### `dimred/manifold.py`

Reducción dimensional no lineal sobre la matriz de co-ocurrencia (importaciones lazy de `sklearn` y `umap`).

- `reduce_mds(matrix, n_components)` — Multidimensional Scaling.
- `reduce_tsne(matrix, n_components, perplexity)` — t-SNE.
- `reduce_umap(matrix, n_components, n_neighbors)` — UMAP.

### `dimred/correspondence.py`

Análisis de correspondencias para biplots (importación lazy de `prince`).

- `compute_ca(df, row_column, col_column)` — construye tabla de contingencia desde el DataFrame WoS, detecta y salta dimensiones degeneradas (eigenvalue >= 0.99), y proyecta filas y columnas en el mismo espacio CA. Devuelve coordenadas con frecuencia marginal, contribucion a la inercia y % de inercia explicada.

### `topics/modeling.py`

Modelado de tópicos sobre abstracts (importación lazy de `bertopic`).

- `fit_lda(texts, n_topics)` — LDA con `sklearn.decomposition.LatentDirichletAllocation`.
- `fit_bertopic(texts, n_topics)` — BERTopic con embeddings de lenguaje.

### `viz/`

Funciones de visualización reutilizables para Quarto. Todas las dependencias (`plotly`, `pyvis`, `matplotlib`) se importan de forma lazy dentro de cada función.

| Módulo | Responsabilidad |
|---|---|
| `plotly_graphs.py` | Grafos interactivos de co-ocurrencia con Plotly (nodos coloreados por comunidad, tamaño por centralidad) |
| `plotly_scatter.py` | Scatter plots de centralidades y biplots de CA |
| `pyvis_net.py` | Export de grafos a HTML interactivo con PyVis |
| `export.py` | Export a GEXF (Gephi) y CSV de métricas de nodos/aristas |

### `obsidian.py`

Generador del vault Obsidian para exploración personal del corpus.

Produce notas Markdown con YAML frontmatter (`type`, `frequency`, `degree`, `betweenness`, `community`, `tags`) y wikilinks `[[keyword]]` que generan aristas en el Graph View de Obsidian. El INDEX incluye queries Dataview.

Estructura generada:

```
vault_bibliometria/
├── keywords/
├── authors/
├── journals/
└── communities/
```

### `cli.py`

Interfaz de linea de comandos construida con Typer. Expone 10 comandos:

| Comando | Descripcion |
|---|---|
| `load` | Verifica la carga del archivo Excel WoS |
| `build-keywords` | Construye el grafo de co-ocurrencia de keywords |
| `build-coauthors` | Construye la red de co-autoria |
| `communities` | Detecta comunidades (Louvain / Leiden) |
| `centralities` | Calcula metricas de centralidad |
| `evolution` | Analisis de evolucion temporal |
| `dimred` | Reduccion dimensional (MDS, t-SNE, UMAP) |
| `ca` | Analisis de Correspondencias (biplot keyword x revista) |
| `vault` | Genera vault Obsidian |
| `pipeline` | Ejecuta el pipeline completo de extremo a extremo |

---

## 3. Flujo de datos

```
Excel WoS (savedrecs)
        │
        ▼
  io/loader.py
  load_wos_data()
        │ pd.DataFrame (331 filas, ~70 columnas)
        ▼
  preprocessing/parse.py
  parse_multivalue()
  extract_countries_from_addresses()
        │ listas Python por campo (keywords, autores, países…)
        ▼
  preprocessing/normalize.py
  normalize_keyword_series()
        │ keywords normalizados y deduplicados
        ▼
  graphs/
  build_cooccurrence_graph()   ──→  nx.Graph (keyword–keyword)
  build_coauthor_graph()       ──→  nx.Graph (autor–autor)
  build_cocitation_graph()     ──→  nx.Graph (referencia–referencia)
  build_bipartite_graph()      ──→  nx.Graph bipartito
        │
        ▼
  graphs/weights.py
  apply_all_normalizations()
        │ grafos con atributos AS, Jaccard, Salton, Inclusion
        ▼
  analysis/communities.py      ──→  partition dict
  analysis/centrality.py       ──→  pd.DataFrame métricas
  analysis/temporal.py         ──→  dict de grafos por ventana
        │
        ├──→  viz/plotly_graphs.py   ──→  figuras Plotly (Quarto)
        ├──→  viz/export.py          ──→  .gexf (Gephi) + .csv (tablas)
        ├──→  dimred/manifold.py     ──→  coordenadas 2D/3D
        ├──→  dimred/correspondence.py ──→ biplot CA
        ├──→  topics/modeling.py     ──→  tópicos LDA/BERTopic
        └──→  obsidian.py            ──→  vault Markdown Obsidian
```

Los archivos intermedios (grafos serializados en GEXF, CSVs de centralidades) se almacenan en `output/`. Los outputs de Quarto van a `_site/` (directorio generado, no versionado).

### Páginas Quarto

El sitio web se construye con 8 páginas `.qmd` en la raíz del proyecto, configuradas en `_quarto.yml`:

| Página | Contenido |
|---|---|
| `index.qmd` | Resumen ejecutivo: estadísticas clave y navegación |
| `01_datos.qmd` | Descripción del corpus: distribución temporal, revistas, cobertura |
| `02_coocurrencia.qmd` | Grafo interactivo (Plotly + PyVis), estadísticas de red |
| `03_comunidades.qmd` | Comunidades Louvain: treemap, tabla, interpretación |
| `04_centralidades.qmd` | Degree vs betweenness, structural holes, tablas interactivas |
| `05_reduccion_dim.qmd` | Tabset MDS / t-SNE / UMAP / CA con gráficos interactivos |
| `06_evolucion.qmd` | Evolución temporal, keywords emergentes/en declive |
| `about.qmd` | Autor, metodología, herramientas, reproducibilidad |

Las páginas importan directamente desde el paquete `co_occurrence` instalado y leen los CSVs precalculados de `output/`. Deploy con `deploy.sh` → S3.

---

## 4. Dependencias opcionales y carga lazy

Para evitar errores de importación cuando paquetes pesados no están instalados, los módulos opcionales aplican importaciones lazy: el `import` se realiza dentro de la función que lo necesita, no en el nivel de módulo.

| Grupo | Paquetes | Módulos afectados |
|---|---|---|
| `viz` | `plotly`, `pyvis`, `matplotlib` | `viz/plotly_graphs.py`, `viz/plotly_scatter.py`, `viz/pyvis_net.py` |
| `dimred` | `scikit-learn`, `umap-learn`, `prince` | `dimred/manifold.py`, `dimred/correspondence.py` |
| `communities` | `igraph`, `leidenalg`, `python-louvain` | `analysis/communities.py` |
| `topics` | `bertopic` | `topics/modeling.py` |
| `publish` | `itables` | exportación para páginas Quarto |

Patrón aplicado:

```python
def reduce_umap(matrix: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Reduce dimensionality with UMAP."""
    import umap  # lazy import
    reducer = umap.UMAP(n_components=n_components)
    return reducer.fit_transform(matrix)
```

---

## 5. Convenciones

### Representación de grafos

- **networkx** es la representación canónica en todo el paquete. Todos los módulos reciben y devuelven objetos `nx.Graph` o `nx.DiGraph`.
- **igraph** se usa exclusivamente dentro de `analysis/communities.py` para ejecutar el algoritmo Leiden, que requiere esa biblioteca. La conversión `nx → igraph → nx` es interna al módulo.

### Logging

Se usa **loguru** en todos los módulos. Nunca `print()`. Ejemplo:

```python
from loguru import logger

logger.info("Grafo construido: {} nodos, {} aristas", G.number_of_nodes(), G.number_of_edges())
```

### Configuración y validación

- **pydantic** se usa para validar configuración (`config.py`) y parámetros de entrada en las fronteras del sistema (CLI, carga de datos).
- Los settings se instancian una vez y se pasan explícitamente; no se usa estado global mutable.

### Rutas de archivo

- Se usa **`pathlib.Path`** en todo el código. Nunca strings para rutas.
- Los paths relativos al proyecto se resuelven desde las constantes definidas en `config.py`.

### Encoding y formato de datos

- Encoding UTF-8 en todos los archivos.
- Separador de campos multi-valor WoS: `;` (punto y coma).
- Keywords siempre en **lowercase** tras la normalización.
- Peso mínimo por defecto en aristas de co-ocurrencia: `min_weight=1`, frecuencia mínima de nodo: `min_frequency=2`.

### Exports

| Formato | Uso |
|---|---|
| `.gexf` | Grafos para visualización en Gephi |
| `.csv` | Tablas de métricas (centralidad, comunidades) |
| `.html` | Grafos interactivos PyVis |
| `.md` | Notas del vault Obsidian |
