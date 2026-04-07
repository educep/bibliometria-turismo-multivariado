"""Detección de comunidades: Louvain, Leiden, y etiquetado semántico."""

from collections import defaultdict

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS


def detect_louvain(
    G: nx.Graph,
    resolution: float = DEFAULTS.louvain_resolution,
    weight: str = "weight",
    seed: int = DEFAULTS.community_seed,
) -> dict[str, int]:
    """Detecta comunidades con el algoritmo de Louvain.

    Args:
        G: Grafo no dirigido.
        resolution: Resolución del algoritmo (mayor = más comunidades).
        weight: Atributo de peso.
        seed: Semilla para reproducibilidad.

    Returns:
        Diccionario {nodo: id_comunidad}.
    """
    from community import community_louvain  # dep opcional: python-louvain

    partition = community_louvain.best_partition(
        G, weight=weight, resolution=resolution, random_state=seed
    )
    nx.set_node_attributes(G, partition, "community")

    n_communities = len(set(partition.values()))
    logger.info("Louvain: {} comunidades detectadas (resolution={})", n_communities, resolution)
    return partition


def detect_leiden(
    G: nx.Graph,
    weight: str = "weight",
    seed: int = DEFAULTS.community_seed,
) -> dict[str, int]:
    """Detecta comunidades con el algoritmo de Leiden (más robusto que Louvain).

    Args:
        G: Grafo no dirigido.
        weight: Atributo de peso.
        seed: Semilla para reproducibilidad.

    Returns:
        Diccionario {nodo: id_comunidad}.
    """
    import igraph as ig  # dep opcional
    import leidenalg  # dep opcional

    G_ig = ig.Graph.from_networkx(G)
    partition_obj = leidenalg.find_partition(
        G_ig,
        leidenalg.ModularityVertexPartition,
        weights=weight,
        seed=seed,
    )

    node_names = [G_ig.vs[i]["_nx_name"] for i in range(G_ig.vcount())]
    partition = {name: partition_obj.membership[i] for i, name in enumerate(node_names)}
    nx.set_node_attributes(G, partition, "community")

    n_communities = len(set(partition.values()))
    logger.info("Leiden: {} comunidades detectadas", n_communities)
    return partition


# ---------------------------------------------------------------------------
# Nombres semánticos para comunidades
# ---------------------------------------------------------------------------
# Reglas de naming: si una comunidad contiene keywords de un perfil temático
# reconocible, recibe un nombre interpretativo. Se evalúan en orden de
# especificidad (más específico primero). Cada regla es (nombre, keywords_requeridas)
# donde basta que AL MENOS 2 de las keywords aparezcan en la comunidad.
# ---------------------------------------------------------------------------
COMMUNITY_NAMING_RULES: list[tuple[str, list[str]]] = [
    (
        "Time Series & Forecasting",
        [
            "tourism demand forecasting",
            "singular spectrum analysis",
            "tourist arrivals",
            "multivariate time series",
            "leading indicators",
            "support vector machine",
            "segmentation",
        ],
    ),
    (
        "Macroeconomics & Causality",
        [
            "economic growth",
            "granger causality",
            "panel data",
            "vector autoregression",
            "carbon emissions",
            "energy consumption",
            "cointegration",
        ],
    ),
    (
        "Multivariate Analysis & Clustering",
        [
            "multivariate analysis",
            "cluster analysis",
            "competitiveness",
            "self-organizing maps",
            "logistic regression analysis",
            "social network analysis",
        ],
    ),
    (
        "QCA & Methodological Diversity",
        [
            "fuzzy-set qualitative comparative analysis",
            "qualitative comparative analysis",
            "discriminant analysis",
            "exploratory factor analysis",
            "data envelopment analysis",
        ],
    ),
    (
        "Regression, PCA & Scaling",
        [
            "multiple regression",
            "principal component analysis",
            "multidimensional scaling",
            "biplot",
            "hospitality",
            "social media",
        ],
    ),
    (
        "Environmental & Consumer Behavior",
        [
            "environmental management",
            "consumer behavior",
            "heavy metals",
            "brand personality",
            "conservation",
            "ecological indicators",
        ],
    ),
    (
        "SEM & Behavioral Models",
        [
            "structural equation modeling",
            "satisfaction",
            "destination image",
            "loyalty",
            "motivation",
            "service quality",
        ],
    ),
    (
        "COVID-19, Sustainability & Intentions",
        [
            "covid-19",
            "sustainability",
            "behavioral intention",
            "theory of planned behavior",
            "resilience",
            "ecotourism",
            "medical tourism",
        ],
    ),
]


def _assign_semantic_name(keywords: list[str]) -> str | None:
    """Asigna nombre semántico a una comunidad según sus keywords."""
    kw_set = set(keywords)
    for name, rule_keywords in COMMUNITY_NAMING_RULES:
        matches = sum(1 for kw in rule_keywords if kw in kw_set)
        if matches >= 2:
            return name
    return None


def label_communities(
    G: nx.Graph,
    partition: dict[str, int],
    top_n: int = DEFAULTS.top_keywords_per_community,
) -> pd.DataFrame:
    """Etiqueta cada comunidad con nombre semántico y keywords más frecuentes.

    Args:
        G: Grafo con atributo 'frequency' en nodos.
        partition: Diccionario {nodo: id_comunidad}.
        top_n: Número de keywords top para la etiqueta.

    Returns:
        DataFrame con columnas: community, name, label, size, keywords.
    """
    community_nodes: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for node, comm_id in partition.items():
        freq = G.nodes[node].get("frequency", 1)
        community_nodes[comm_id].append((node, freq))

    records = []
    for comm_id, nodes in sorted(community_nodes.items()):
        all_sorted = sorted(nodes, key=lambda x: x[1], reverse=True)
        all_keywords = [kw for kw, _ in all_sorted]
        top_kws = all_sorted[:top_n]
        rest_count = len(nodes) - len(top_kws)
        label = " / ".join([kw for kw, _ in top_kws])
        if rest_count > 0:
            label += f" (+{rest_count} más)"

        semantic_name = _assign_semantic_name(all_keywords)
        name = semantic_name if semantic_name else f"Comunidad {comm_id}"

        records.append(
            {
                "community": comm_id,
                "name": name,
                "label": label,
                "size": len(nodes),
                "keywords": all_keywords,
            }
        )
        logger.info("{}: {} ({} nodos)", name, label, len(nodes))

    return pd.DataFrame(records)
