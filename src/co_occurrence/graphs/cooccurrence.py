"""Construcción de grafos de co-ocurrencia a partir de campos multi-valor."""

from collections import Counter
from itertools import combinations

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS, MULTIVALUE_SEP
from co_occurrence.preprocessing.normalize import normalize_keyword


def build_cooccurrence_graph(
    df: pd.DataFrame,
    column: str = "Author Keywords",
    sep: str = MULTIVALUE_SEP,
    min_weight: int = DEFAULTS.min_cooccurrence_weight,
    min_frequency: int = 1,
    apply_normalization: bool = True,
) -> nx.Graph:
    """Construye un grafo de co-ocurrencia a partir de una columna multi-valor.

    Dos items co-ocurren cuando aparecen en el mismo artículo.
    El peso de la arista es el número de artículos en que co-ocurren.

    Args:
        df: DataFrame con los artículos WoS.
        column: Nombre de la columna multi-valor.
        sep: Separador entre items.
        min_weight: Umbral mínimo de co-ocurrencias para crear arista.
        min_frequency: Frecuencia mínima de un nodo para incluirlo en el grafo.
        apply_normalization: Si True, normaliza keywords con diccionario de sinónimos.

    Returns:
        Grafo no dirigido con atributos 'frequency' en nodos y 'weight' en aristas.
    """
    edge_counter: Counter[tuple[str, str]] = Counter()
    node_freq: Counter[str] = Counter()

    for _, row in df.iterrows():
        if pd.isna(row.get(column)):
            continue

        items = [k.strip().lower() for k in str(row[column]).split(sep)]
        if apply_normalization:
            items = [normalize_keyword(k) for k in items]
        items = list(set(items))  # deduplica dentro del mismo artículo

        for item in items:
            if item:
                node_freq[item] += 1
        for a, b in combinations(sorted(items), 2):
            if a and b:
                edge_counter[(a, b)] += 1

    G = nx.Graph()
    for node, freq in node_freq.items():
        if freq >= min_frequency:
            G.add_node(node, frequency=freq)
    for (a, b), weight in edge_counter.items():
        if weight >= min_weight and a in G and b in G:
            G.add_edge(a, b, weight=weight)

    # Eliminar nodos aislados (sin aristas tras filtro)
    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)

    logger.info(
        "Grafo co-ocurrencia '{}': {} nodos, {} aristas (min_weight={}, min_freq={})",
        column,
        G.number_of_nodes(),
        G.number_of_edges(),
        min_weight,
        min_frequency,
    )
    return G
