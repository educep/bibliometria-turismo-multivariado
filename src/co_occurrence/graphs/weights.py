"""Normalización de pesos de co-ocurrencia: Association Strength, Jaccard, Salton."""

import math

import networkx as nx
from loguru import logger


def association_strength(G: nx.Graph) -> nx.Graph:
    """Añade atributo 'assoc_strength' a cada arista.

    AS(a,b) = w(a,b) / (f(a) * f(b))
    Penaliza co-ocurrencias esperadas por azar. Usado por VOSviewer.

    Args:
        G: Grafo con atributo 'frequency' en nodos y 'weight' en aristas.

    Returns:
        El mismo grafo con atributo 'assoc_strength' añadido a aristas.
    """
    for u, v, data in G.edges(data=True):
        fu = G.nodes[u].get("frequency", 1)
        fv = G.nodes[v].get("frequency", 1)
        data["assoc_strength"] = data["weight"] / (fu * fv)
    logger.info("Association Strength calculada para {} aristas", G.number_of_edges())
    return G


def jaccard_index(G: nx.Graph) -> nx.Graph:
    """Añade atributo 'jaccard' a cada arista.

    J(a,b) = w(a,b) / (f(a) + f(b) - w(a,b))

    Args:
        G: Grafo con 'frequency' en nodos y 'weight' en aristas.

    Returns:
        El mismo grafo con atributo 'jaccard' añadido.
    """
    for u, v, data in G.edges(data=True):
        fu = G.nodes[u].get("frequency", 1)
        fv = G.nodes[v].get("frequency", 1)
        denom = fu + fv - data["weight"]
        data["jaccard"] = data["weight"] / denom if denom > 0 else 0.0
    logger.info("Jaccard Index calculado para {} aristas", G.number_of_edges())
    return G


def salton_cosine(G: nx.Graph) -> nx.Graph:
    """Añade atributo 'salton' (coseno de Salton) a cada arista.

    S(a,b) = w(a,b) / sqrt(f(a) * f(b))

    Args:
        G: Grafo con 'frequency' en nodos y 'weight' en aristas.

    Returns:
        El mismo grafo con atributo 'salton' añadido.
    """
    for u, v, data in G.edges(data=True):
        fu = G.nodes[u].get("frequency", 1)
        fv = G.nodes[v].get("frequency", 1)
        denom = math.sqrt(fu * fv)
        data["salton"] = data["weight"] / denom if denom > 0 else 0.0
    logger.info("Salton Cosine calculado para {} aristas", G.number_of_edges())
    return G


def inclusion_index(G: nx.Graph) -> nx.Graph:
    """Añade atributo 'inclusion' (Inclusion Index) a cada arista.

    I(a,b) = w(a,b) / min(f(a), f(b))

    Args:
        G: Grafo con 'frequency' en nodos y 'weight' en aristas.

    Returns:
        El mismo grafo con atributo 'inclusion' añadido.
    """
    for u, v, data in G.edges(data=True):
        fu = G.nodes[u].get("frequency", 1)
        fv = G.nodes[v].get("frequency", 1)
        denom = min(fu, fv)
        data["inclusion"] = data["weight"] / denom if denom > 0 else 0.0
    logger.info("Inclusion Index calculado para {} aristas", G.number_of_edges())
    return G


def apply_all_normalizations(G: nx.Graph) -> nx.Graph:
    """Aplica todas las normalizaciones de co-ocurrencia al grafo.

    Args:
        G: Grafo con 'frequency' en nodos y 'weight' en aristas.

    Returns:
        Grafo con atributos assoc_strength, jaccard, salton, inclusion en aristas.
    """
    association_strength(G)
    jaccard_index(G)
    salton_cosine(G)
    inclusion_index(G)
    return G
