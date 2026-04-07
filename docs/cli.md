# Referencia de la CLI — co-occurrence-library

La interfaz de línea de comandos se invoca con `python -m co_occurrence` seguido del subcomando deseado.
El punto de entrada es `src/co_occurrence/cli.py`, construido con [Typer](https://typer.tiangolo.com/).

---

## Índice

1. [load](#load)
2. [build-keywords](#build-keywords)
3. [build-coauthors](#build-coauthors)
4. [communities](#communities)
5. [centralities](#centralities)
6. [evolution](#evolution)
7. [dimred](#dimred)
8. [ca](#ca)
9. [vault](#vault)
10. [pipeline](#pipeline)

---

## `load`

Carga el archivo Excel WoS y muestra un resumen del dataset.

### Sintaxis

```bash
python -m co_occurrence load [--path RUTA]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--path`  | `Path` | `data/anal multiv 331 artic completo.xlsx` | Ruta alternativa al archivo Excel WoS. Si se omite, usa la ruta definida en `config.py`. |

### Salida en consola

```
Registros: 331
Columnas: 70
Años: 2000-2023
Keywords no nulas: 298
```

### Archivos generados

Ninguno. Este comando es exclusivamente de diagnóstico.

### Ejemplos

```bash
# Usar la ruta por defecto
python -m co_occurrence load

# Especificar un archivo diferente
python -m co_occurrence load --path data/mi_exportacion_wos.xlsx
```

---

## `build-keywords`

Construye el grafo de co-ocurrencia a partir del campo `Author Keywords` del dataset WoS y lo exporta en formato GEXF.

### Sintaxis

```bash
python -m co_occurrence build-keywords [--min-weight N] [--min-frequency N]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--min-weight` | `int` | `1` | Peso mínimo para incluir una arista. Pares de keywords que co-ocurran menos de N veces son descartados. |
| `--min-frequency` | `int` | `2` | Frecuencia mínima de un keyword para ser incluido como nodo. Keywords que aparezcan en menos de N artículos son eliminados antes de construir el grafo. |

### Salida en consola

```
Grafo: 487 nodos, 1243 aristas
```

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/keyword_cooccurrence.gexf` | Grafo de co-ocurrencia en formato GEXF, importable directamente en Gephi. |

### Ejemplos

```bash
# Valores por defecto (min-weight=1, min-frequency=2)
python -m co_occurrence build-keywords

# Filtrado más estricto: solo pares con 5 o más co-ocurrencias, keywords en 3+ artículos
python -m co_occurrence build-keywords --min-weight 5 --min-frequency 3
```

---

## `build-coauthors`

Construye la red de co-autoría a partir del campo `Authors` y la exporta en formato GEXF.

### Sintaxis

```bash
python -m co_occurrence build-coauthors [--min-weight N]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--min-weight` | `int` | `1` | Peso mínimo para incluir una arista. Con valor 1 se incluyen todos los pares de autores que hayan colaborado al menos una vez. |

### Salida en consola

```
Grafo: 812 nodos, 634 aristas
```

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/coauthor_network.gexf` | Red de co-autoría en formato GEXF. |

### Ejemplos

```bash
# Incluir todas las colaboraciones (por defecto)
python -m co_occurrence build-coauthors

# Solo pares de autores con 2 o más artículos en común
python -m co_occurrence build-coauthors --min-weight 2
```

---

## `communities`

Detecta comunidades temáticas en el grafo de co-ocurrencia de keywords. Construye el grafo internamente con `min_weight=1`, `min_frequency=2`. Admite dos algoritmos: Louvain (por defecto) y Leiden. Exporta la tabla de comunidades etiquetadas semánticamente.

### Sintaxis

```bash
python -m co_occurrence communities [--algorithm ALGO] [--resolution R]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--algorithm` | `str` | `louvain` | Algoritmo de detección. Valores válidos: `louvain`, `leiden`. |
| `--resolution` | `float` | `1.0` | Parámetro de resolución para Louvain. Valores mayores producen más comunidades y más pequeñas; valores menores generan comunidades más grandes. Este parámetro se ignora cuando se usa `leiden`. |

### Salida en consola

Tabla con las comunidades detectadas y sus keywords representativas:

```
community_id  label                    size  top_keywords
           0  sustainable tourism        42  sustainability, ecotourism, ...
           1  digital marketing          31  social media, e-tourism, ...
```

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/communities_labeled.csv` | Tabla con `community_id`, etiqueta semántica, tamaño y keywords principales de cada comunidad. |

### Ejemplos

```bash
# Louvain con resolución por defecto
python -m co_occurrence communities

# Louvain con resolución alta (más comunidades, más pequeñas)
python -m co_occurrence communities --algorithm louvain --resolution 1.5

# Leiden (ignora --resolution)
python -m co_occurrence communities --algorithm leiden
```

---

## `centralities`

Calcula un conjunto completo de métricas de centralidad sobre el grafo de co-ocurrencia de keywords: degree, betweenness, eigenvector, PageRank y huecos estructurales (constraint de Burt). Añade la comunidad Louvain de cada nodo.

### Sintaxis

```bash
python -m co_occurrence centralities
```

### Parámetros

Este comando no tiene parámetros configurables. Construye internamente el grafo con `min_weight=1`, `min_frequency=2` y detecta comunidades Louvain con `resolution=1.0`.

### Salida en consola

Las 20 keywords con mayor centralidad:

```
keyword              degree  betweenness  eigenvector  pagerank  community
tourism                 ...          ...          ...       ...          0
sustainability          ...          ...          ...       ...          0
```

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/centralities.csv` | Tabla completa con todas las métricas de centralidad por keyword. |

### Ejemplos

```bash
python -m co_occurrence centralities
```

---

## `evolution`

Analiza la evolución temporal de las keywords usando ventanas deslizantes de N años. Identifica keywords emergentes (crecimiento reciente) y en declive (reducción de uso). Exporta métricas de evolución por keyword y ventana temporal.

### Sintaxis

```bash
python -m co_occurrence evolution [--window N]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--window` | `int` | `5` | Tamaño de la ventana temporal en años. Determina el intervalo usado para construir cada grafo parcial. |

### Salida en consola

```
Keywords emergentes (23):
  + digital transformation
  + overtourism
  + ...

Keywords en declive (18):
  - heritage tourism
  - competitiveness
  - ...
```

Se muestran hasta 20 keywords por categoría.

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/keyword_evolution.csv` | Métricas de evolución por keyword y ventana temporal (frecuencia, degree, tendencia). |

### Ejemplos

```bash
# Ventana de 5 años (por defecto)
python -m co_occurrence evolution

# Ventana de 3 años para análisis más granular
python -m co_occurrence evolution --window 3

# Ventana de 10 años para tendencias largas
python -m co_occurrence evolution --window 10
```

---

## `dimred`

Ejecuta reducción dimensional sobre el grafo de co-ocurrencia de keywords y genera un scatter plot interactivo coloreado por comunidad Louvain.

### Sintaxis

```bash
python -m co_occurrence dimred [--method METODO] [--top-labels N]
```

### Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `--method` | `str` | `umap` | Método de reducción dimensional. Valores válidos: `mds`, `tsne`, `umap`. |
| `--top-labels` | `int` | `20` | Número de keywords más frecuentes que muestran etiqueta visible en el scatter. |

### Salida en consola

```
UMAP: 124 keywords -> output/dimred_umap.html
```

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/dimred_{method}.csv` | Coordenadas 2D (x, y), keyword y frecuencia. |
| `output/dimred_{method}.html` | Scatter plot interactivo Plotly coloreado por comunidad Louvain. Burbujas proporcionales a la frecuencia. Top-N keywords etiquetadas. |

### Ejemplos

```bash
# UMAP (recomendado — preserva estructura local y global)
python -m co_occurrence dimred --method umap

# MDS (preserva distancias globales, clásico en bibliometría)
python -m co_occurrence dimred --method mds

# t-SNE (revela clusters locales, no preserva distancias globales)
python -m co_occurrence dimred --method tsne

# UMAP con más etiquetas visibles
python -m co_occurrence dimred --method umap --top-labels 30
```

---

## `ca`

Ejecuta un Analisis de Correspondencias (CA) sobre la tabla de contingencia keyword x revista (u otras columnas WoS) y genera un biplot interactivo donde ambas entidades se proyectan en el mismo espacio factorial.

### Sintaxis

```bash
python -m co_occurrence ca [--row-column COLUMNA] [--col-column COLUMNA]
```

### Parametros

| Parametro | Tipo | Por defecto | Descripcion |
|-----------|------|-------------|-------------|
| `--row-column` | `str` | `Author Keywords` | Columna WoS para las filas de la tabla de contingencia. |
| `--col-column` | `str` | `Source Title` | Columna WoS para las columnas de la tabla de contingencia. |

### Salida en consola

```
CA: 114 filas x 132 columnas -> output/ca_biplot.html
```

### Archivos generados

| Archivo | Descripcion |
|---------|-------------|
| `output/ca_biplot.html` | Biplot interactivo Plotly con keywords (circulos azules) y revistas (triangulos coral) en el mismo espacio 2D. Tamanio proporcional a frecuencia marginal. Etiquetas para las entidades con mayor contribucion a la inercia. |
| `output/ca_row_coords.csv` | Coordenadas CA de keywords (x, y, frequency, contribution, entity_type). |
| `output/ca_col_coords.csv` | Coordenadas CA de revistas (x, y, frequency, contribution, entity_type). |

### Notas tecnicas

- Las keywords se normalizan con el diccionario de sinonimos y se filtran con la stoplist.
- La tabla de contingencia se filtra iterativamente para eliminar filas y columnas con frecuencia < 2.
- Las dimensiones degeneradas (eigenvalue >= 0.99, causadas por pares exclusivos keyword-revista) se detectan y saltan automaticamente.
- La inercia explicada por los dos primeros ejes se muestra en las etiquetas del grafico.

### Ejemplos

```bash
# Biplot keyword x revista (por defecto)
python -m co_occurrence ca

# Biplot keyword x categoria WoS
python -m co_occurrence ca --col-column "WoS Categories"
```

---

## `vault`

Genera un vault de Obsidian con notas estructuradas para keywords, autores, revistas y comunidades. Cada nota incluye YAML frontmatter con métricas, wikilinks para generar el graph view y queries Dataview en el índice.

### Sintaxis

```bash
python -m co_occurrence vault
```

### Parámetros

Este comando no tiene parámetros configurables. El vault se genera en la ruta `vault_bibliometria/` dentro del directorio raíz del proyecto.

### Salida en consola

```
Vault generado en /ruta/al/proyecto/vault_bibliometria
```

### Archivos generados

El vault se crea en `vault_bibliometria/` con la siguiente estructura:

```
vault_bibliometria/
├── keywords/       # Una nota por keyword con métricas y wikilinks
├── authors/        # Una nota por autor con colaboradores y publicaciones
├── journals/       # Una nota por revista
├── communities/    # Una nota por comunidad con sus keywords principales
└── INDEX.md        # Índice general con queries Dataview
```

Cada nota de keyword incluye:
- Frontmatter YAML: `type`, `frequency`, `degree`, `betweenness`, `community`, `tags`
- Wikilinks `[[keyword]]` hacia keywords co-ocurrentes
- Enlace a la comunidad temática

### Ejemplos

```bash
python -m co_occurrence vault
```

Tras ejecutar el comando, abrir la carpeta `vault_bibliometria/` como vault en Obsidian para explorar el graph view y las queries Dataview.

---

## `pipeline`

Ejecuta el pipeline analítico completo en un solo paso: carga de datos, construccion de grafos (keywords y co-autoría), normalización de pesos, detección de comunidades, cálculo de centralidades, huecos estructurales y evolución temporal. Exporta todos los archivos de salida.

### Sintaxis

```bash
python -m co_occurrence pipeline
```

### Parámetros

Este comando no tiene parámetros. Usa todos los valores por defecto definidos en `config.py`.

### Pasos ejecutados internamente

| Paso | Operación |
|------|-----------|
| 1 | Carga de datos WoS desde `data/` |
| 2 | Construcción del grafo de co-ocurrencia de keywords (`min_weight=1`, `min_frequency=2`) |
| 3 | Construcción de la red de co-autoría (`min_weight=1`) |
| 4 | Normalización de pesos (Association Strength, Jaccard, Salton, Inclusion) |
| 5 | Detección de comunidades Louvain (`resolution=1.0`) y etiquetado semántico |
| 6 | Cálculo de centralidades (degree, betweenness, eigenvector, PageRank) |
| 7 | Cálculo de huecos estructurales (constraint de Burt) |
| 8 | Análisis de evolución temporal (`window=5`) |
| 9 | Reduccion dimensional UMAP + scatter interactivo por comunidad |
| 10 | Analisis de Correspondencias (keyword x revista) + biplot interactivo |
| 11 | Exportacion de todos los archivos de salida |

### Salida en consola

```
Pipeline completado. Outputs en output/
```

El progreso detallado se registra con `loguru` a nivel `INFO`.

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `output/keyword_cooccurrence.gexf` | Grafo de co-ocurrencia con pesos normalizados |
| `output/coauthor_network.gexf` | Red de co-autoría |
| `output/communities_labeled.csv` | Comunidades con etiqueta semántica y keywords principales |
| `output/centralities.csv` | Métricas de centralidad por keyword |
| `output/structural_holes.csv` | Métricas de huecos estructurales (constraint, effective size) |
| `output/keyword_evolution.csv` | Evolución temporal de keywords por ventana |
| `output/dimred_umap.csv` | Coordenadas UMAP 2D de keywords |
| `output/dimred_umap.html` | Scatter interactivo UMAP coloreado por comunidad |
| `output/ca_biplot.html` | Biplot interactivo CA keyword x revista |
| `output/ca_row_coords.csv` | Coordenadas CA de keywords |
| `output/ca_col_coords.csv` | Coordenadas CA de revistas |

### Ejemplos

```bash
# Ejecutar el pipeline completo
python -m co_occurrence pipeline
```

Este es el comando recomendado para una primera ejecución o para regenerar todos los outputs desde cero.

---

## Referencia rápida

```bash
python -m co_occurrence load                                  # Diagnóstico del dataset
python -m co_occurrence build-keywords                        # Grafo de keywords (min-weight=1, min-frequency=2)
python -m co_occurrence build-coauthors --min-weight 1        # Red de co-autoría
python -m co_occurrence communities --algorithm louvain       # Comunidades Louvain
python -m co_occurrence communities --algorithm leiden        # Comunidades Leiden
python -m co_occurrence centralities                          # Métricas de centralidad
python -m co_occurrence evolution --window 5                  # Evolución temporal
python -m co_occurrence dimred --method umap                  # Reducción dimensional UMAP
python -m co_occurrence dimred --method mds                   # Reducción dimensional MDS
python -m co_occurrence dimred --method tsne                  # Reduccion dimensional t-SNE
python -m co_occurrence ca                                    # Biplot CA keyword x revista
python -m co_occurrence vault                                 # Vault Obsidian
python -m co_occurrence pipeline                              # Pipeline completo
```

Para obtener ayuda sobre cualquier subcomando:

```bash
python -m co_occurrence --help
python -m co_occurrence load --help
python -m co_occurrence communities --help
```
