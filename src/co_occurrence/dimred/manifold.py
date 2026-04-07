"""Reducción dimensional de la matriz de co-ocurrencia: MDS, t-SNE, UMAP."""

import networkx as nx
import numpy as np
import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS


def cooccurrence_to_distance_matrix(G: nx.Graph) -> tuple[np.ndarray, list[str]]:
    """Convierte un grafo de co-ocurrencia en una matriz de distancias.

    Distancia = 1 - (w / w_max) para pares con co-ocurrencia,
    distancia = 1.0 para pares sin co-ocurrencia.

    Args:
        G: Grafo de co-ocurrencia con 'weight' en aristas.

    Returns:
        Tupla (matriz_distancias, lista_nodos).
    """
    nodes = list(G.nodes())
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    W = np.zeros((n, n))
    for u, v, data in G.edges(data=True):
        i, j = node_idx[u], node_idx[v]
        W[i, j] = data["weight"]
        W[j, i] = data["weight"]

    w_max = W.max() if W.max() > 0 else 1.0
    D = np.where(W > 0, 1 - W / w_max, 1.0)
    np.fill_diagonal(D, 0)

    return D, nodes


def reduce_mds(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
) -> pd.DataFrame:
    """Reducción dimensional con MDS (Multidimensional Scaling).

    Preserva distancias globales. Clásico en bibliometría.

    Args:
        G: Grafo de co-ocurrencia.
        n_components: Dimensiones de salida.
        random_state: Semilla.

    Returns:
        DataFrame con columnas: keyword, x, y, frequency.
    """
    from sklearn.manifold import MDS

    D, nodes = cooccurrence_to_distance_matrix(G)

    logger.info("MDS: reduciendo {} nodos a {}D...", len(nodes), n_components)
    mds = MDS(
        n_components=n_components,
        metric="precomputed",
        init="random",
        n_init=4,
        random_state=random_state,
    )
    coords = mds.fit_transform(D)

    df = pd.DataFrame(
        {
            "keyword": nodes,
            "x": coords[:, 0],
            "y": coords[:, 1],
            "frequency": [G.nodes[n].get("frequency", 1) for n in nodes],
        }
    )
    logger.info("MDS completado (stress={})", round(mds.stress_, 4))
    return df


def reduce_tsne(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
    perplexity: float = 30.0,
) -> pd.DataFrame:
    """Reducción dimensional con t-SNE.

    Bueno para revelar clusters locales. No preserva distancias globales.

    Args:
        G: Grafo de co-ocurrencia.
        n_components: Dimensiones de salida.
        random_state: Semilla.
        perplexity: Perplexity (ajustar si pocos nodos).

    Returns:
        DataFrame con columnas: keyword, x, y, frequency.
    """
    from sklearn.manifold import TSNE

    D, nodes = cooccurrence_to_distance_matrix(G)

    # Ajustar perplexity si hay pocos nodos
    effective_perplexity = min(perplexity, max(5.0, len(nodes) / 4))

    logger.info("t-SNE: reduciendo {} nodos (perplexity={})...", len(nodes), effective_perplexity)
    tsne = TSNE(
        n_components=n_components,
        metric="precomputed",
        init="random",
        random_state=random_state,
        perplexity=effective_perplexity,
    )
    coords = tsne.fit_transform(D)

    return pd.DataFrame(
        {
            "keyword": nodes,
            "x": coords[:, 0],
            "y": coords[:, 1],
            "frequency": [G.nodes[n].get("frequency", 1) for n in nodes],
        }
    )


def reduce_umap(
    G: nx.Graph,
    n_components: int = DEFAULTS.dimred_n_components,
    random_state: int = DEFAULTS.dimred_random_state,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> pd.DataFrame:
    """Reducción dimensional con UMAP.

    Preserva estructura local y global. Recomendado para este proyecto.

    Args:
        G: Grafo de co-ocurrencia.
        n_components: Dimensiones de salida.
        random_state: Semilla.
        n_neighbors: Vecinos para construir el grafo local.
        min_dist: Distancia mínima entre puntos en el embedding.

    Returns:
        DataFrame con columnas: keyword, x, y, frequency.
    """
    import umap

    D, nodes = cooccurrence_to_distance_matrix(G)

    effective_neighbors = min(n_neighbors, len(nodes) - 1)

    logger.info("UMAP: reduciendo {} nodos (n_neighbors={})...", len(nodes), effective_neighbors)
    reducer = umap.UMAP(
        metric="precomputed",
        n_components=n_components,
        random_state=random_state,
        n_neighbors=effective_neighbors,
        min_dist=min_dist,
    )
    coords = reducer.fit_transform(D)

    return pd.DataFrame(
        {
            "keyword": nodes,
            "x": coords[:, 0],
            "y": coords[:, 1],
            "frequency": [G.nodes[n].get("frequency", 1) for n in nodes],
        }
    )
