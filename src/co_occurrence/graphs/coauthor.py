"""Construcción de la red de co-autoría."""

from collections import Counter
from itertools import combinations

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import MULTIVALUE_SEP


def build_coauthor_graph(
    df: pd.DataFrame,
    column: str = "Author Full Names",
    sep: str = MULTIVALUE_SEP,
    min_weight: int = 1,
) -> nx.Graph:
    """Construye un grafo de co-autoría.

    Dos autores están conectados si firman el mismo artículo.
    El peso de la arista es el número de artículos co-firmados.

    Args:
        df: DataFrame con los artículos WoS.
        column: Columna de autores.
        sep: Separador entre autores.
        min_weight: Umbral mínimo de co-autorías para crear arista.

    Returns:
        Grafo no dirigido con 'frequency' (n artículos) en nodos y 'weight' en aristas.
    """
    edge_counter: Counter[tuple[str, str]] = Counter()
    node_freq: Counter[str] = Counter()

    for _, row in df.iterrows():
        if pd.isna(row.get(column)):
            continue

        authors = [a.strip().lower() for a in str(row[column]).split(sep)]
        authors = [a for a in authors if a]
        authors = list(set(authors))

        for author in authors:
            node_freq[author] += 1
        for a, b in combinations(sorted(authors), 2):
            edge_counter[(a, b)] += 1

    G = nx.Graph()
    for node, freq in node_freq.items():
        G.add_node(node, frequency=freq)
    for (a, b), weight in edge_counter.items():
        if weight >= min_weight:
            G.add_edge(a, b, weight=weight)

    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)

    logger.info(
        "Grafo co-autoría: {} nodos, {} aristas (min_weight={})",
        G.number_of_nodes(),
        G.number_of_edges(),
        min_weight,
    )
    return G
