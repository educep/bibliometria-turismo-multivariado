# Topic Modeling sobre Abstracts — Nice to Do

## Qué es y por qué hacerlo

Hasta ahora, todo el análisis se basa en **keywords**: 3-5 palabras clave que el autor elige para describir su artículo. Son útiles pero tienen dos limitaciones:

1. **Son declarativas, no descriptivas.** El autor elige lo que quiere que veas, no necesariamente lo que hizo. Un artículo que usa cluster analysis para segmentar turistas gastronómicos podría tener solo "tourism" y "segmentation" como keywords — perdemos el método y el contexto.

2. **Son escasas.** 3-5 palabras por artículo dejan mucha información fuera. El abstract tiene ~200 palabras y describe el problema, la metodología, los datos y los resultados.

El topic modeling lee los 331 abstracts completos y descubre **temas latentes** — agrupaciones de palabras que tienden a co-ocurrir en los mismos textos. Cada tema es una distribución de palabras, y cada artículo es una mezcla de temas.

## Qué esperamos encontrar

Los topics deberían superponerse parcialmente con las 8 comunidades de co-ocurrencia, pero no perfectamente. Las discrepancias son los hallazgos:

- **Topic sin comunidad correspondiente** → tema que existe en la práctica pero no se nombra en las keywords. Ejemplo: un cluster de abstracts sobre "revenue / pricing / occupancy / hotel" que no tiene presencia en el grafo de co-ocurrencia porque los autores usan keywords genéricas.

- **Comunidad sin topic correspondiente** → agrupación artificial de keywords que no refleja un tema real. Posible señal de que la normalización de sinónimos fusionó cosas que no debían fusionarse.

- **Artículos con topic dominante diferente a su comunidad** → artículos clasificados en un subcampo por sus keywords pero que en realidad trabajan en otro. Los "impostores" temáticos — interesantes para el análisis.

## Dos técnicas posibles

### Opción A — LDA (Latent Dirichlet Allocation)

**Qué es:** Modelo probabilístico clásico. Asume que cada documento es una mezcla de K temas, y cada tema es una distribución sobre el vocabulario. Es el estándar en bibliometría.

**Ventajas:**
- Rápido, determinístico con seed
- Interpretable: cada tema es una lista ordenada de palabras con probabilidades
- Bien establecido en la literatura (fácil de citar y justificar)
- No necesita GPU

**Desventajas:**
- Bag-of-words: ignora el orden de las palabras y el contexto semántico
- Hay que elegir K (número de temas) a priori — se puede optimizar con coherence score, pero es un paso extra
- Sensible a stopwords y preprocesamiento

**Implementación:**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

abstracts = df["Abstract"].dropna().tolist()

# Vectorización con TF-IDF (mejor que CountVectorizer para corpus pequeños)
vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words="english",
    min_df=3,           # palabra debe aparecer en al menos 3 abstracts
    max_df=0.8,         # ignorar palabras que aparecen en >80% de abstracts
    ngram_range=(1, 2), # unigramas y bigramas
)
X = vectorizer.fit_transform(abstracts)

# LDA con 8-12 temas (empezar con 10, ajustar)
lda = LatentDirichletAllocation(
    n_components=10,
    random_state=42,
    max_iter=50,
    learning_method="batch",
)
lda.fit(X)
```

### Opción B — BERTopic

**Qué es:** Usa embeddings de transformers (sentence-transformers) para representar cada abstract como un vector denso de 384-768 dimensiones, luego aplica UMAP + HDBSCAN para encontrar clusters, y TF-IDF por cluster para extraer las palabras representativas.

**Ventajas:**
- Captura semántica: "tourist satisfaction" y "visitor contentment" caen en el mismo cluster aunque no compartan palabras
- No hay que elegir K — HDBSCAN encuentra el número óptimo automáticamente
- Mejor para corpus pequeños (~300 docs) porque aprovecha el conocimiento pre-entrenado del modelo de lenguaje

**Desventajas:**
- Necesita descargar el modelo de embeddings (~90MB la primera vez)
- Más lento que LDA
- Menos transparente: los clusters emergen de un espacio de 768 dimensiones que no es directamente interpretable
- Más difícil de citar en un paper académico (más reciente, menos establecido)

**Implementación:**

```python
from bertopic import BERTopic

topic_model = BERTopic(
    language="english",
    nr_topics=10,          # sugiere 10 temas, HDBSCAN puede dar más o menos
    min_topic_size=5,      # mínimo 5 docs por topic
    verbose=True,
)
topics, probs = topic_model.fit_transform(abstracts)
```

### Recomendación

**Hacer ambos.** LDA primero (rápido, establecido, citable), BERTopic después para comparar. Si los resultados convergen, la conclusión es robusta. Si divergen, eso es material de discusión.

---

## Integración con el análisis existente

### Paso 1 — Asignar topic dominante a cada artículo

```python
# LDA: topic con mayor probabilidad
df["topic_lda"] = lda.transform(X).argmax(axis=1)

# BERTopic: asignación directa
df["topic_bertopic"] = topics
```

### Paso 2 — Tabla cruzada topic × comunidad

Cada artículo ya tiene una comunidad (vía sus keywords) y ahora un topic (vía su abstract). La tabla cruzada muestra la correspondencia:

```python
# Asignar comunidad al artículo = comunidad de su keyword más frecuente
# (un artículo puede tener keywords en varias comunidades)
crosstab = pd.crosstab(df["topic_lda"], df["community_dominant"])
```

Si topic 3 = "hotel efficiency performance DEA" y comunidad 4 = "multivariate analysis / cluster analysis", y la tabla muestra que los artículos del topic 3 están repartidos entre comunidad 2 y 4, eso significa que el tema DEA/eficiencia se fragmenta en el grafo de co-ocurrencia. Hallazgo.

### Paso 3 — Grafo bipartito keyword × topic

Crear un grafo donde los nodos son keywords Y topics, y las aristas conectan cada keyword con los topics donde aparece (ponderado por frecuencia).

```python
G_bipartite = nx.Graph()
for topic_id in range(n_topics):
    topic_articles = df[df["topic_lda"] == topic_id]
    for _, row in topic_articles.iterrows():
        if pd.notna(row["Author Keywords"]):
            for kw in row["Author Keywords"].split(";"):
                kw = normalize_keyword(kw.strip().lower())
                if kw and kw in G_keywords.nodes():
                    edge = (kw, f"topic_{topic_id}")
                    if G_bipartite.has_edge(*edge):
                        G_bipartite[edge[0]][edge[1]]["weight"] += 1
                    else:
                        G_bipartite.add_edge(kw, f"topic_{topic_id}", weight=1)
```

Esto permite visualizar en un mismo grafo la relación entre los dos sistemas de clasificación: el declarado (keywords → comunidades) y el latente (abstracts → topics).

### Paso 4 — Evolución temporal de topics

Misma lógica que keyword_evolution pero para topics: ¿qué temas crecen, cuáles declinan?

```python
topic_by_year = df.groupby(["Publication Year", "topic_lda"]).size().unstack(fill_value=0)
```

Esto produce un gráfico de áreas apiladas: evolución del peso relativo de cada tema a lo largo del tiempo.

---

## Preprocesamiento de abstracts

Los abstracts tienen ruido específico que hay que limpiar:

1. **Frases boilerplate:** "This paper examines...", "The results show that...", "© 2022 Elsevier Ltd." — no aportan contenido temático
2. **Caracteres corruptos:** el dataset tiene `?Modelling?` con signos de interrogación — artefactos de encoding
3. **Stopwords del dominio:** "tourism", "study", "analysis", "results", "paper" aparecen en TODOS los abstracts — no discriminan temas
4. **Stemming vs lemmatization:** "satisfaction" y "satisfying" deberían colapsar. Usar spaCy lemmatizer en lugar de stemming bruto (Porter/Snowball)

```python
import spacy
nlp = spacy.load("en_core_web_sm")

DOMAIN_STOPWORDS = {
    "tourism", "tourist", "study", "paper", "research", "results",
    "analysis", "data", "method", "approach", "finding", "show",
    "suggest", "examine", "investigate", "propose", "aim",
}

def clean_abstract(text: str) -> str:
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if token.is_alpha
        and not token.is_stop
        and token.lemma_ not in DOMAIN_STOPWORDS
        and len(token.lemma_) > 2
    ]
    return " ".join(tokens)
```

## Outputs esperados

| Archivo | Contenido |
|---------|-----------|
| `topics_lda.csv` | artículo_id, topic dominante, probabilidades por topic |
| `topics_bertopic.csv` | artículo_id, topic, probabilidad |
| `topic_words.csv` | topic_id, top-20 palabras con pesos |
| `topic_community_crosstab.csv` | tabla cruzada topic × comunidad |
| `topic_evolution.csv` | topic × año × conteo |
| `topic_bipartite.gexf` | grafo keyword × topic para Gephi/plotly |
| `topics_lda_viz.html` | pyLDAvis interactivo (LDA) |
| `topic_evolution.html` | plotly stacked area chart |

## Estructura del módulo

```
src/co_occurrence/
└── topics.py
    ├── clean_abstracts(df) → Series limpia
    ├── fit_lda(abstracts, n_topics=10) → modelo, matriz doc-topic, palabras-topic
    ├── fit_bertopic(abstracts, n_topics=10) → modelo, topics, probs
    ├── topic_community_crosstab(df) → DataFrame
    ├── topic_evolution(df) → DataFrame
    └── build_topic_keyword_graph(df, G_keywords) → nx.Graph bipartito
```

## Dependencias adicionales

```bash
# LDA (ya incluida vía scikit-learn en [dimred])
# Solo falta spaCy para preprocesamiento
pip install spacy
python -m spacy download en_core_web_sm

# BERTopic (en [topics] del pyproject.toml)
pip install bertopic
```

## Criterio de éxito

- 8-12 topics interpretables (ni 3 genéricos ni 25 fragmentados)
- Al menos 70% de coincidencia entre topics y comunidades de co-ocurrencia (la estructura debe ser consistente)
- El 30% de discrepancia debe ser explicable (artículos con keywords genéricas pero abstracts específicos)
- Cada topic debe poder nombrarse con 3-4 palabras que un investigador de turismo reconocería

## Estimación de esfuerzo

- LDA: 2-3 horas (preprocesamiento + tuning de K + visualización)
- BERTopic: 1-2 horas adicionales (modelo pre-entrenado hace el trabajo pesado)
- Integración con pipeline existente: 1-2 horas (crosstab, bipartito, evolución)
- **Total: ~5-7 horas**
