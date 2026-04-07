"""Generador de vault Obsidian desde la red de co-ocurrencia.

Cada keyword = una nota .md con wikilinks a co-ocurrentes.
El graph view de Obsidian renderiza automáticamente la red.

Estructura generada:
    vault_bibliometria/
    ├── _INDEX.md
    ├── keywords/
    ├── authors/
    ├── journals/
    └── communities/
"""

import re
from pathlib import Path

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import MULTIVALUE_SEP, VAULT_DIR


def _sanitize_filename(name: str) -> str:
    """Limpia nombre para usar como archivo .md."""
    return re.sub(r'[/\\:?*"<>|]', "-", name).strip().rstrip(".")


def _write_note(vault_path: Path, folder: str, title: str, content: str) -> None:
    """Escribe una nota .md en el vault."""
    path = vault_path / folder
    path.mkdir(parents=True, exist_ok=True)
    filepath = path / f"{_sanitize_filename(title)}.md"
    filepath.write_text(content, encoding="utf-8")


def generate_keyword_notes(
    G: nx.Graph,
    partition: dict[str, int],
    centralities: pd.DataFrame,
    community_names: dict[int, str],
    vault_path: Path = VAULT_DIR,
) -> None:
    """Genera una nota por keyword con métricas y wikilinks a co-ocurrentes."""
    for node in G.nodes():
        freq = G.nodes[node].get("frequency", 1)
        comm = partition.get(node, -1)
        comm_name = community_names.get(comm, f"Comunidad {comm}")

        row = centralities[centralities["keyword"] == node]
        degree = int(row["degree"].values[0]) if len(row) > 0 else 0
        betweenness = float(row["betweenness"].values[0]) if len(row) > 0 else 0.0

        neighbors = sorted(
            G[node].items(),
            key=lambda x: x[1].get("weight", 1),
            reverse=True,
        )

        content = f"""---
type: keyword
frequency: {freq}
degree: {degree}
betweenness: {betweenness:.4f}
community: {comm}
community_name: "{comm_name}"
tags:
  - keyword
  - comunidad-{comm}
---

# {node}

> Frecuencia: **{freq}** | Grado: **{degree}** | Betweenness: **{betweenness:.4f}**
> Comunidad: [[{comm_name}]]

## Co-ocurre con

"""
        for neighbor, data in neighbors:
            weight = data.get("weight", 1)
            content += f"- [[{neighbor}]] ({weight}x)\n"

        content += f"\n## Comunidad\n\nPertenece a [[{comm_name}]]\n"
        _write_note(vault_path, "keywords", node, content)

    logger.info("Generadas {} notas de keywords", G.number_of_nodes())


def generate_author_notes(
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
    """Genera una nota por autor con links a coautores, keywords y revistas."""
    author_data: dict[str, dict] = {}

    for _, row in df.iterrows():
        if pd.isna(row.get("Authors")):
            continue
        authors = [a.strip() for a in str(row["Authors"]).split(MULTIVALUE_SEP)]
        keywords: list[str] = []
        if pd.notna(row.get("Author Keywords")):
            keywords = [
                k.strip().lower() for k in str(row["Author Keywords"]).split(MULTIVALUE_SEP)
            ]
        journal = str(row.get("Source Title", ""))
        year = row.get("Publication Year", "")
        title = str(row.get("Article Title", ""))

        for author in authors:
            if not author:
                continue
            if author not in author_data:
                author_data[author] = {
                    "coauthors": set(),
                    "keywords": set(),
                    "articles": [],
                    "journals": set(),
                }
            author_data[author]["coauthors"].update(a for a in authors if a != author and a)
            author_data[author]["keywords"].update(k for k in keywords if k)
            if journal:
                author_data[author]["journals"].add(journal)
            author_data[author]["articles"].append(f"{title} ({year})")

    for author, data in author_data.items():
        content = f"""---
type: author
n_articles: {len(data['articles'])}
n_coauthors: {len(data['coauthors'])}
tags:
  - author
---

# {author}

## Coautores

"""
        for coauthor in sorted(data["coauthors"]):
            content += f"- [[{coauthor}]]\n"

        content += "\n## Keywords\n\n"
        for kw in sorted(data["keywords"]):
            content += f"- [[{kw}]]\n"

        content += "\n## Publica en\n\n"
        for j in sorted(data["journals"]):
            if j:
                content += f"- [[{j}]]\n"

        content += "\n## Articulos\n\n"
        for art in data["articles"]:
            content += f"- {art}\n"

        _write_note(vault_path, "authors", author, content)

    logger.info("Generadas {} notas de autores", len(author_data))


def generate_journal_notes(
    df: pd.DataFrame,
    vault_path: Path = VAULT_DIR,
) -> None:
    """Genera una nota por revista con links a keywords y autores."""
    journal_data: dict[str, dict] = {}

    for _, row in df.iterrows():
        journal = str(row.get("Source Title", ""))
        if not journal or pd.isna(row.get("Source Title")):
            continue
        if journal not in journal_data:
            journal_data[journal] = {"authors": set(), "keywords": set(), "count": 0}
        journal_data[journal]["count"] += 1
        if pd.notna(row.get("Authors")):
            journal_data[journal]["authors"].update(
                a.strip() for a in str(row["Authors"]).split(MULTIVALUE_SEP)
            )
        if pd.notna(row.get("Author Keywords")):
            journal_data[journal]["keywords"].update(
                k.strip().lower() for k in str(row["Author Keywords"]).split(MULTIVALUE_SEP)
            )

    for journal, data in journal_data.items():
        content = f"""---
type: journal
n_articles: {data['count']}
tags:
  - journal
---

# {journal}

> **{data['count']}** articulos en el corpus

## Keywords asociadas

"""
        for kw in sorted(data["keywords"]):
            if kw:
                content += f"- [[{kw}]]\n"

        content += "\n## Autores\n\n"
        for a in sorted(data["authors"]):
            if a:
                content += f"- [[{a}]]\n"

        _write_note(vault_path, "journals", journal, content)

    logger.info("Generadas {} notas de revistas", len(journal_data))


def generate_community_notes(
    G: nx.Graph,
    partition: dict[str, int],
    community_names: dict[int, str],
    vault_path: Path = VAULT_DIR,
) -> None:
    """Genera una nota por comunidad con sus keywords miembros."""
    from collections import defaultdict

    communities: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for node, comm in partition.items():
        communities[comm].append((node, G.nodes[node].get("frequency", 1)))

    for comm_id, members in communities.items():
        members_sorted = sorted(members, key=lambda x: x[1], reverse=True)
        top5 = " / ".join([m[0] for m in members_sorted[:5]])
        comm_name = community_names.get(comm_id, f"Comunidad {comm_id}")

        content = f"""---
type: community
id: {comm_id}
name: "{comm_name}"
n_keywords: {len(members)}
label: "{top5}"
tags:
  - community
---

# {comm_name}

> {len(members)} keywords | Top: {top5}

## Miembros (por frecuencia)

"""
        for kw, freq in members_sorted:
            content += f"- [[{kw}]] ({freq}x)\n"

        _write_note(vault_path, "communities", comm_name, content)

    logger.info("Generadas {} notas de comunidades", len(communities))


def generate_index(
    G: nx.Graph,
    partition: dict[str, int],
    df: pd.DataFrame,
    community_names: dict[int, str],
    vault_path: Path = VAULT_DIR,
) -> None:
    """Dashboard principal del vault con queries Dataview."""
    n_communities = len(set(partition.values()))

    content = f"""---
type: index
tags:
  - dashboard
---

# Analisis Bibliometrico -- Turismo y Tecnicas Multivariadas

> Corpus: **{len(df)}** articulos | Keywords: **{G.number_of_nodes()}** | Co-ocurrencias: **{G.number_of_edges()}** | Comunidades: **{n_communities}**

## Navegacion

- `keywords/` -- keywords y sus co-ocurrencias
- `authors/` -- autores y sus colaboraciones
- `journals/` -- revistas y su perfil tematico
- `communities/` -- clusters tematicos detectados

## Uso del graph view

1. Abrir Graph View (Ctrl+G)
2. Filtrar por `tag:#keyword` para ver solo la red de co-ocurrencia
3. Filtrar por `tag:#author` para ver solo la red de co-autoria
4. Filtrar por `tag:#comunidad-N` para aislar una comunidad
5. Colorear por tags para distinguir tipos de nodo

## Queries Dataview

### Top 10 keywords por frecuencia

```dataview
TABLE frequency, degree, betweenness, community
FROM "keywords"
SORT frequency DESC
LIMIT 10
```

### Keywords puente (alto betweenness, bajo degree)

```dataview
TABLE frequency, degree, betweenness
FROM "keywords"
WHERE betweenness > 0.05 AND degree < 20
SORT betweenness DESC
```
"""
    _write_note(vault_path, "", "_INDEX", content)
    logger.info("INDEX generado en {}", vault_path)


def generate_vault(
    G: nx.Graph,
    partition: dict[str, int],
    centralities: pd.DataFrame,
    df: pd.DataFrame,
    community_names: dict[int, str] | None = None,
    vault_path: Path = VAULT_DIR,
) -> Path:
    """Genera el vault Obsidian completo.

    Args:
        G: Grafo de co-ocurrencia de keywords.
        partition: Diccionario {keyword: comunidad}.
        centralities: DataFrame de compute_centralities().
        df: DataFrame WoS original.
        community_names: Diccionario {id_comunidad: nombre_semántico}.
        vault_path: Directorio raiz del vault.

    Returns:
        Ruta del vault generado.
    """
    logger.info("Generando vault Obsidian en {}", vault_path)
    vault_path.mkdir(parents=True, exist_ok=True)

    if community_names is None:
        community_names = {i: f"Comunidad {i}" for i in set(partition.values())}

    generate_keyword_notes(G, partition, centralities, community_names, vault_path)
    generate_author_notes(df, vault_path)
    generate_journal_notes(df, vault_path)
    generate_community_notes(G, partition, community_names, vault_path)
    generate_index(G, partition, df, community_names, vault_path)

    logger.info("Vault completo generado en {}", vault_path)
    return vault_path
