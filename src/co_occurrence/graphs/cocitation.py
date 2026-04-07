"""Construcción de la red de co-citación."""

from collections import Counter
from itertools import combinations

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS


def build_cocitation_graph(
    df: pd.DataFrame,
    column: str = "Cited References",
    sep: str = ";",
    min_weight: int = DEFAULTS.min_cocitation_weight,
) -> nx.Graph:
    """Construye un grafo de co-citación.

    Dos referencias están conectadas si el mismo artículo las cita.
    El peso es el número de artículos que citan ambas referencias.

    NOTA: Con 331 artículos y ~100 refs/artículo, el grafo puede ser enorme.
    Usar min_weight>=5 para filtrar.

    Args:
        df: DataFrame con los artículos WoS.
        column: Columna de referencias citadas.
        sep: Separador entre referencias.
        min_weight: Umbral mínimo de co-citaciones.

    Returns:
        Grafo no dirigido con 'weight' en aristas.
    """
    edge_counter: Counter[tuple[str, str]] = Counter()
    node_freq: Counter[str] = Counter()

    for _, row in df.iterrows():
        if pd.isna(row.get(column)):
            continue

        refs = [r.strip() for r in str(row[column]).split(sep)]
        refs = [r for r in refs if r]
        refs = list(set(refs))

        for ref in refs:
            node_freq[ref] += 1
        for a, b in combinations(sorted(refs), 2):
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
        "Grafo co-citación: {} nodos, {} aristas (min_weight={})",
        G.number_of_nodes(),
        G.number_of_edges(),
        min_weight,
    )
    return G
