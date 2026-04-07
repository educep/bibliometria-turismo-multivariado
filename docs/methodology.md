# Fundamentos Metodológicos

Documento de referencia para el proyecto **co-occurrence-library** (331 artículos WoS, análisis bibliométrico multivariado en turismo).

---

## 1. Co-ocurrencia

### Definición

La **co-ocurrencia** mide la frecuencia con la que dos entidades aparecen juntas en el mismo documento. Sea $A$ el conjunto de artículos del corpus; para dos entidades $a$ y $b$, el peso de co-ocurrencia se define como:

$$w(a, b) = |\{ d \in A \mid a \in d \text{ y } b \in d \}|$$

Es decir, $w(a, b)$ es el número de artículos en los que $a$ y $b$ co-ocurren. La frecuencia marginal de una entidad $a$ es:

$$f(a) = |\{ d \in A \mid a \in d \}|$$

Con estas definiciones se construye una **matriz de co-ocurrencia** $W$ donde $W_{ij} = w(a_i, a_j)$, simétrica y con diagonal $W_{ii} = f(a_i)$.

### Tipos de redes bibliométricas

| Red | Nodos | Arista $w(a,b)$ |
|-----|-------|-----------------|
| **Co-ocurrencia de keywords** | Palabras clave (author keywords, KeyWords Plus) | Artículos en que ambas keywords aparecen juntas |
| **Co-autoría** | Autores | Artículos firmados conjuntamente |
| **Co-citación** | Referencias citadas | Artículos que citan ambas referencias simultáneamente |
| **Acoplamiento bibliográfico** | Artículos fuente | Referencias compartidas entre dos artículos |

Cada tipo de red captura una dimensión distinta de la estructura intelectual del campo. La co-ocurrencia de keywords refleja proximidad temática; la co-autoría, colaboración; la co-citación, similitud de base intelectual; el acoplamiento bibliográfico, similitud de marco teórico.

### Grafos bipartitos

Además de las redes unimodales anteriores, es posible construir **grafos bipartitos** que relacionan dos tipos de entidades distintas. En un grafo bipartito $G = (U, V, E)$ los nodos se dividen en dos conjuntos disjuntos $U$ y $V$, y las aristas solo conectan nodos de conjuntos distintos. Las proyecciones unimodales de un bipartito recuperan las redes de co-ocurrencia.

Las redes bipartitas implementadas son:

- **Autor–keyword**: autores y palabras clave vinculados por el uso de una keyword en un artículo del autor.
- **Revista–keyword**: revistas y keywords vinculadas por la publicación de artículos con esa keyword en esa revista.
- **País–keyword**: países (extraídos de las afiliaciones) y keywords vinculados por los artículos en que ambos aparecen.

---

## 2. Normalización de pesos

Los pesos crudos $w(a, b)$ están influidos por la frecuencia marginal de las entidades: dos keywords muy frecuentes co-ocurrirán muchas veces aunque no estén especialmente relacionadas. Las **medidas de asociación normalizadas** corrigen este sesgo.

Sea $N = |A|$ el número total de artículos del corpus.

### 2.1 Association Strength (Equivalence Index)

$$AS(a, b) = \frac{w(a, b)}{f(a) \cdot f(b)}$$

Es la medida estándar de VOSviewer (Van Eck & Waltman, 2010). Se interpreta como la razón entre la co-ocurrencia observada y la esperada bajo independencia estadística (asumiendo $f(a)/N$ y $f(b)/N$ como probabilidades marginales, $AS$ es proporcional al cociente de verosimilitudes). **Uso principal:** layout de grafos, identificación de asociaciones fuertes independientemente de la frecuencia.

### 2.2 Índice de Jaccard

$$J(a, b) = \frac{w(a, b)}{f(a) + f(b) - w(a, b)}$$

El denominador es el tamaño de la unión $|d_a \cup d_b|$, por lo que $J \in [0, 1]$. Es equivalente al coeficiente de Jaccard para conjuntos. **Uso principal:** detección de comunidades (penaliza conjuntos muy dispares en tamaño).

### 2.3 Coseno de Salton

$$S(a, b) = \frac{w(a, b)}{\sqrt{f(a) \cdot f(b)}}$$

Equivale al coseno del ángulo entre los vectores de co-ocurrencia de $a$ y $b$, por lo que $S \in [0, 1]$. Es menos sensible que Jaccard a diferencias de frecuencia extremas. **Uso principal:** similitud temática, matrices de distancia para reducción dimensional.

### 2.4 Índice de Inclusión

$$I(a, b) = \frac{w(a, b)}{\min(f(a), f(b))}$$

Mide en qué proporción la entidad menos frecuente está "subsumida" por la más frecuente. Si $I(a, b) \approx 1$, prácticamente todos los documentos de $a$ también contienen $b$ (o viceversa). **Uso principal:** detección de relaciones jerárquicas y términos genéricos que engloban a términos específicos.

### Comparación

| Medida | Rango | Simétrica | Sensibilidad a frecuencia |
|--------|-------|-----------|--------------------------|
| $AS$ | $[0, \infty)$ | Sí | Baja (divide por producto) |
| $J$ | $[0, 1]$ | Sí | Media |
| $S$ | $[0, 1]$ | Sí | Media (divide por media geométrica) |
| $I$ | $[0, 1]$ | No | Alta (asimétrica por diseño) |

---

## 3. Detección de comunidades

Una **comunidad** es un subconjunto de nodos con mayor densidad de conexiones internas que externas. En el contexto bibliométrico, las comunidades de keywords corresponden a clústeres temáticos o frentes de investigación.

### 3.1 Algoritmo de Louvain

Blondel et al. (2008) proponen un algoritmo greedy en dos fases que maximiza la **modularidad**:

$$Q = \frac{1}{2m} \sum_{ij} \left[ w_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

donde $m = \sum_{ij} w_{ij} / 2$ es el peso total del grafo, $k_i = \sum_j w_{ij}$ el grado ponderado del nodo $i$, $c_i$ la comunidad asignada a $i$, y $\delta$ la función delta de Kronecker. El algoritmo itera: (1) reasignación local de nodos a la comunidad vecina que maximiza $\Delta Q$; (2) contracción del grafo agregando comunidades como supernodos. Complejidad $O(n \log n)$.

**Limitación:** puede producir comunidades internamente desconectadas para resoluciones altas.

### 3.2 Algoritmo de Leiden

Traag et al. (2019) extienden Louvain garantizando que las comunidades resultantes sean **bien conectadas** (cada comunidad es un subgrafo conectado). Introduce una fase de refinamiento que permite la subdivisión de comunidades mal formadas. Leiden es más lento que Louvain pero produce particiones de mayor calidad topológica.

### 3.3 Parámetro de resolución

Ambos algoritmos aceptan un parámetro de resolución $\gamma > 0$ que modula la función de calidad:

$$Q_\gamma = \frac{1}{2m} \sum_{ij} \left[ w_{ij} - \gamma \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

- $\gamma < 1$: comunidades más grandes (menos granularidad).
- $\gamma > 1$: comunidades más pequeñas (mayor granularidad).
- $\gamma = 1$: modularidad estándar de Newman-Girvan.

### 3.4 Etiquetado semántico

Cada comunidad se etiqueta automáticamente usando las $N$ keywords con mayor grado ponderado dentro de la comunidad. Este procedimiento es equivalente a identificar el "núcleo temático" de cada clúster por centralidad interna.

---

## 4. Centralidades

Las **métricas de centralidad** cuantifican la importancia estructural de cada nodo en la red. Para una keyword, indican su relevancia en la literatura analizada.

### 4.1 Grado y grado ponderado

El **grado** $k_i$ es el número de vecinos del nodo $i$:

$$k_i = \sum_{j \neq i} \mathbb{1}[w_{ij} > 0]$$

El **grado ponderado** (o fuerza del nodo) incorpora los pesos de las aristas:

$$s_i = \sum_{j \neq i} w_{ij}$$

En redes de keywords, $k_i$ indica cuántas otras keywords co-ocurren con $i$; $s_i$ indica la intensidad total de esas co-ocurrencias.

### 4.2 Betweenness (intermediación)

$$BC(i) = \sum_{s \neq i \neq t} \frac{\sigma_{st}(i)}{\sigma_{st}}$$

donde $\sigma_{st}$ es el número de caminos geodésicos entre $s$ y $t$, y $\sigma_{st}(i)$ los que pasan por $i$. Una keyword con alta betweenness actúa como **puente** entre clústeres temáticos distintos, siendo crucial para la cohesión del campo.

### 4.3 Closeness (cercanía)

$$CC(i) = \frac{n-1}{\sum_{j \neq i} d(i,j)}$$

donde $d(i,j)$ es la distancia geodésica entre $i$ y $j$. Mide la capacidad de un nodo para alcanzar rápidamente el resto de la red. En grafos no conectados se usa la variante de Wasserman-Faust normalizada por componente.

### 4.4 Centralidad de eigenvector

La centralidad de eigenvector $x_i$ satisface:

$$x_i = \frac{1}{\lambda} \sum_j w_{ij} x_j \quad \Leftrightarrow \quad \mathbf{W x} = \lambda \mathbf{x}$$

donde $\lambda$ es el mayor eigenvalor de la matriz de adyacencia $W$ y $\mathbf{x}$ el eigenvector correspondiente. Un nodo es influyente si está conectado a otros nodos influyentes.

### 4.5 PageRank

$$PR(i) = \frac{1-d}{n} + d \sum_{j \in \mathcal{N}(i)} \frac{w_{ji}}{s_j} PR(j)$$

donde $d \in (0,1)$ es el factor de amortiguamiento (típicamente $d = 0.85$) y $\mathcal{N}(i)$ los vecinos de $i$. PageRank es conceptualmente similar a la centralidad de eigenvector pero con amortiguamiento que evita la concentración excesiva de importancia en cliques.

### 4.6 Agujeros estructurales (Burt, 1992)

Los **agujeros estructurales** son posiciones en la red donde un nodo conecta grupos que de otro modo estarían desconectados. Burt (1992) propone dos métricas complementarias:

**Tamaño efectivo** de la red egocéntrica de $i$:

$$ES(i) = n_i - \frac{\sum_{j \in \mathcal{N}(i)} \sum_{q \in \mathcal{N}(i), q \neq j} p_{iq} m_{jq}}{n_i}$$

donde $p_{iq}$ es la proporción de tiempo que $i$ dedica a $q$, y $m_{jq}$ la fuerza de la relación entre $j$ y $q$.

**Restricción** (*constraint*):

$$C(i) = \sum_{j \in \mathcal{N}(i)} \left( p_{ij} + \sum_{q \in \mathcal{N}(i), q \neq j} p_{iq} p_{qj} \right)^2$$

Un valor bajo de $C(i)$ indica que $i$ ocupa una **posición de broker**: conecta clústeres distintos sin estar él mismo constreñido por ninguno. En bibliometría, una keyword con baja restricción es un nexo interdisciplinario.

---

## 5. Reducción dimensional

Las matrices de co-ocurrencia son de alta dimensión. Las técnicas de **reducción dimensional** proyectan los nodos en espacios de baja dimensión (2D o 3D) para su visualización e interpretación.

### Matriz de distancias

A partir de la matriz de similitud normalizada $S$ (cualquier medida de la sección 2), se construye la matriz de distancias:

$$D(i, j) = 1 - \frac{w(i,j)}{w_{\max}}$$

donde $w_{\max} = \max_{i,j} w(i,j)$. Alternativamente puede usarse $D(i,j) = 1 - S(i,j)$ con $S$ el coseno de Salton.

### 5.1 Escalamiento Multidimensional (MDS)

MDS busca una configuración de puntos $\mathbf{y}_1, \ldots, \mathbf{y}_n \in \mathbb{R}^k$ tal que las distancias euclídeas entre puntos aproximen las distancias originales:

$$\text{Stress} = \sqrt{\frac{\sum_{i<j} (d_{ij} - \hat{d}_{ij})^2}{\sum_{i<j} d_{ij}^2}}$$

donde $\hat{d}_{ij} = \|\mathbf{y}_i - \mathbf{y}_j\|$ es la distancia en el espacio reducido. El **stress** es la métrica de ajuste: valores por debajo de 0.1 son considerados buenos. MDS preserva bien las distancias globales.

### 5.2 t-SNE

t-SNE (van der Maaten & Hinton, 2008) minimiza la divergencia KL entre la distribución de similitudes en el espacio original (Gaussiana) y en el espacio reducido (t de Student):

$$KL(P \| Q) = \sum_{i \neq j} p_{ij} \log \frac{p_{ij}}{q_{ij}}$$

El parámetro de **perplejidad** $(\approx 5\text{–}50)$ controla el número efectivo de vecinos considerados. t-SNE preserva la estructura local (vecindades próximas) a expensas de la global. Los ejes no tienen interpretación directa. **No recomendado para conjuntos pequeños** ($n < 50$) ni para comparar ejecuciones distintas (inicialización aleatoria).

### 5.3 UMAP

UMAP (McInnes et al., 2018) construye una representación topológica del espacio de alta dimensión mediante un complejo simplicial difuso y minimiza la divergencia entre la topología original y la proyectada. Los hiperparámetros principales son:

- `n_neighbors`: tamaño del vecindario local (análogo a perplejidad en t-SNE).
- `min_dist`: distancia mínima entre puntos en el espacio reducido.

UMAP es más rápido que t-SNE, preserva mejor la estructura global y produce resultados más reproducibles. Es el método preferido para corpus de tamaño moderado (~331 documentos).

### 5.4 Análisis de Correspondencias (CA)

El **Análisis de Correspondencias** (Benzécri, 1973) descompone una tabla de contingencia $X$ (por ejemplo, keywords × revistas) mediante la descomposición en valores singulares de la matriz de residuos:

$$\chi_{ij} = \frac{x_{ij} - \hat{x}_{ij}}{\sqrt{\hat{x}_{ij}}}$$

donde $\hat{x}_{ij} = \frac{x_{i\cdot} x_{\cdot j}}{x_{\cdot\cdot}}$ es la frecuencia esperada bajo independencia. Los ejes factoriales maximizan la inercia explicada (análoga a la varianza en PCA).

El **biplot** superpone filas y columnas en el mismo espacio factorial, permitiendo interpretar conjuntamente keywords, revistas y países. La proximidad entre una keyword y una revista indica asociación por encima de lo esperado.

El **Análisis de Correspondencias Múltiples (MCA)** extiende CA a más de dos variables categóricas simultáneamente.

---

## 6. Topic Modeling

Los modelos de tópicos identifican estructuras temáticas latentes en los textos (abstracts, títulos, keywords) sin supervisión.

### 6.1 LDA (Latent Dirichlet Allocation)

Blei et al. (2003) modelan cada documento como una mezcla de $K$ tópicos, y cada tópico como una distribución sobre el vocabulario. Las distribuciones siguen priors de Dirichlet:

$$\theta_d \sim \text{Dir}(\alpha), \quad \phi_k \sim \text{Dir}(\beta)$$

$$z_{dn} \sim \text{Categorical}(\theta_d), \quad w_{dn} \sim \text{Categorical}(\phi_{z_{dn}})$$

LDA asume la **hipótesis de intercambiabilidad** (bag of words): el orden de las palabras no importa. El número de tópicos $K$ debe especificarse a priori y optimizarse mediante perplejidad o coherencia (métrica $C_v$). Para corpora pequeños (~331 documentos), $K \in [5, 20]$ es un rango razonable.

### 6.2 BERTopic

BERTopic (Grootendorst, 2022) combina representaciones contextuales de transformadores con agrupamiento no paramétrico:

1. **Embeddings**: los documentos se representan con un modelo de lenguaje preentrenado (SBERT, multilingual-e5, etc.).
2. **Reducción de dimensionalidad**: UMAP reduce la dimensión de los embeddings.
3. **Clustering**: HDBSCAN agrupa los documentos en el espacio reducido.
4. **Representación de tópicos**: c-TF-IDF identifica las palabras más representativas de cada clúster.

BERTopic no requiere especificar $K$ a priori y es sensible al contexto semántico, lo que lo hace superior a LDA para **corpora pequeños** como el presente (~331 documentos). El hiperparámetro `min_cluster_size` de HDBSCAN controla la granularidad.

---

## 7. Evolución temporal

El análisis diacrónico examina cómo cambia la estructura de la red a lo largo del tiempo.

### 7.1 Ventanas deslizantes

Se divide el corpus en ventanas temporales solapadas o adyacentes. Para cada ventana $[t, t+\Delta t]$ se construye una red de co-ocurrencia independiente $G_t$. Esto permite comparar:

- Evolución de la modularidad $Q_t$ y el número de comunidades.
- Cambios en la centralidad de keywords entre periodos.
- Aparición y desaparición de aristas.

### 7.2 Keywords emergentes

Una keyword $a$ se considera **emergente** si:

$$f_t(a) \approx 0 \text{ para } t < t^*, \quad f_t(a) > 0 \text{ para } t \geq t^*$$

o bien si su frecuencia muestra un crecimiento relativo positivo sostenido:

$$\Delta f(a) = \frac{f_{t_{\text{fin}}}(a) - f_{t_{\text{ini}}}(a)}{f_{t_{\text{ini}}}(a)} \gg 0$$

### 7.3 Keywords en declive

Análogamente, una keyword $a$ está en **declive** si:

$$\Delta f(a) \ll 0 \quad \text{o} \quad f_t(a) = 0 \text{ para } t > t^*$$

El análisis temporal permite identificar **frentes de investigación emergentes** (keywords con crecimiento acelerado en periodos recientes) y áreas maduras o en retroceso, lo que orienta la prospectiva del campo.

---

## 8. Referencias

- Benzécri, J.-P. (1973). *L'Analyse des données. Vol. 2: L'Analyse des correspondances*. Dunod.
- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993–1022.
- Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008. https://doi.org/10.1088/1742-5468/2008/10/P10008
- Burt, R. S. (1992). *Structural Holes: The Social Structure of Competition*. Harvard University Press.
- Callon, M., Courtial, J.-P., & Laville, F. (1991). Co-word analysis as a tool for describing the network of interactions between basic and technological research: The case of polymer chemistry. *Scientometrics*, 22(1), 155–205.
- Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. *arXiv*:2203.05794.
- McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv*:1802.03426.
- Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. *Scientific Reports*, 9, 5233. https://doi.org/10.1038/s41598-019-41695-z
- Van Eck, N. J., & Waltman, L. (2010). Software survey: VOSviewer, a computer program for bibliometric mapping. *Scientometrics*, 84(2), 523–538. https://doi.org/10.1007/s11192-009-0146-3
- Waltman, L., van Eck, N. J., & Noyons, E. C. M. (2010). A unified approach to mapping and clustering of bibliometric networks. *Journal of Informetrics*, 4(4), 629–635. https://doi.org/10.1016/j.joi.2010.07.002
