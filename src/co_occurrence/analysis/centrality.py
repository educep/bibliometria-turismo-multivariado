"""Métricas de centralidad cruzada y huecos estructurales (Burt)."""

import networkx as nx
import pandas as pd
from loguru import logger


def compute_centralities(
    G: nx.Graph,
    weight: str = "weight",
    partition: dict[str, int] | None = None,
) -> pd.DataFrame:
    """Calcula múltiples métricas de centralidad para todos los nodos.

    Args:
        G: Grafo no dirigido con pesos.
        weight: Nombre del atributo de peso en aristas.
        partition: Diccionario {nodo: comunidad} (opcional, se añade como columna).

    Returns:
        DataFrame con columnas: keyword, frequency, degree, weighted_degree,
        betweenness, closeness, eigenvector, pagerank, [community].
    """
    logger.info("Calculando centralidades para {} nodos...", G.number_of_nodes())

    bc = nx.betweenness_centrality(G, weight=weight)
    cc = nx.closeness_centrality(G, distance=weight)

    try:
        ec = nx.eigenvector_centrality(G, weight=weight, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        logger.warning("Eigenvector centrality no convergió, aumentando iteraciones")
        ec = nx.eigenvector_centrality(G, weight=weight, max_iter=5000, tol=1e-4)

    pr = nx.pagerank(G, weight=weight)

    records = []
    for node in G.nodes():
        record = {
            "keyword": node,
            "frequency": G.nodes[node].get("frequency", 1),
            "degree": G.degree(node),
            "weighted_degree": G.degree(node, weight=weight),
            "betweenness": bc.get(node, 0),
            "closeness": cc.get(node, 0),
            "eigenvector": ec.get(node, 0),
            "pagerank": pr.get(node, 0),
        }
        if partition is not None:
            record["community"] = partition.get(node, -1)
        records.append(record)

    df = pd.DataFrame(records).sort_values("weighted_degree", ascending=False)
    logger.info(
        "Centralidades calculadas: top 5 por weighted_degree: {}",
        df["keyword"].head(5).tolist(),
    )
    return df


def compute_structural_holes(
    G: nx.Graph,
    weight: str = "weight",
) -> pd.DataFrame:
    """Calcula métricas de huecos estructurales (Burt) para cada nodo.

    - Constraint: valores bajos = nodo ocupa más huecos estructurales.
    - Effective size: contactos no redundantes del nodo.

    Args:
        G: Grafo no dirigido con pesos.
        weight: Atributo de peso.

    Returns:
        DataFrame con columnas: keyword, frequency, constraint, effective_size.
    """
    logger.info("Calculando structural holes para {} nodos...", G.number_of_nodes())

    constraint = nx.constraint(G, weight=weight)
    eff_size = nx.effective_size(G, weight=weight)

    records = []
    for node in G.nodes():
        records.append(
            {
                "keyword": node,
                "frequency": G.nodes[node].get("frequency", 1),
                "constraint": constraint.get(node, float("nan")),
                "effective_size": eff_size.get(node, float("nan")),
            }
        )

    df = pd.DataFrame(records).sort_values("constraint", ascending=True)
    logger.info("Top 5 nodos puente (menor constraint): {}", df["keyword"].head(5).tolist())
    return df
