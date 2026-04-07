# Referencia de API — co-occurrence-library

Documentación completa de todas las funciones y clases públicas del paquete `co_occurrence`.
Corpus: 331 artículos WoS sobre turismo y técnicas multivariadas.

---

## Índice

1. [config](#1-config)
2. [io.loader](#2-ioloader)
3. [preprocessing.parse](#3-preprocessingparse)
4. [preprocessing.normalize](#4-preprocessingnormalize)
5. [graphs.cooccurrence](#5-graphscooccurrence)
6. [graphs.coauthor](#6-graphscoauthor)
7. [graphs.cocitation](#7-graphscocitation)
8. [graphs.bipartite](#8-graphsbipartite)
9. [graphs.weights](#9-graphsweights)
10. [analysis.communities](#10-analysiscommunities)
11. [analysis.centrality](#11-analysiscentrality)
12. [analysis.temporal](#12-analysistemporal)
13. [dimred.manifold](#13-dimredmanifold)
14. [dimred.correspondence](#14-dimredcorrespondence)
15. [topics.modeling](#15-topicsmodeling)
16. [viz.plotly_graphs](#16-vizplotly_graphs)
17. [viz.plotly_scatter](#17-vizplotly_scatter)
18. [viz.pyvis_net](#18-vizpyvis_net)
19. [viz.export](#19-vizexport)
20. [obsidian](#20-obsidian)

---

## 1. `config`

Módulo de configuración global: paths del proyecto y parámetros por defecto para la construcción y el análisis de grafos.

### Constantes de ruta

| Constante | Tipo | Descripción |
|-----------|------|-------------|
| `PROJECT_ROOT` | `Path` | Raíz del proyecto (dos niveles sobre `config.py`) |
| `DATA_DIR` | `Path` | Directorio `data/` |
| `DATA_FILE` | `Path` | Archivo Excel WoS: `data/anal multiv 331 artic completo.xlsx` |
| `SHEET_NAME` | `str` | Hoja de datos: `"savedrecs"` |
| `OUTPUT_DIR` | `Path` | Directorio `output/` (se crea automáticamente) |
| `VAULT_DIR` | `Path` | Directorio `vault_bibliometria/` |
| `MULTIVALUE_SEP` | `str` | Separador de campos multi-valor WoS: `";"` |

### Clase `GraphDefaults`

```python
class GraphDefaults(BaseModel):
    min_cooccurrence_weight: int = 2
    min_cocitation_weight: int = 5
    louvain_resolution: float = 1.0
    temporal_window_years: int = 5
    top_keywords_per_community: int = 5
    dimred_n_components: int = 2
    dimred_random_state: int = 42
```

Parámetros por defecto para la construcción y análisis de grafos. Modelo Pydantic; validación automática de tipos.

**Campos:**

| Campo | Tipo | Defecto | Descripción |
|-------|------|---------|-------------|
| `min_cooccurrence_weight` | `int` | `2` | Co-ocurrencias mínimas para crear arista en grafos de keywords/autores |
| `min_cocitation_weight` | `int` | `5` | Co-citaciones mínimas para crear arista (corpus grande: reducir ruido) |
| `louvain_resolution` | `float` | `1.0` | Resolución Louvain: mayor valor genera más comunidades |
| `temporal_window_years` | `int` | `5` | Tamaño de ventana temporal en años |
| `top_keywords_per_community` | `int` | `5` | Keywords que forman la etiqueta de cada comunidad |
| `dimred_n_components` | `int` | `2` | Dimensiones de salida en reducción dimensional |
| `dimred_random_state` | `int` | `42` | Semilla de aleatoriedad para reproducibilidad |

**Instancia global:**

```python
DEFAULTS = GraphDefaults()
```

**Ejemplo:**

```python
from co_occurrence.config import DEFAULTS, GraphDefaults

# Usar valores por defecto
print(DEFAULTS.min_cooccurrence_weight)  # 2

# Personalizar
my_cfg = GraphDefaults(min_cooccurrence_weight=3, louvain_resolution=1.5)
```

---

## 2. `io.loader`

Lectura del archivo Excel exportado de Web of Science.

### `load_wos_data`

```python
def load_wos_data(
    path: Path = DATA_FILE,
    sheet_name: str = SHEET_NAME,
) -> pd.DataFrame:
```

Lee el archivo Excel de WoS y retorna un DataFrame limpio.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `path` | `Path` | `DATA_FILE` | Ruta al archivo Excel |
| `sheet_name` | `str` | `"savedrecs"` | Nombre de la hoja a leer |

**Retorna:** `pd.DataFrame` con los 331 registros WoS. Los nombres de columna se limpian de espacios en blanco.

**Ejemplo:**

```python
from co_occurrence.io.loader import load_wos_data

df = load_wos_data()
print(df.shape)           # (331, N_columnas)
print(df.columns.tolist())
```

---

## 3. `preprocessing.parse`

Parseo de campos multi-valor y extracción de países del formato WoS.

### `parse_multivalue`

```python
def parse_multivalue(
    series: pd.Series,
    sep: str = MULTIVALUE_SEP,
    to_lower: bool = True,
) -> pd.Series:
```

Parsea una columna multi-valor separada por `sep` y devuelve una Series explotada (una entrada por valor), conservando el índice del artículo original.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `series` | `pd.Series` | — | Columna del DataFrame (puede contener NaN) |
| `sep` | `str` | `";"` | Separador entre valores |
| `to_lower` | `bool` | `True` | Si `True`, convierte todos los valores a minúsculas |

**Retorna:** `pd.Series` explotada con un valor por fila, indexada al artículo original. Las cadenas vacías son eliminadas.

**Ejemplo:**

```python
from co_occurrence.preprocessing.parse import parse_multivalue

keywords_long = parse_multivalue(df["Author Keywords"])
# Cada fila es una keyword, el índice apunta al artículo
print(keywords_long.value_counts().head(10))
```

---

### `extract_countries_from_addresses`

```python
def extract_countries_from_addresses(addresses: pd.Series) -> pd.Series:
```

Extrae los países de la columna `Addresses` de WoS. El formato WoS es `"[Autor] Institución, Ciudad, Estado, País; ..."`. El país es el último elemento antes del siguiente `;` o fin de cadena.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `addresses` | `pd.Series` | Columna `'Addresses'` del DataFrame WoS |

**Retorna:** `pd.Series` explotada con un país por fila en minúsculas, indexada por `article_idx`.

**Ejemplo:**

```python
from co_occurrence.preprocessing.parse import extract_countries_from_addresses

countries = extract_countries_from_addresses(df["Addresses"])
print(countries.value_counts().head(5))
# spain       45
# usa         38
# ...
```

---

## 4. `preprocessing.normalize`

Normalización de keywords mediante diccionario de sinónimos y detección de candidatos.

### `normalize_keyword`

```python
def normalize_keyword(
    kw: str,
    synonyms: dict[str, str] = KEYWORD_SYNONYMS,
    stoplist: set[str] = KEYWORD_STOPLIST,
) -> str:
```

Normaliza una keyword individual: convierte a minúsculas, elimina espacios y aplica el diccionario de sinónimos. Si la keyword (tras normalización) pertenece a la stoplist, retorna la cadena vacía `""`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `kw` | `str` | — | Keyword en bruto |
| `synonyms` | `dict[str, str]` | `KEYWORD_SYNONYMS` | Diccionario de mapeo sinónimo → forma canónica |
| `stoplist` | `set[str]` | `KEYWORD_STOPLIST` | Conjunto de keywords a suprimir (retorna `""` si la keyword pertenece a él) |

**Retorna:** `str` con la keyword normalizada (forma canónica o el propio valor en minúsculas si no está en el diccionario), o `""` si la keyword está en la stoplist.

**Ejemplo:**

```python
from co_occurrence.preprocessing.normalize import normalize_keyword

normalize_keyword("COVID-19")    # "covid-19" (o su forma canónica si está en KEYWORD_SYNONYMS)
normalize_keyword("  Tourism  ") # "tourism"
normalize_keyword("Spain")       # "" (término geográfico en KEYWORD_STOPLIST)
```

---

### `normalize_keyword_series`

```python
def normalize_keyword_series(
    series: pd.Series,
    synonyms: dict[str, str] = KEYWORD_SYNONYMS,
) -> pd.Series:
```

Normaliza una Series de keywords ya parseadas (una keyword por fila) aplicando `normalize_keyword` a cada elemento. Registra en el log el número de sustituciones realizadas.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `series` | `pd.Series` | — | Series con una keyword por fila |
| `synonyms` | `dict[str, str]` | `KEYWORD_SYNONYMS` | Diccionario de sinónimos |

**Retorna:** `pd.Series` con las keywords normalizadas. Las keywords suprimidas por la stoplist (cuya normalización retorna `""`) son eliminadas del resultado; la Series de salida puede tener menos filas que la de entrada. El log registra el número de sustituciones realizadas y el número de keywords eliminadas.

**Ejemplo:**

```python
from co_occurrence.preprocessing.parse import parse_multivalue
from co_occurrence.preprocessing.normalize import normalize_keyword_series

kw_raw = parse_multivalue(df["Author Keywords"])
kw_norm = normalize_keyword_series(kw_raw)
# Las keywords en KEYWORD_STOPLIST quedan excluidas de kw_norm
```

---

### `build_synonym_candidates`

```python
def build_synonym_candidates(
    series: pd.Series,
    min_freq: int = 2,
) -> pd.DataFrame:
```

Detecta posibles sinónimos buscando keywords que comparten tokens léxicos. Útil para expandir el diccionario `synonyms.py` manualmente.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `series` | `pd.Series` | — | Series de keywords parseadas (una por fila) |
| `min_freq` | `int` | `2` | Frecuencia mínima para que una keyword sea candidata |

**Retorna:** `pd.DataFrame` con columnas `keyword_a`, `keyword_b`, `shared_tokens`, `freq_a`, `freq_b`, ordenado por tokens compartidos.

**Ejemplo:**

```python
from co_occurrence.preprocessing.normalize import build_synonym_candidates

candidates = build_synonym_candidates(kw_norm, min_freq=3)
candidates.head(20)  # revisar manualmente y añadir a synonyms.py
```

---

## 5. `graphs.cooccurrence`

Construcción del grafo principal de co-ocurrencia de keywords (o cualquier campo multi-valor).

### `build_cooccurrence_graph`

```python
def build_cooccurrence_graph(
    df: pd.DataFrame,
    column: str = "Author Keywords",
    sep: str = MULTIVALUE_SEP,
    min_weight: int = DEFAULTS.min_cooccurrence_weight,
    min_frequency: int = 1,
    apply_normalization: bool = True,
) -> nx.Graph:
```

Construye un grafo de co-ocurrencia a partir de una columna multi-valor. Dos items co-ocurren cuando aparecen en el mismo artículo. El peso de la arista es el número de artículos en que co-ocurren. Los nodos con frecuencia por debajo de `min_frequency` son excluidos antes de crear aristas. Los nodos aislados (sin aristas tras el filtro) son eliminados.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame con los artículos WoS |
| `column` | `str` | `"Author Keywords"` | Nombre de la columna multi-valor |
| `sep` | `str` | `";"` | Separador entre items |
| `min_weight` | `int` | `2` | Umbral mínimo de co-ocurrencias para crear arista |
| `min_frequency` | `int` | `1` | Frecuencia mínima de aparición de un nodo para incluirlo en el grafo |
| `apply_normalization` | `bool` | `True` | Si `True`, normaliza keywords con el diccionario de sinónimos (y aplica la stoplist) |

**Retorna:** `nx.Graph` no dirigido con:
- Atributo `frequency` en cada nodo (número de artículos en que aparece el item)
- Atributo `weight` en cada arista (número de co-ocurrencias)

**Ejemplo:**

```python
from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph

G = build_cooccurrence_graph(df, min_weight=3)
print(G.number_of_nodes(), G.number_of_edges())

# Excluir keywords que aparecen en menos de 3 artículos
G = build_cooccurrence_graph(df, min_weight=2, min_frequency=3)

# También funciona con categorías WoS
G_cat = build_cooccurrence_graph(df, column="Web of Science Categories")
```

---

## 6. `graphs.coauthor`

Construcción de la red de co-autoría.

### `build_coauthor_graph`

```python
def build_coauthor_graph(
    df: pd.DataFrame,
    column: str = "Author Full Names",
    sep: str = MULTIVALUE_SEP,
    min_weight: int = 1,
) -> nx.Graph:
```

Construye un grafo de co-autoría. Dos autores están conectados si firman el mismo artículo. El peso de la arista es el número de artículos co-firmados. Los nodos aislados son eliminados.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame con los artículos WoS |
| `column` | `str` | `"Author Full Names"` | Columna de autores |
| `sep` | `str` | `";"` | Separador entre autores |
| `min_weight` | `int` | `1` | Umbral mínimo de co-autorías para crear arista |

**Retorna:** `nx.Graph` no dirigido con:
- Atributo `frequency` en nodos (número de artículos publicados por el autor)
- Atributo `weight` en aristas (número de artículos co-firmados)

**Ejemplo:**

```python
from co_occurrence.graphs.coauthor import build_coauthor_graph

G_authors = build_coauthor_graph(df)
print(G_authors.number_of_nodes())  # autores con al menos una co-autoría
```

---

## 7. `graphs.cocitation`

Construcción de la red de co-citación.

### `build_cocitation_graph`

```python
def build_cocitation_graph(
    df: pd.DataFrame,
    column: str = "Cited References",
    sep: str = ";",
    min_weight: int = DEFAULTS.min_cocitation_weight,
) -> nx.Graph:
```

Construye un grafo de co-citación. Dos referencias están conectadas si el mismo artículo las cita. El peso es el número de artículos que citan ambas referencias. Con 331 artículos y ~100 refs/artículo el grafo puede ser enorme; se recomienda `min_weight >= 5`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame con los artículos WoS |
| `column` | `str` | `"Cited References"` | Columna de referencias citadas |
| `sep` | `str` | `";"` | Separador entre referencias |
| `min_weight` | `int` | `5` | Umbral mínimo de co-citaciones |

**Retorna:** `nx.Graph` no dirigido con:
- Atributo `frequency` en nodos (número de artículos que citan esta referencia)
- Atributo `weight` en aristas (número de co-citaciones)

**Ejemplo:**

```python
from co_occurrence.graphs.cocitation import build_cocitation_graph

G_cit = build_cocitation_graph(df, min_weight=10)
```

---

## 8. `graphs.bipartite`

Construcción de grafos bipartitos entre dos tipos de entidades del corpus.

### `build_bipartite_graph`

```python
def build_bipartite_graph(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    sep: str = MULTIVALUE_SEP,
    normalize_b: bool = False,
    node_type_a: str = "type_a",
    node_type_b: str = "type_b",
) -> nx.Graph:
```

Construye un grafo bipartito entre dos columnas multi-valor. Cada artículo genera aristas entre todos los items de `col_a` y todos los de `col_b`. El peso de la arista es el número de artículos en que co-aparecen.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS |
| `col_a` | `str` | — | Primera columna multi-valor (ej. `'Author Full Names'`) |
| `col_b` | `str` | — | Segunda columna multi-valor (ej. `'Author Keywords'`) |
| `sep` | `str` | `";"` | Separador |
| `normalize_b` | `bool` | `False` | Si `True`, normaliza items de `col_b` como keywords |
| `node_type_a` | `str` | `"type_a"` | Etiqueta del tipo de nodo A (atributo `node_type`) |
| `node_type_b` | `str` | `"type_b"` | Etiqueta del tipo de nodo B (atributo `node_type`) |

**Retorna:** `nx.Graph` bipartito con atributos `bipartite` (0 o 1) y `node_type` en los nodos, y `weight` en las aristas.

**Ejemplo:**

```python
from co_occurrence.graphs.bipartite import build_bipartite_graph

G_bip = build_bipartite_graph(
    df,
    col_a="Source Title",
    col_b="Author Keywords",
    normalize_b=True,
    node_type_a="journal",
    node_type_b="keyword",
)
```

---

### `build_author_keyword_graph`

```python
def build_author_keyword_graph(df: pd.DataFrame) -> nx.Graph:
```

Atajo para construir el grafo bipartito **autor — keyword**. Columnas: `Author Full Names` (tipo `"author"`) y `Author Keywords` (tipo `"keyword"`, normalizada).

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame WoS |

**Retorna:** `nx.Graph` bipartito autor-keyword.

**Ejemplo:**

```python
from co_occurrence.graphs.bipartite import build_author_keyword_graph

G_ak = build_author_keyword_graph(df)
```

---

### `build_journal_keyword_graph`

```python
def build_journal_keyword_graph(df: pd.DataFrame) -> nx.Graph:
```

Atajo para construir el grafo bipartito **revista — keyword**. Columnas: `Source Title` (tipo `"journal"`) y `Author Keywords` (tipo `"keyword"`, normalizada).

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame WoS |

**Retorna:** `nx.Graph` bipartito revista-keyword.

**Ejemplo:**

```python
from co_occurrence.graphs.bipartite import build_journal_keyword_graph

G_jk = build_journal_keyword_graph(df)
```

---

### `build_country_keyword_graph`

```python
def build_country_keyword_graph(df: pd.DataFrame) -> nx.Graph:
```

Atajo para construir el grafo bipartito **país — keyword**. Los países se extraen de la columna `Addresses` mediante `extract_countries_from_addresses`. El tipo de nodo país es `"country"` y el de keyword `"keyword"` (normalizada).

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame WoS (requiere columna `"Addresses"`) |

**Retorna:** `nx.Graph` bipartito país-keyword.

**Ejemplo:**

```python
from co_occurrence.graphs.bipartite import build_country_keyword_graph

G_ck = build_country_keyword_graph(df)
```

---

## 9. `graphs.weights`

Normalización de pesos de co-ocurrencia. Todas las funciones modifican el grafo **en lugar** (`in-place`) añadiendo atributos a las aristas y devuelven el mismo grafo.

### `association_strength`

```python
def association_strength(G: nx.Graph) -> nx.Graph:
```

Añade el atributo `assoc_strength` a cada arista.

**Fórmula:** `AS(a,b) = w(a,b) / (f(a) × f(b))`

Penaliza co-ocurrencias esperadas por azar. Es la métrica usada por VOSviewer y la recomendada para el layout del grafo.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo con atributo `frequency` en nodos y `weight` en aristas |

**Retorna:** El mismo grafo con atributo `assoc_strength` añadido a las aristas.

---

### `jaccard_index`

```python
def jaccard_index(G: nx.Graph) -> nx.Graph:
```

Añade el atributo `jaccard` a cada arista.

**Fórmula:** `J(a,b) = w(a,b) / (f(a) + f(b) − w(a,b))`

Recomendado para la detección de comunidades.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo con `frequency` en nodos y `weight` en aristas |

**Retorna:** El mismo grafo con atributo `jaccard` añadido.

---

### `salton_cosine`

```python
def salton_cosine(G: nx.Graph) -> nx.Graph:
```

Añade el atributo `salton` (coseno de Salton) a cada arista.

**Fórmula:** `S(a,b) = w(a,b) / √(f(a) × f(b))`

Equivalente al coseno entre vectores de frecuencia.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo con `frequency` en nodos y `weight` en aristas |

**Retorna:** El mismo grafo con atributo `salton` añadido.

---

### `inclusion_index`

```python
def inclusion_index(G: nx.Graph) -> nx.Graph:
```

Añade el atributo `inclusion` (Inclusion Index) a cada arista.

**Fórmula:** `I(a,b) = w(a,b) / min(f(a), f(b))`

Mide en qué medida un item más frecuente "incluye" al menos frecuente.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo con `frequency` en nodos y `weight` en aristas |

**Retorna:** El mismo grafo con atributo `inclusion` añadido.

---

### `apply_all_normalizations`

```python
def apply_all_normalizations(G: nx.Graph) -> nx.Graph:
```

Aplica las cuatro normalizaciones en una sola llamada: Association Strength, Jaccard, Salton y Inclusion. Las aristas quedan con los cuatro atributos añadidos.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo con `frequency` en nodos y `weight` en aristas |

**Retorna:** El mismo grafo con atributos `assoc_strength`, `jaccard`, `salton` e `inclusion` en todas las aristas.

**Ejemplo:**

```python
from co_occurrence.graphs.weights import apply_all_normalizations

G = apply_all_normalizations(G)
# Ahora se puede usar cualquier peso normalizado
data = G["tourism"]["sustainability"]
print(data["assoc_strength"], data["jaccard"])
```

---

## 10. `analysis.communities`

Detección de comunidades temáticas y etiquetado semántico. Los algoritmos de Louvain y Leiden requieren dependencias opcionales.

### `detect_louvain`

```python
def detect_louvain(
    G: nx.Graph,
    resolution: float = DEFAULTS.louvain_resolution,
    weight: str = "weight",
) -> dict[str, int]:
```

Detecta comunidades con el algoritmo de Louvain. Requiere `python-louvain` (`community`).

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo no dirigido |
| `resolution` | `float` | `1.0` | Resolución del algoritmo (mayor = más comunidades) |
| `weight` | `str` | `"weight"` | Atributo de peso de aristas a utilizar |

**Retorna:** `dict[str, int]` con `{nodo: id_comunidad}`. Además, añade el atributo `community` a cada nodo del grafo.

**Ejemplo:**

```python
from co_occurrence.analysis.communities import detect_louvain

partition = detect_louvain(G, resolution=1.2)
# {tourism: 0, sustainability: 0, management: 1, ...}
```

---

### `detect_leiden`

```python
def detect_leiden(
    G: nx.Graph,
    weight: str = "weight",
) -> dict[str, int]:
```

Detecta comunidades con el algoritmo de Leiden, más robusto que Louvain (garantiza comunidades bien conectadas). Requiere `igraph` y `leidenalg`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo no dirigido |
| `weight` | `str` | `"weight"` | Atributo de peso de aristas |

**Retorna:** `dict[str, int]` con `{nodo: id_comunidad}`. Añade el atributo `community` a cada nodo del grafo.

**Ejemplo:**

```python
from co_occurrence.analysis.communities import detect_leiden

partition = detect_leiden(G)
```

---

### `label_communities`

```python
def label_communities(
    G: nx.Graph,
    partition: dict[str, int],
    top_n: int = DEFAULTS.top_keywords_per_community,
) -> pd.DataFrame:
```

Etiqueta cada comunidad con sus keywords más frecuentes (por atributo `frequency` del nodo). La etiqueta es una cadena de los top-N keywords separados por `" / "`, seguida del sufijo `" (+N más)"` cuando la comunidad tiene más miembros que `top_n`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo con atributo `frequency` en nodos |
| `partition` | `dict[str, int]` | — | Diccionario `{nodo: id_comunidad}` |
| `top_n` | `int` | `5` | Número de keywords top para formar la etiqueta |

**Retorna:** `pd.DataFrame` con columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `community` | `int` | Identificador de la comunidad |
| `label` | `str` | Etiqueta con los top-N keywords separados por `" / "`, más sufijo `" (+N más)"` si hay miembros adicionales |
| `size` | `int` | Número de nodos en la comunidad |
| `keywords` | `list[str]` | Lista con **todos** los miembros de la comunidad, ordenados por `frequency` descendente |

**Ejemplo:**

```python
from co_occurrence.analysis.communities import detect_louvain, label_communities

partition = detect_louvain(G)
labels_df = label_communities(G, partition, top_n=5)
print(labels_df[["community", "label", "size"]])
# community 0: "tourism / sustainability / management / hotel / satisfaction (+12 más)"
# keywords contiene los 17 miembros completos de la comunidad, no solo los 5 del label
```

---

## 11. `analysis.centrality`

Métricas de centralidad clásicas y análisis de huecos estructurales (Burt).

### `compute_centralities`

```python
def compute_centralities(
    G: nx.Graph,
    weight: str = "weight",
    partition: dict[str, int] | None = None,
) -> pd.DataFrame:
```

Calcula múltiples métricas de centralidad para todos los nodos del grafo. Si la eigenvector centrality no converge, aumenta automáticamente las iteraciones.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo no dirigido con pesos |
| `weight` | `str` | `"weight"` | Nombre del atributo de peso en aristas |
| `partition` | `dict[str, int] \| None` | `None` | Diccionario `{nodo: comunidad}` (opcional; si se provee, se añade columna `community`) |

**Retorna:** `pd.DataFrame` ordenado por `weighted_degree` descendente con columnas:

| Columna | Descripción |
|---------|-------------|
| `keyword` | Nombre del nodo |
| `frequency` | Frecuencia del nodo (atributo del grafo) |
| `degree` | Grado no ponderado |
| `weighted_degree` | Grado ponderado |
| `betweenness` | Betweenness centrality |
| `closeness` | Closeness centrality |
| `eigenvector` | Eigenvector centrality |
| `pagerank` | PageRank |
| `community` | *(solo si se provee `partition`)* |

**Ejemplo:**

```python
from co_occurrence.analysis.centrality import compute_centralities

centralities = compute_centralities(G, partition=partition)
centralities[["keyword", "weighted_degree", "betweenness"]].head(20)
```

---

### `compute_structural_holes`

```python
def compute_structural_holes(
    G: nx.Graph,
    weight: str = "weight",
) -> pd.DataFrame:
```

Calcula métricas de huecos estructurales de Burt para cada nodo. Los nodos con bajo `constraint` ocupan posiciones puente estratégicas entre comunidades.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo no dirigido con pesos |
| `weight` | `str` | `"weight"` | Atributo de peso |

**Retorna:** `pd.DataFrame` ordenado por `constraint` ascendente con columnas:

| Columna | Descripción |
|---------|-------------|
| `keyword` | Nombre del nodo |
| `frequency` | Frecuencia del nodo |
| `constraint` | Constraint de Burt: valores bajos indican más huecos estructurales |
| `effective_size` | Contactos no redundantes del nodo |

**Ejemplo:**

```python
from co_occurrence.analysis.centrality import compute_structural_holes

holes = compute_structural_holes(G)
# Los primeros filas son los nodos puente más importantes
holes.head(10)
```

---

## 12. `analysis.temporal`

Análisis de la evolución temporal de keywords: grafos por período, métricas y detección de tendencias.

### `build_temporal_graphs`

```python
def build_temporal_graphs(
    df: pd.DataFrame,
    column: str = "Author Keywords",
    window_years: int = DEFAULTS.temporal_window_years,
    windows: list[tuple[int, int]] | None = None,
    min_weight: int = 1,
) -> dict[str, nx.Graph]:
```

Construye un grafo de co-ocurrencia por cada ventana temporal. Si `windows` es `None`, las ventanas se generan automáticamente con paso `window_years` desde el año mínimo hasta el máximo.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS con columna `'Publication Year'` |
| `column` | `str` | `"Author Keywords"` | Columna multi-valor para co-ocurrencia |
| `window_years` | `int` | `5` | Tamaño de la ventana en años |
| `windows` | `list[tuple[int, int]] \| None` | `None` | Lista explícita de `(inicio, fin)`. Si `None`, se genera automáticamente |
| `min_weight` | `int` | `1` | Peso mínimo para aristas (se recomienda `1` para ventanas pequeñas) |

**Retorna:** `dict[str, nx.Graph]` con `{etiqueta_periodo: grafo}`, donde la etiqueta tiene formato `"AAAA-AAAA"`.

**Ejemplo:**

```python
from co_occurrence.analysis.temporal import build_temporal_graphs

# Ventanas automáticas de 5 años
temporal = build_temporal_graphs(df)

# Ventanas manuales
temporal_custom = build_temporal_graphs(
    df,
    windows=[(2000, 2009), (2010, 2019), (2020, 2024)],
)
```

---

### `keyword_evolution_metrics`

```python
def keyword_evolution_metrics(
    temporal_graphs: dict[str, nx.Graph],
) -> pd.DataFrame:
```

Calcula métricas de frecuencia y centralidad por keyword en cada período temporal. Útil para trazar la trayectoria de una keyword a lo largo del tiempo.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `temporal_graphs` | `dict[str, nx.Graph]` | Diccionario `{periodo: grafo}` generado por `build_temporal_graphs` |

**Retorna:** `pd.DataFrame` con columnas `period`, `keyword`, `frequency`, `degree`, `weighted_degree`, `betweenness`.

**Ejemplo:**

```python
from co_occurrence.analysis.temporal import keyword_evolution_metrics

evo = keyword_evolution_metrics(temporal)
# Filtrar por keyword específica
evo[evo["keyword"] == "sustainability"].sort_values("period")
```

---

### `detect_emerging_declining`

```python
def detect_emerging_declining(
    temporal_graphs: dict[str, nx.Graph],
    n_early: int = 2,
) -> tuple[set[str], set[str]]:
```

Detecta keywords emergentes (aparecen en el último período pero no en los primeros `n_early`) y en declive (aparecen en los primeros `n_early` pero no en el último).

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `temporal_graphs` | `dict[str, nx.Graph]` | — | Diccionario `{periodo: grafo}` ordenado cronológicamente |
| `n_early` | `int` | `2` | Número de períodos iniciales que se consideran "tempranos" |

**Retorna:** `tuple[set[str], set[str]]` con `(emergentes, en_declive)`.

**Ejemplo:**

```python
from co_occurrence.analysis.temporal import (
    build_temporal_graphs,
    detect_emerging_declining,
)

temporal = build_temporal_graphs(df)
emerging, declining = detect_emerging_declining(temporal, n_early=2)
print("Emergentes:", emerging)
print("En declive:", declining)
```

---

## 13. `dimred.manifold`

Reducción dimensional de la matriz de co-ocurrencia: MDS, t-SNE y UMAP. Las funciones `reduce_*` usan internamente `cooccurrence_to_distance_matrix` para convertir el grafo a una matriz de distancias antes de aplicar el algoritmo.

### `cooccurrence_to_distance_matrix`

```python
def cooccurrence_to_distance_matrix(
    G: nx.Graph,
) -> tuple[np.ndarray, list[str]]:
```

Convierte un grafo de co-ocurrencia en una matriz de distancias simétricas. Pares con co-ocurrencia: `distancia = 1 − (w / w_max)`. Pares sin co-ocurrencia: `distancia = 1.0`. La diagonal es `0`.

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `G` | `nx.Graph` | Grafo de co-ocurrencia con atributo `weight` en aristas |

**Retorna:** `tuple[np.ndarray, list[str]]` con `(matriz_distancias, lista_nodos)`. La matriz es de forma `(n, n)`.

---

### `reduce_mds`

```python
def reduce_mds(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
) -> pd.DataFrame:
```

Reducción dimensional con MDS (Multidimensional Scaling). Preserva distancias globales. Es la técnica clásica en bibliometría (VOSviewer usa MDS). Requiere `scikit-learn`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `n_components` | `int` | `2` | Dimensiones de salida |
| `random_state` | `int` | `42` | Semilla de aleatoriedad |

**Retorna:** `pd.DataFrame` con columnas `keyword`, `x`, `y`, `frequency`. El stress del MDS se registra en el log.

**Ejemplo:**

```python
from co_occurrence.dimred.manifold import reduce_mds

coords_mds = reduce_mds(G)
```

---

### `reduce_tsne`

```python
def reduce_tsne(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
    perplexity: float = 30.0,
) -> pd.DataFrame:
```

Reducción dimensional con t-SNE. Revela clusters locales con mayor claridad que MDS, pero no preserva distancias globales. La perplexity se ajusta automáticamente si hay pocos nodos. Requiere `scikit-learn`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `n_components` | `int` | `2` | Dimensiones de salida |
| `random_state` | `int` | `42` | Semilla de aleatoriedad |
| `perplexity` | `float` | `30.0` | Perplexity del t-SNE (ajustar si hay pocos nodos) |

**Retorna:** `pd.DataFrame` con columnas `keyword`, `x`, `y`, `frequency`.

**Ejemplo:**

```python
from co_occurrence.dimred.manifold import reduce_tsne

coords_tsne = reduce_tsne(G, perplexity=20.0)
```

---

### `reduce_umap`

```python
def reduce_umap(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> pd.DataFrame:
```

Reducción dimensional con UMAP. Preserva tanto estructura local como global. Es la técnica recomendada para este proyecto. El parámetro `n_neighbors` se ajusta automáticamente si hay menos nodos que vecinos solicitados. Requiere `umap-learn`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `n_components` | `int` | `2` | Dimensiones de salida |
| `random_state` | `int` | `42` | Semilla de aleatoriedad |
| `n_neighbors` | `int` | `15` | Vecinos para construir el grafo local |
| `min_dist` | `float` | `0.1` | Distancia mínima entre puntos en el embedding |

**Retorna:** `pd.DataFrame` con columnas `keyword`, `x`, `y`, `frequency`.

**Ejemplo:**

```python
from co_occurrence.dimred.manifold import reduce_umap

coords_umap = reduce_umap(G, n_neighbors=10, min_dist=0.05)
```

---

## 14. `dimred.correspondence`

Análisis de Correspondencias (CA) para biplots keyword-revista, keyword-país, etc.

### `compute_ca`

```python
def compute_ca(
    df: pd.DataFrame,
    row_column: str = "Author Keywords",
    col_column: str = "Source Title",
    sep: str = MULTIVALUE_SEP,
    n_components: int = DEFAULTS.dimred_n_components,
    normalize_rows: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
```

Analisis de Correspondencias simple sobre una tabla de contingencia construida a partir de dos columnas WoS. Proyecta filas (ej. keywords) y columnas (ej. revistas) en el mismo espacio factorial. Requiere `prince`.

Detecta y salta automaticamente dimensiones degeneradas (eigenvalue >= 0.99) causadas por pares exclusivos keyword-revista. Filtra iterativamente la tabla de contingencia para eliminar filas y columnas con frecuencia < 2.

**Parametros:**

| Parametro | Tipo | Defecto | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS |
| `row_column` | `str` | `"Author Keywords"` | Columna para filas de la tabla de contingencia |
| `col_column` | `str` | `"Source Title"` | Columna para columnas de la tabla de contingencia |
| `sep` | `str` | `";"` | Separador en campos multi-valor |
| `n_components` | `int` | `2` | Numero de componentes utiles (se extraen mas si hay degenerados) |
| `normalize_rows` | `bool` | `True` | Si `True` y `row_column` es keywords, normaliza con sinonimos |

**Retorna:** `tuple[pd.DataFrame, pd.DataFrame]` con `(row_coords, col_coords)`. Cada DataFrame tiene:

| Columna | Descripcion |
|---------|-------------|
| `x`, `y` | Coordenadas factoriales (o `dim_0`, `dim_1`, ... si `n_components != 2`) |
| `frequency` | Frecuencia marginal (suma de la fila/columna en la tabla de contingencia) |
| `contribution` | Contribucion a la inercia (`(x^2 + y^2) * frequency`) |
| `entity_type` | Nombre de la columna WoS de origen |

El indice del DataFrame es el nombre de la entidad. El atributo `attrs["explained_inertia"]` contiene el % de inercia explicada por cada dimension.

**Ejemplo:**

```python
from co_occurrence.dimred.correspondence import compute_ca

row_coords, col_coords = compute_ca(
    df,
    row_column="Author Keywords",
    col_column="Source Title",
)
# row_coords: 114 keywords en el espacio CA
# col_coords: 132 revistas en el mismo espacio
# row_coords.attrs["explained_inertia"] -> [2.6, 2.5] (% por dim)
```

---

## 15. `topics.modeling`

Topic modeling sobre abstracts: LDA clásico y BERTopic neuronal. Dependencias opcionales.

### `fit_lda`

```python
def fit_lda(
    df: pd.DataFrame,
    column: str = "Abstract",
    n_topics: int = 8,
    max_features: int = 1000,
    random_state: int = 42,
) -> tuple[pd.DataFrame, list[list[str]]]:
```

Ajusta LDA (Latent Dirichlet Allocation) sobre los abstracts y asigna el topic dominante a cada artículo. Usa TF-IDF con `stop_words="english"`. Requiere `scikit-learn`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS |
| `column` | `str` | `"Abstract"` | Columna con texto de abstracts |
| `n_topics` | `int` | `8` | Número de topics a detectar |
| `max_features` | `int` | `1000` | Vocabulario máximo para TF-IDF |
| `random_state` | `int` | `42` | Semilla de aleatoriedad |

**Retorna:** `tuple[pd.DataFrame, list[list[str]]]` con:
- `df_con_topics`: DataFrame original con columna `lda_topic` añadida (entero con el topic dominante)
- `topic_words`: lista de listas con las top 10 palabras por topic

**Ejemplo:**

```python
from co_occurrence.topics.modeling import fit_lda

df_topics, topic_words = fit_lda(df, n_topics=10)
for i, words in enumerate(topic_words):
    print(f"Topic {i}: {', '.join(words)}")
```

---

### `fit_bertopic`

```python
def fit_bertopic(
    df: pd.DataFrame,
    column: str = "Abstract",
    nr_topics: int = 10,
    language: str = "english",
) -> tuple[pd.DataFrame, object]:
```

Ajusta BERTopic sobre los abstracts. Más sofisticado que LDA y mejor adaptado a corpus pequeños (~331 documentos). El topic `-1` es el topic de outliers (documentos no asignados). Requiere `bertopic`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS |
| `column` | `str` | `"Abstract"` | Columna con texto de abstracts |
| `nr_topics` | `int` | `10` | Número de topics objetivo |
| `language` | `str` | `"english"` | Idioma de los documentos |

**Retorna:** `tuple[pd.DataFrame, object]` con:
- `df_con_topics`: DataFrame original con columna `bertopic` añadida (entero con el topic asignado)
- `topic_model`: objeto `BERTopic` ajustado (permite llamar a `topic_model.get_topic_info()`, `topic_model.visualize_topics()`, etc.)

**Ejemplo:**

```python
from co_occurrence.topics.modeling import fit_bertopic

df_topics, model = fit_bertopic(df, nr_topics=8)
model.get_topic_info()
```

---

## 16. `viz.plotly_graphs`

Visualización de grafos como figuras Plotly interactivas, usando coordenadas pre-calculadas por los módulos de reducción dimensional.

### `plot_network`

```python
def plot_network(
    G: nx.Graph,
    coords: pd.DataFrame,
    partition: dict[str, int] | None = None,
    title: str = "Red de co-ocurrencia",
    min_degree_label: int = 5,
    height: int = 700,
    save_path: Path | None = None,
) -> object:
```

Dibuja un grafo interactivo con Plotly usando coordenadas pre-calculadas (MDS, t-SNE o UMAP). El tamaño de los nodos es proporcional al grado ponderado. El color representa la comunidad (si se provee `partition`) o la frecuencia. Solo se muestran etiquetas de texto para nodos con grado >= `min_degree_label`. Requiere `plotly`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `coords` | `pd.DataFrame` | — | DataFrame con columnas `keyword`, `x`, `y` (salida de `reduce_mds/tsne/umap`) |
| `partition` | `dict[str, int] \| None` | `None` | Diccionario `{nodo: comunidad}` para colorear por comunidad |
| `title` | `str` | `"Red de co-ocurrencia"` | Título del gráfico |
| `min_degree_label` | `int` | `5` | Grado mínimo para mostrar la etiqueta del nodo |
| `height` | `int` | `700` | Altura del gráfico en píxeles |
| `save_path` | `Path \| None` | `None` | Si se provee, guarda el HTML en esta ruta (con `include_plotlyjs="cdn"`) |

**Retorna:** Figura `plotly.graph_objects.Figure`.

**Ejemplo:**

```python
from co_occurrence.dimred.manifold import reduce_umap
from co_occurrence.viz.plotly_graphs import plot_network

coords = reduce_umap(G)
fig = plot_network(G, coords, partition=partition, title="Red keywords turismo")
fig.show()

# Guardar para Quarto
fig = plot_network(G, coords, save_path=Path("output/red_keywords.html"))
```

---

## 17. `viz.plotly_scatter`

Scatter plots de métricas de centralidad, mapas de reducción dimensional y biplots del Análisis de Correspondencias.

### `plot_manifold_scatter`

```python
def plot_manifold_scatter(
    coords: pd.DataFrame,
    partition: dict[str, int] | None = None,
    method: str = "UMAP",
    top_n_labels: int = 20,
    height: int = 700,
    save_path: Path | None = None,
) -> object:
```

Scatter plot interactivo de coordenadas de reducción dimensional. Colorea los puntos por comunidad Louvain (si se proporciona `partition`) o por frecuencia. Muestra etiquetas de texto para las `top_n_labels` keywords más frecuentes. Burbujas proporcionales a la frecuencia.

Requiere `plotly`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `coords` | `pd.DataFrame` | — | DataFrame con columnas `keyword`, `x`, `y`, `frequency` (salida de `reduce_mds`, `reduce_tsne` o `reduce_umap`) |
| `partition` | `dict[str, int] \| None` | `None` | Diccionario `{keyword: community_id}` de `detect_louvain()` / `detect_leiden()`. Si `None`, colorea por frecuencia |
| `method` | `str` | `"UMAP"` | Nombre del método (para título y ejes) |
| `top_n_labels` | `int` | `20` | Número de keywords con etiqueta visible |
| `height` | `int` | `700` | Altura en píxeles |
| `save_path` | `Path \| None` | `None` | Ruta para guardar HTML |

**Retorna:** Figura `plotly.express.Figure`.

**Ejemplo:**

```python
from co_occurrence.analysis.communities import detect_louvain
from co_occurrence.dimred.manifold import reduce_umap
from co_occurrence.viz.plotly_scatter import plot_manifold_scatter

coords = reduce_umap(G)
partition = detect_louvain(G)
fig = plot_manifold_scatter(coords, partition=partition, method="UMAP")
fig.show()
```

---

### `plot_degree_vs_betweenness`

```python
def plot_degree_vs_betweenness(
    centralities: pd.DataFrame,
    title: str = "Degree vs Betweenness Centrality",
    height: int = 600,
    save_path: Path | None = None,
) -> object:
```

Scatter plot de grado ponderado vs betweenness centrality con líneas de cuadrante en las medianas. Permite identificar visualmente:
- Cuadrante alto-alto: keywords pilares del campo
- Alto betweenness + bajo degree: keywords puente interdisciplinarias

Requiere `plotly`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `centralities` | `pd.DataFrame` | — | DataFrame de `compute_centralities()` con columnas `keyword`, `weighted_degree`, `betweenness`, `frequency` y opcionalmente `community` |
| `title` | `str` | `"Degree vs Betweenness Centrality"` | Título del gráfico |
| `height` | `int` | `600` | Altura en píxeles |
| `save_path` | `Path \| None` | `None` | Ruta para guardar HTML |

**Retorna:** Figura `plotly.express.Figure`.

**Ejemplo:**

```python
from co_occurrence.viz.plotly_scatter import plot_degree_vs_betweenness

fig = plot_degree_vs_betweenness(centralities)
fig.show()
```

---

### `plot_ca_biplot`

```python
def plot_ca_biplot(
    row_coords: pd.DataFrame,
    col_coords: pd.DataFrame,
    title: str = "Biplot — Análisis de Correspondencias",
    height: int = 600,
    save_path: Path | None = None,
) -> object:
```

Biplot del Análisis de Correspondencias: filas (ej. keywords, círculos azules) y columnas (ej. revistas, triángulos coral) proyectados en el mismo espacio factorial. Requiere `plotly`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `row_coords` | `pd.DataFrame` | — | Coordenadas de filas con columnas `x`, `y`, `entity_type` (salida de `compute_ca`) |
| `col_coords` | `pd.DataFrame` | — | Coordenadas de columnas con columnas `x`, `y`, `entity_type` |
| `title` | `str` | `"Biplot — Análisis de Correspondencias"` | Título del gráfico |
| `height` | `int` | `600` | Altura en píxeles |
| `save_path` | `Path \| None` | `None` | Ruta para guardar HTML |

**Retorna:** Figura `plotly.graph_objects.Figure`.

**Ejemplo:**

```python
from co_occurrence.dimred.correspondence import compute_ca
from co_occurrence.viz.plotly_scatter import plot_ca_biplot

row_coords, col_coords = compute_ca(df)
fig = plot_ca_biplot(row_coords, col_coords, title="Keywords vs Revistas")
fig.show()
```

---

## 18. `viz.pyvis_net`

Exportación de grafos como HTML interactivos con físicas de red usando pyvis.

### `export_pyvis`

```python
def export_pyvis(
    G: nx.Graph,
    output_path: Path,
    height: str = "800px",
    width: str = "100%",
    bgcolor: str = "#ffffff",
    partition: dict[str, int] | None = None,
) -> Path:
```

Exporta un grafo como HTML interactivo con pyvis. Los nodos se dimensionan en función de su frecuencia (`max(10, min(50, freq × 3))`). Si se provee `partition`, los nodos se colorean por comunidad con una paleta de 15 colores cíclica. Las aristas muestran el peso al hacer hover. Requiere `pyvis`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo networkx |
| `output_path` | `Path` | — | Ruta del archivo HTML de salida |
| `height` | `str` | `"800px"` | Altura del canvas |
| `width` | `str` | `"100%"` | Ancho del canvas |
| `bgcolor` | `str` | `"#ffffff"` | Color de fondo |
| `partition` | `dict[str, int] \| None` | `None` | Diccionario `{nodo: comunidad}` para colorear nodos |

**Retorna:** `Path` del archivo HTML generado.

**Ejemplo:**

```python
from co_occurrence.viz.pyvis_net import export_pyvis

path = export_pyvis(
    G,
    output_path=Path("output/red_keywords.html"),
    partition=partition,
)
```

---

## 19. `viz.export`

Exportación de grafos y DataFrames a formatos externos: GEXF (Gephi) y CSV.

### `export_gexf`

```python
def export_gexf(
    G: nx.Graph,
    name: str,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
```

Exporta un grafo en formato GEXF para Gephi. El directorio de salida se crea si no existe. El archivo se nombra `{name}.gexf`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo networkx con atributos en nodos y aristas |
| `name` | `str` | — | Nombre base del archivo (sin extensión) |
| `output_dir` | `Path` | `OUTPUT_DIR` | Directorio de salida |

**Retorna:** `Path` del archivo GEXF generado.

**Ejemplo:**

```python
from co_occurrence.viz.export import export_gexf

path = export_gexf(G, name="cooccurrence_keywords")
# Genera output/cooccurrence_keywords.gexf
```

---

### `export_csv`

```python
def export_csv(
    df: pd.DataFrame,
    name: str,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
```

Exporta un DataFrame a CSV con encoding `utf-8-sig` (compatible con Excel en Windows). El directorio de salida se crea si no existe. El archivo se nombra `{name}.csv`.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame a exportar |
| `name` | `str` | — | Nombre base del archivo (sin extensión) |
| `output_dir` | `Path` | `OUTPUT_DIR` | Directorio de salida |

**Retorna:** `Path` del archivo CSV generado.

**Ejemplo:**

```python
from co_occurrence.viz.export import export_csv

path = export_csv(centralities, name="centralidades_keywords")
# Genera output/centralidades_keywords.csv
```

---

## 20. `obsidian`

Generador de vault Obsidian para exploración interactiva del corpus en el graph view.

**Estructura generada:**

```
vault_bibliometria/
├── _INDEX.md            ← Dashboard con queries Dataview
├── keywords/            ← Una nota .md por keyword
├── authors/             ← Una nota .md por autor
├── journals/            ← Una nota .md por revista
└── communities/         ← Una nota .md por comunidad
```

Cada nota tiene YAML frontmatter con métricas, wikilinks `[[keyword]]` que generan aristas en el graph view de Obsidian, y queries Dataview en el INDEX.

---

### `generate_vault`

```python
def generate_vault(
    G: nx.Graph,
    partition: dict[str, int],
    centralities: pd.DataFrame,
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> Path:
```

Genera el vault Obsidian completo. Orquesta la llamada a los cuatro generadores individuales (`generate_keyword_notes`, `generate_author_notes`, `generate_journal_notes`, `generate_community_notes`) y al generador del índice (`generate_index`).

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia de keywords |
| `partition` | `dict[str, int]` | — | Diccionario `{keyword: comunidad}` |
| `centralities` | `pd.DataFrame` | — | DataFrame de `compute_centralities()` |
| `df` | `pd.DataFrame` | — | DataFrame WoS original |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `Path` del directorio del vault generado.

**Ejemplo:**

```python
from co_occurrence.obsidian import generate_vault

vault = generate_vault(G, partition, centralities, df)
# Abrir vault_path en Obsidian para explorar la red
```

---

### `generate_keyword_notes`

```python
def generate_keyword_notes(
    G: nx.Graph,
    partition: dict[str, int],
    centralities: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
```

Genera una nota `.md` por keyword en `vault_bibliometria/keywords/`. Cada nota incluye frontmatter YAML con `type`, `frequency`, `degree`, `betweenness`, `community` y `tags`, un resumen de métricas, la lista de keywords co-ocurrentes ordenadas por peso (con wikilinks), y un enlace a la nota de comunidad.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `partition` | `dict[str, int]` | — | Diccionario `{keyword: comunidad}` |
| `centralities` | `pd.DataFrame` | — | DataFrame de `compute_centralities()` |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `None`.

---

### `generate_author_notes`

```python
def generate_author_notes(
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
```

Genera una nota `.md` por autor en `vault_bibliometria/authors/`. Cada nota incluye la lista de coautores (wikilinks), keywords utilizadas (wikilinks), revistas en que publica, y lista de artículos con año.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS original |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `None`.

---

### `generate_journal_notes`

```python
def generate_journal_notes(
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
```

Genera una nota `.md` por revista en `vault_bibliometria/journals/`. Cada nota incluye el número de artículos en el corpus, la lista de keywords asociadas (wikilinks) y los autores que publican en ella.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | — | DataFrame WoS original |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `None`.

---

### `generate_community_notes`

```python
def generate_community_notes(
    G: nx.Graph,
    partition: dict[str, int],
    vault_path: Path = VAULT_DIR,
) -> None:
```

Genera una nota `.md` por comunidad en `vault_bibliometria/communities/`. Cada nota incluye la etiqueta con los top-5 keywords, el número de keywords miembros y la lista completa ordenada por frecuencia descendente con wikilinks.

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia |
| `partition` | `dict[str, int]` | — | Diccionario `{keyword: comunidad}` |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `None`.

---

### `generate_index`

```python
def generate_index(
    G: nx.Graph,
    partition: dict[str, int],
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
```

Genera el dashboard principal del vault (`_INDEX.md`) con estadísticas globales del corpus, instrucciones de uso del graph view de Obsidian, y queries Dataview predefinidas (top keywords por frecuencia, keywords puente por betweenness alto y degree bajo).

**Parámetros:**

| Parámetro | Tipo | Defecto | Descripción |
|-----------|------|---------|-------------|
| `G` | `nx.Graph` | — | Grafo de co-ocurrencia de keywords |
| `partition` | `dict[str, int]` | — | Diccionario `{keyword: comunidad}` |
| `df` | `pd.DataFrame` | — | DataFrame WoS original |
| `vault_path` | `Path` | `VAULT_DIR` | Directorio raíz del vault |

**Retorna:** `None`.

---

## Flujo de trabajo completo

El orden recomendado para ejecutar el pipeline completo:

```python
from pathlib import Path
from co_occurrence.io.loader import load_wos_data
from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
from co_occurrence.graphs.weights import apply_all_normalizations
from co_occurrence.analysis.communities import detect_louvain, label_communities
from co_occurrence.analysis.centrality import compute_centralities
from co_occurrence.dimred.manifold import reduce_umap
from co_occurrence.viz.plotly_graphs import plot_network
from co_occurrence.viz.export import export_gexf, export_csv
from co_occurrence.obsidian import generate_vault

# 1. Cargar datos
df = load_wos_data()

# 2. Construir grafo
G = build_cooccurrence_graph(df, min_weight=2)

# 3. Normalizar pesos
G = apply_all_normalizations(G)

# 4. Detectar comunidades
partition = detect_louvain(G)
labels = label_communities(G, partition)

# 5. Calcular centralidades
centralities = compute_centralities(G, partition=partition)

# 6. Reducción dimensional
coords = reduce_umap(G)

# 7. Visualizar
fig = plot_network(G, coords, partition=partition)
fig.show()

# 8. Exportar
export_gexf(G, "cooccurrence_keywords")
export_csv(centralities, "centralidades")

# 9. Vault Obsidian
generate_vault(G, partition, centralities, df)
```
