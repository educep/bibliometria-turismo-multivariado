"""Construcción de grafos bipartitos: autor-keyword, revista-keyword, país-keyword."""

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import MULTIVALUE_SEP
from co_occurrence.preprocessing.normalize import normalize_keyword
from co_occurrence.preprocessing.parse import extract_countries_from_addresses


def build_bipartite_graph(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    sep: str = MULTIVALUE_SEP,
    normalize_b: bool = False,
    node_type_a: str = "type_a",
    node_type_b: str = "type_b",
) -> nx.Graph:
    """Construye un grafo bipartito entre dos columnas multi-valor.

    Cada artículo genera aristas entre todos los items de col_a y col_b.
    El peso de la arista es el número de artículos en que co-aparecen.

    Args:
        df: DataFrame WoS.
        col_a: Primera columna multi-valor (ej. 'Author Full Names').
        col_b: Segunda columna multi-valor (ej. 'Author Keywords').
        sep: Separador.
        normalize_b: Si True, normaliza items de col_b como keywords.
        node_type_a: Etiqueta del tipo de nodo A.
        node_type_b: Etiqueta del tipo de nodo B.

    Returns:
        Grafo bipartito con atributo 'bipartite' y 'node_type' en nodos.
    """
    G = nx.Graph()
    edge_weights: dict[tuple[str, str], int] = {}

    for _, row in df.iterrows():
        if pd.isna(row.get(col_a)) or pd.isna(row.get(col_b)):
            continue

        items_a = [a.strip().lower() for a in str(row[col_a]).split(sep) if a.strip()]
        items_b = [b.strip().lower() for b in str(row[col_b]).split(sep) if b.strip()]

        if normalize_b:
            items_b = [normalize_keyword(b) for b in items_b]

        items_a = list(set(items_a))
        items_b = list(set(items_b))

        for a in items_a:
            G.add_node(a, bipartite=0, node_type=node_type_a)
        for b in items_b:
            G.add_node(b, bipartite=1, node_type=node_type_b)

        for a in items_a:
            for b in items_b:
                key = (a, b)
                edge_weights[key] = edge_weights.get(key, 0) + 1

    for (a, b), w in edge_weights.items():
        G.add_edge(a, b, weight=w)

    logger.info(
        "Grafo bipartito {}-{}: {} nodos, {} aristas",
        node_type_a,
        node_type_b,
        G.number_of_nodes(),
        G.number_of_edges(),
    )
    return G


def build_author_keyword_graph(df: pd.DataFrame) -> nx.Graph:
    """Grafo bipartito autor-keyword."""
    return build_bipartite_graph(
        df,
        col_a="Author Full Names",
        col_b="Author Keywords",
        normalize_b=True,
        node_type_a="author",
        node_type_b="keyword",
    )


def build_journal_keyword_graph(df: pd.DataFrame) -> nx.Graph:
    """Grafo bipartito revista-keyword."""
    return build_bipartite_graph(
        df,
        col_a="Source Title",
        col_b="Author Keywords",
        normalize_b=True,
        node_type_a="journal",
        node_type_b="keyword",
    )


def build_country_keyword_graph(df: pd.DataFrame) -> nx.Graph:
    """Grafo bipartito país-keyword.

    Requiere extraer países de la columna Addresses.
    """
    # Crear columna temporal con países
    countries = extract_countries_from_addresses(df["Addresses"])
    df_temp = df.copy()
    # Agrupar países por artículo
    country_by_article = countries.groupby(level=0).apply(lambda s: "; ".join(s.unique()))
    df_temp["_countries"] = country_by_article

    return build_bipartite_graph(
        df_temp,
        col_a="_countries",
        col_b="Author Keywords",
        normalize_b=True,
        node_type_a="country",
        node_type_b="keyword",
    )
