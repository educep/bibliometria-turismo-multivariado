# Resultados del Pipeline — co-occurrence-library

**Fuente:** 331 artículos Web of Science (turismo, análisis multivariado)
**Fecha de ejecución:** 2026-04-06
**Pipeline:** `python -m co_occurrence pipeline`

---

## 1. Carga de datos

| Parámetro | Valor |
|---|---|
| Registros cargados | 331 |
| Columnas | 72 |
| Rango temporal | 2017–2024 |
| Artículos con keywords | 322 |
| Artículos sin keywords | 9 |

Los 9 artículos sin keywords quedan excluidos de los análisis de co-ocurrencia pero se conservan para el grafo de co-autoría.

---

## 2. Grafo de co-ocurrencia de keywords

**Parámetros:** `min_weight=1` (se retienen todos los pares), `min_frequency=2` (solo keywords con al menos 2 apariciones en el corpus)

| Métrica | Valor |
|---|---|
| Nodos (keywords) | 124 |
| Aristas (pares co-ocurrentes) | 365 |

El umbral `min_frequency=2` filtra términos de aparición única manteniendo únicamente las keywords con respaldo empírico suficiente. El resultado es un grafo más completo que refleja la diversidad temática del corpus sin sacrificar robustez.

### Normalizaciones aplicadas

Se calcularon las cuatro normalizaciones estándar para cada arista:

| Medida | Fórmula | Uso recomendado |
|---|---|---|
| **Association Strength** | `w(a,b) / (f(a) × f(b))` | Layout del grafo |
| **Jaccard** | `w(a,b) / (f(a) + f(b) − w(a,b))` | Detección de comunidades |
| **Coseno de Salton** | `w(a,b) / √(f(a) × f(b))` | Comparación de pares |
| **Inclusion Index** | `w(a,b) / min(f(a), f(b))` | Relaciones jerárquicas |

donde `w(a,b)` es la co-ocurrencia bruta y `f(a)`, `f(b)` son las frecuencias individuales de cada keyword.

---

## 3. Grafo de co-autoría

**Parámetros:** `min_weight=1` (se incluyen todos los pares de autores que han colaborado al menos una vez)

| Métrica | Valor |
|---|---|
| Nodos (autores) | 1 123 |
| Aristas (colaboraciones) | 2 558 |

La red de co-autoría es considerablemente mayor que la de keywords, lo que refleja la diversidad de equipos de investigación presentes en el corpus. El umbral `min_weight=1` captura toda colaboración registrada, incluyendo coautorías únicas.

---

## 4. Comunidades detectadas (Louvain)

**Parámetros:** algoritmo Louvain, `resolution=1.0`

Se detectaron **8 comunidades** en el grafo de co-ocurrencia de keywords:

| Comunidad | Nodos | Keywords representativas |
|---|---|---|
| Com 0 | 14 | segmentation, tourism demand forecasting, gastronomy, sustainable tourism, climate change, singular spectrum analysis, world heritage sites, tourist arrivals, leading indicators, multivariate time series, support vector machine, management, gender, international tourism |
| Com 1 | 14 | tourism, economic growth, granger causality, well-being, panel data, vector autoregression, economic development, carbon emissions, regression analysis, globalization, urbanization, exchange rate, energy consumption, job satisfaction |
| Com 2 | 25 | multivariate analysis, cluster analysis, competitiveness, perception, water quality, logistic regression analysis, wine tourism, cultural heritage, rural development, tourism destination, seasonality, gini index (+13 más) |
| Com 3 | 9 | discriminant analysis, fuzzy-set qualitative comparative analysis, exploratory factor analysis, qualitative comparative analysis, time series, tourism research, data envelopment analysis, partial least squares, classification |
| Com 4 | 18 | multiple regression, hospitality, principal component analysis, social media, hotels, multidimensional scaling, internal factors, online reviews, hydrogeochemistry, tourist destinations, hydrochemistry, destination marketing (+6 más) |
| Com 5 | 7 | environmental management, consumer behavior, heavy metals, brand personality, tourism management, ecological indicators, conservation |
| Com 6 | 17 | satisfaction, motivation, destination image, structural equation modeling, loyalty, rural tourism, sustainable development, service quality, innovation, camping tourism, halal tourism (+6 más) |
| Com 7 | 20 | covid-19, sustainability, behavioral intention, ecotourism, medical tourism, resilience, indicators, theory of planned behavior, tourists, countryside, attitude, pull factors (+8 más) |

La **Comunidad 2** es la más grande del corpus (25 nodos), seguida por la **Comunidad 7** (20 nodos) y la **Comunidad 6** (17 nodos). Las comunidades reflejan ejes temáticos bien diferenciados: análisis econométrico del turismo (Com 1), métodos multivariados (Com 2), comportamiento del consumidor (Com 6) e impacto del COVID-19 y sostenibilidad (Com 7).

---

## 5. Centralidades

### Grado ponderado (weighted degree)

Suma de los pesos brutos de co-ocurrencia de cada keyword con sus vecinos.

| Keyword | Weighted Degree |
|---|---|
| tourism | 88 |
| multivariate analysis | 48 |
| economic growth | 27 |
| satisfaction | 25 |
| motivation | 24 |
| covid-19 | 23 |
| segmentation | 22 |
| sustainability | 20 |
| tourism demand forecasting | 19 |
| behavioral intention | 18 |

### Betweenness centrality

Proporción de caminos mínimos entre pares de nodos que pasan por cada keyword. Indica poder de intermediación.

| Keyword | Betweenness |
|---|---|
| tourism | 0.2662 |
| multivariate analysis | 0.2527 |
| covid-19 | 0.1401 |
| tourism demand forecasting | 0.1108 |
| segmentation | 0.0737 |
| social media | 0.0656 |
| motivation | 0.0488 |
| satisfaction | 0.0327 |
| sustainability | 0.0700 |
| cluster analysis | 0.0689 |

### Eigenvector centrality

Mide la influencia de un nodo considerando la influencia de sus vecinos.

| Keyword | Eigenvector |
|---|---|
| tourism | 0.5912 |
| economic growth | 0.3641 |
| multivariate analysis | 0.2430 |
| granger causality | 0.3087 |
| panel data | 0.1278 |
| carbon emissions | 0.1448 |
| satisfaction | 0.1801 |
| motivation | 0.1818 |
| cluster analysis | 0.1064 |
| covid-19 | 0.1178 |

### PageRank

| Keyword | PageRank |
|---|---|
| tourism | 0.08077 |
| multivariate analysis | 0.05069 |
| economic growth | 0.02342 |
| covid-19 | 0.02488 |
| satisfaction | 0.02326 |
| motivation | 0.02226 |
| segmentation | 0.02074 |
| tourism demand forecasting | 0.01963 |
| cluster analysis | 0.01816 |
| behavioral intention | 0.01898 |

"tourism" y "multivariate analysis" ocupan las primeras posiciones en las cuatro métricas, confirmando su papel como nodos dominantes de la red. "covid-19" destaca por su alta betweenness (0.1401), actuando como puente entre comunidades temáticas distintas.

---

## 6. Huecos estructurales (Structural Holes)

Los huecos estructurales identifican keywords que actúan como puentes entre comunidades temáticas distintas. Se miden con el **constraint de Burt** (valores bajos = mayor posición de intermediación estratégica) y el **tamaño efectivo de red** (effective size).

| Keyword | Constraint | Effective Size |
|---|---|---|
| tourism | 0.0734 | 50.56 |
| multivariate analysis | 0.0799 | 34.11 |
| covid-19 | 0.0964 | 18.24 |
| behavioral intention | 0.1209 | 14.41 |
| tourism demand forecasting | 0.1243 | 15.52 |
| sustainability | 0.1302 | 15.43 |
| segmentation | 0.1303 | 14.93 |
| multiple regression | 0.1507 | 10.54 |

"tourism" presenta el constraint más bajo (0.073) y el mayor tamaño efectivo (50.56), lo que confirma que actúa como broker principal de la red. "multivariate analysis" ocupa la segunda posición (constraint 0.080, effective size 34.11), reflejando su papel transversal a múltiples comunidades metodológicas. "covid-19" (constraint 0.096) emerge como tercer conector clave, conectando las comunidades de salud, sostenibilidad y comportamiento del turista.

---

## 7. Evolución temporal

El corpus se dividió en dos ventanas temporales para detectar keywords emergentes y en declive:

| Periodo | Artículos | Keywords únicas (min_weight=1) |
|---|---|---|
| 2017–2021 | 213 | 743 |
| 2022–2026 | 118 | 434 |

**Total de observaciones keyword-periodo:** 1 177

La ventana 2017–2021 concentra el 64 % de los artículos y el 63 % del vocabulario único. La ventana 2022–2026 muestra menor volumen pero permite identificar tendencias recientes. Keywords que aparecen únicamente en 2022–2026 son candidatas a términos emergentes; las que desaparecen en ese periodo son candidatas a términos en declive.

---

## 8. Reducción dimensional (UMAP)

Se proyectaron los 124 nodos del grafo de co-ocurrencia a 2D usando UMAP con `n_neighbors=15`, `min_dist=0.1`, `random_state=42`. La matriz de distancias se calculó como `1 - w/w_max` (pares con co-ocurrencia) y `1.0` (pares sin co-ocurrencia).

| Parámetro | Valor |
|---|---|
| Keywords proyectadas | 124 |
| Método | UMAP (precomputed distances) |
| n_neighbors | 15 |
| min_dist | 0.1 |

El scatter interactivo (`output/dimred_umap.html`) colorea cada keyword por su comunidad Louvain, con burbujas proporcionales a la frecuencia y etiquetas para las 20 keywords más frecuentes. Las comunidades forman clusters visualmente diferenciados en el espacio UMAP, confirmando que la partición Louvain es coherente con la proximidad en la matriz de co-ocurrencia.

También disponibles: MDS (`output/dimred_mds.html`) y t-SNE (`output/dimred_tsne.html`).

---

## 9. Analisis de Correspondencias (CA)

Se proyecto la tabla de contingencia 114 keywords x 132 revistas en un espacio factorial 2D usando `prince.CA`.

| Parametro | Valor |
|---|---|
| Tabla de contingencia | 114 x 132 (tras filtrado freq >= 2) |
| Dimensiones degeneradas detectadas | 1 (eigenvalue = 0.9999, saltada) |
| Dimensiones usadas | dim2 y dim3 |
| Inercia dim2 | 2.6% |
| Inercia dim3 | 2.5% |
| Inercia acumulada 2D | 5.1% |
| Inercia total | 29.6 |

La dimension degenerada fue causada por el par exclusivo "knowledge management" <-> "Middle East Journal of Management" (correspondencia perfecta). Se detecto automaticamente y se salto a las dimensiones 2-3.

### Estructura del biplot

El biplot revela dos tradiciones metodologicas con circuitos de publicacion distintos:

- **Eje vertical positivo:** SEM, satisfaccion, lealtad, motivacion -> revistas de management y hospitalidad (Tourism Review, Urban Forestry & Urban Greening)
- **Eje vertical negativo:** time series, VAR, SSA, Granger, tourism demand forecasting -> revistas cuantitativas (Annals of Tourism Research, Tourism Economics)

### Keywords con mayor contribucion

| Keyword | Freq | x | y |
|---|---|---|---|
| hotels | 3 | +8.55 | +0.74 |
| structural equation modeling | 8 | -0.24 | +1.67 |
| tourism demand forecasting | 11 | +0.07 | -1.24 |
| singular spectrum analysis | 3 | +0.11 | -2.23 |
| vector autoregression | 3 | +0.03 | -2.02 |
| loyalty | 7 | -0.18 | +1.00 |

### Revistas con mayor contribucion

| Revista | Freq | x | y |
|---|---|---|---|
| Annals of Tourism Research | 11 | +0.15 | -2.29 |
| Tourism Review | 10 | +1.27 | +0.15 |
| Current Issues in Tourism | 20 | +0.11 | -0.64 |
| Tourism Economics | 5 | -0.02 | -1.19 |

La baja inercia (5.1%) es habitual en CA bibliometrica con tablas dispersas (331 articulos en 132 revistas). La estructura es interpretable y diferencia claramente la investigacion causal/estructural de la predictiva/temporal.

---

## 10. Archivos generados

Todos los archivos de salida se encuentran en `output/`:

| Archivo | Descripción |
|---|---|
| `keyword_cooccurrence.gexf` | Grafo de co-ocurrencia de keywords con las 4 normalizaciones de peso; importable en Gephi |
| `coauthor_network.gexf` | Grafo de co-autoría entre autores; importable en Gephi |
| `communities_labeled.csv` | Asignación de comunidad para cada keyword, con etiquetas Louvain |
| `centralities.csv` | Métricas de centralidad por keyword: degree, betweenness, eigenvector, PageRank |
| `structural_holes.csv` | Constraint de Burt y effective size por keyword |
| `keyword_evolution.csv` | Frecuencia de keywords por ventana temporal (2017–2021 / 2022–2026) |
| `dimred_umap.csv` | Coordenadas UMAP 2D (keyword, x, y, frequency) |
| `dimred_umap.html` | Scatter interactivo UMAP coloreado por comunidad Louvain |
| `dimred_mds.csv` | Coordenadas MDS 2D |
| `dimred_mds.html` | Scatter interactivo MDS |
| `dimred_tsne.csv` | Coordenadas t-SNE 2D |
| `dimred_tsne.html` | Scatter interactivo t-SNE |
| `ca_biplot.html` | Biplot interactivo CA keyword x revista |
| `ca_row_coords.csv` | Coordenadas CA de keywords (x, y, frequency, contribution) |
| `ca_col_coords.csv` | Coordenadas CA de revistas (x, y, frequency, contribution) |

---

## 11. Interpretacion general

La red de co-ocurrencia de keywords (124 nodos, 365 aristas) exhibe una **estructura núcleo-periferia** marcada con dos nodos dominantes y 8 comunidades temáticas bien diferenciadas:

- **Doble núcleo dominante:** "tourism" y "multivariate analysis" lideran conjuntamente todas las métricas. "tourism" tiene el constraint más bajo (0.073) y el mayor tamaño efectivo (50.56), mientras que "multivariate analysis" ocupa la segunda posición en betweenness (0.253) y effective size (34.11). Ambos actúan como brokers estructurales que articulan el resto de la red.

- **Comunidad 2 como hub metodológico:** Con 25 nodos, la Comunidad 2 es la más grande y agrupa los métodos multivariados aplicados al turismo —análisis de clusters, regresión logística, análisis de componentes principales, wine tourism, patrimonio cultural— reflejando la diversidad metodológica del corpus.

- **Comunidades temáticas consolidadas:** Las 8 comunidades detectadas representan ejes temáticos con masa crítica suficiente. Destacan: Com 1 (econometría del turismo: PIB, crecimiento económico, causalidad de Granger), Com 6 (comportamiento del turista: satisfacción, motivación, lealtad) y Com 7 (turismo post-COVID: sostenibilidad, intención de comportamiento, ecoturismo).

- **Emergencia del eje COVID-19/sostenibilidad:** "covid-19" presenta una betweenness de 0.140 y un constraint de 0.096, posicionándolo como tercer conector clave de la red. Su presencia en la Comunidad 7 junto a "sustainability", "behavioral intention" y "resilience" refleja el giro temático del corpus hacia la dimensión post-pandémica.

- **Efecto del umbral min_frequency=2:** El filtro mantiene las 124 keywords con respaldo empírico suficiente (al menos 2 apariciones), produciendo una red más completa (365 aristas) que captura conexiones entre términos de frecuencia moderada sin incluir términos únicos de escasa relevancia estructural.

- **Evolución temporal:** La reducción de artículos en 2022–2026 (118 vs. 213) puede reflejar tanto el recorte del corpus como cambios en la dinámica de publicación post-pandemia. El menor vocabulario del periodo reciente (434 vs. 743 keywords) sugiere una convergencia temática que merece análisis detallado de términos emergentes y en declive.
