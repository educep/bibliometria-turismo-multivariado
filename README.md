# Co-occurrence Library

**Análisis bibliométrico de técnicas multivariadas en las publicaciones en turismo y su integración en una serie de grafos**

## El problema

La investigación en turismo utiliza cada vez más técnicas multivariadas (SEM, análisis factorial, DEA, clustering, etc.), pero no existe un mapa claro de cómo estas técnicas se relacionan entre sí, qué subcampos temáticos forman, ni cómo ha evolucionado su adopción en el tiempo.

Las herramientas clásicas de bibliometría (VOSviewer, Bibliometrix) producen grafos de co-ocurrencia descriptivos, pero se quedan cortas en tres aspectos:

1. **No son propiamente multivariadas.** Un layout Fruchterman-Reingold muestra topología, no distancias semánticas reales.
2. **No revelan estructura latente.** No aplican reducción dimensional sobre la matriz de co-ocurrencia.
3. **Son estáticas.** No permiten exploración interactiva ni evolución temporal animada.

## Los datos

331 artículos exportados de Web of Science (WoS), marzo 2025. Cada registro contiene autores, keywords, abstracts, referencias citadas, revistas, categorías temáticas, afiliaciones, y métricas de impacto.

Glosario completo de columnas: [`glosario_columnas_wos.txt`](data/glosario_columnas_wos.txt)

## La solución

Tres capas analíticas que van más allá de la bibliometría descriptiva:

### Capa 1 — Reducción dimensional de la matriz de co-ocurrencia

Proyectar la matriz de co-ocurrencia de keywords en 2D usando técnicas genuinamente multivariadas: MDS, t-SNE, UMAP, y Análisis de Correspondencias (CA/MCA). El CA permite superponer keywords, revistas y países en el mismo espacio factorial (biplot).

### Capa 2 — Detección de comunidades

Particionar los grafos en subcampos temáticos con Louvain/Leiden. Combinar con análisis de centralidad cruzada (degree vs. betweenness) para identificar keywords pilares y keywords puente.

### Capa 3 — Evolución temporal

Grafos de co-ocurrencia por ventana temporal para mostrar emergencia, consolidación y declive de temas. Detección de keywords emergentes y en declive.

### Valor diferencial adicional

- Topic modeling (LDA/BERTopic) sobre abstracts para contrastar temas latentes vs. keywords declaradas
- Normalización Association Strength / Jaccard para revelar asociaciones no triviales
- Structural holes (Burt) para identificar oportunidades interdisciplinarias
- Grafos multicapa (co-ocurrencia + co-citación + co-autoría)

## Publicación

Sitio web interactivo generado con [Quarto](https://quarto.org/) y desplegado en AWS S3 + CloudFront con HTTPS.

**Sitio web:** [bibliometria-turismo-multivariado.cepeda.fr](https://bibliometria-turismo-multivariado.cepeda.fr)

**Vault Obsidian:** [`vault_bibliometria/`](https://github.com/educep/bibliometria-turismo-multivariado/tree/main/vault_bibliometria) — clonar el repo y abrir la carpeta como vault en Obsidian.

Gráficos interactivos con Plotly (hover, zoom, filtros). Plan detallado: [`plan_publicacion_quarto_s3.md`](docs/preliminar/plan_publicacion_quarto_s3.md)

## Instalación

```bash
# Clonar y crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar con todas las dependencias
pip install -e ".[all]"

# O por grupos según necesidad
pip install -e ".[viz,communities]"    # grafos + visualización
pip install -e ".[dimred]"             # reducción dimensional
pip install -e ".[topics]"             # topic modeling (BERTopic)
pip install -e ".[publish]"            # tablas interactivas para Quarto

# Desarrollo (incluye linters)
pip install -e ".[dev]"
```

## Estructura del proyecto

```
GRAFOS/
├── README.md
├── pyproject.toml
├── requirements.txt
├── Makefile                              ← venv, install, format, lint, test
├── data/
│   └── glosario_columnas_wos.txt         ← descripción de 70 columnas WoS
├── src/co_occurrence/                    ← paquete Python
│   ├── config.py                         ← rutas y parámetros (Pydantic)
│   ├── synonyms.py                       ← ~160 sinónimos + stoplist (~90 términos)
│   ├── cli.py                            ← 10 comandos CLI (Typer)
│   ├── io/loader.py                      ← lectura Excel WoS
│   ├── preprocessing/                    ← parseo, normalización, stoplist
│   ├── graphs/                           ← co-ocurrencia, co-autoría, bipartitos, pesos
│   ├── analysis/                         ← comunidades, centralidades, temporal
│   ├── dimred/                           ← MDS, t-SNE, UMAP, CA/MCA
│   ├── topics/                           ← LDA, BERTopic
│   ├── viz/                              ← Plotly, PyVis, export GEXF/CSV
│   └── obsidian.py                       ← generador de vault Obsidian
├── docs/                                 ← documentación técnica
│   ├── index.md                          ← índice general
│   ├── api.md                            ← referencia de funciones públicas
│   ├── architecture.md                   ← módulos, flujo de datos
│   ├── cli.md                            ← comandos CLI
│   ├── configuration.md                  ← parámetros y sinónimos
│   ├── installation.md                   ← prerrequisitos, dependencias
│   ├── methodology.md                    ← fundamentos matemáticos
│   └── results.md                        ← resultados del pipeline
├── quarto/                               ← páginas Quarto del sitio web
│   ├── _quarto.yml                       ← configuración del sitio
│   ├── index.qmd                         ← página principal
│   ├── 01_datos.qmd                      ← descripción del corpus
│   ├── 02_coocurrencia.qmd               ← grafo de co-ocurrencia interactivo
│   ├── 03_comunidades.qmd                ← comunidades Louvain
│   ├── 04_centralidades.qmd              ← centralidades y structural holes
│   ├── 05_reduccion_dim.qmd              ← MDS, t-SNE, UMAP, CA (tabset)
│   ├── 06_evolucion.qmd                  ← evolución temporal
│   ├── about.qmd                         ← sobre el proyecto
│   ├── coocurrence_pyvis.html            ← grafo interactivo PyVis
│   └── styles.css                        ← estilos del sitio
└── vault_bibliometria/                   ← vault Obsidian generado
    ├── _INDEX.md                         ← índice con queries Dataview
    ├── keywords/                         ← notas por keyword
    ├── authors/                          ← notas por autor
    ├── journals/                         ← notas por revista
    └── communities/                      ← notas por comunidad
```

## Estado actual

- [x] Datos fuente (331 artículos WoS)
- [x] Glosario de columnas
- [x] Pipeline analítico documentado
- [x] Plan de publicación Quarto + S3
- [x] Generador de vault Obsidian
- [x] Configuración de proyecto (`pyproject.toml`)
- [x] Implementación del pipeline en `src/`
- [x] Normalización de keywords (diccionario de sinónimos + stoplist)
- [x] Construcción de grafos (co-ocurrencia, co-autoría, bipartitos, pesos normalizados)
- [x] Detección de comunidades (Louvain / Leiden + etiquetado semántico)
- [x] Centralidades (degree, betweenness, eigenvector, PageRank, structural holes)
- [x] Evolución temporal (ventanas deslizantes, keywords emergentes/en declive)
- [x] CLI pipeline (`python -m co_occurrence pipeline`)
- [x] Reducción dimensional manifold (MDS, t-SNE, UMAP) + scatter interactivo por comunidad
- [x] Reducción dimensional CA/MCA (biplot keyword x revista)
- [x] Visualizaciones interactivas adicionales (PyVis, grafos Plotly)
- [x] Páginas Quarto (.qmd)
- [x] Deploy S3 + CloudFront (HTTPS en bibliometria-turismo-multivariado.cepeda.fr)
- [ ] Topic modeling (LDA / BERTopic)

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [`docs/index.md`](docs/index.md) | Índice de toda la documentación |
| [`docs/installation.md`](docs/installation.md) | Prerrequisitos, venv, dependencias opcionales |
| [`docs/architecture.md`](docs/architecture.md) | Módulos, flujo de datos, convenciones |
| [`docs/cli.md`](docs/cli.md) | 10 comandos CLI con parámetros y ejemplos |
| [`docs/api.md`](docs/api.md) | Referencia completa de las 36 funciones públicas |
| [`docs/methodology.md`](docs/methodology.md) | Fundamentos matemáticos (co-ocurrencia, normalización, comunidades, centralidades, dimred) |
| [`docs/configuration.md`](docs/configuration.md) | GraphDefaults, rutas, sinónimos, stoplist |
| [`docs/results.md`](docs/results.md) | Resultados del pipeline: 124 nodos, 8 comunidades, centralidades |
| [`docs/BITACORA.md`](docs/BITACORA.md) | Cuaderno de laboratorio: hallazgos, decisiones de diseño, lecciones |

### Documentos de diseño originales

| Documento | Contenido |
|-----------|-----------|
| [`docs/preliminar/instrucciones_analisis_grafos.md`](docs/preliminar/instrucciones_analisis_grafos.md) | Pipeline analítico completo con código |
| [`docs/preliminar/plan_publicacion_quarto_s3.md`](docs/preliminar/plan_publicacion_quarto_s3.md) | Arquitectura Quarto, visualización, deploy S3/CloudFront |
| [`docs/preliminar/generador_vault_obsidian.md`](docs/preliminar/generador_vault_obsidian.md) | Generador de vault Obsidian |
| [`data/glosario_columnas_wos.txt`](data/glosario_columnas_wos.txt) | Descripción de las 70 columnas del export WoS |

## Autor

**Eduardo Cepeda, Ph.D.** — [Sitio Web](https://cepeda.fr)

---

*Generado con [Quarto](https://quarto.org), Python y herramientas de código abierto. El desarrollo fue asistido por inteligencia artificial ([Claude Code](https://claude.ai/claude-code)), en línea con los principios de transparencia y uso responsable de IA en la investigación.*
