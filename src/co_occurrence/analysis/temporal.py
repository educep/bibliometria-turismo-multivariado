"""Análisis de evolución temporal: grafos por ventana y detección de keywords emergentes."""

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS
from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph


def build_temporal_graphs(
    df: pd.DataFrame,
    column: str = "Author Keywords",
    window_years: int = DEFAULTS.temporal_window_years,
    windows: list[tuple[int, int]] | None = None,
    min_weight: int = 1,
) -> dict[str, nx.Graph]:
    """Construye un grafo de co-ocurrencia por cada ventana temporal.

    Args:
        df: DataFrame WoS con columna 'Publication Year'.
        column: Columna multi-valor para co-ocurrencia.
        window_years: Tamaño de la ventana en años.
        windows: Lista explícita de (inicio, fin). Si None, se genera automáticamente.
        min_weight: Peso mínimo para aristas (usar 1 para ventanas pequeñas).

    Returns:
        Diccionario {etiqueta_periodo: grafo}.
    """
    if windows is None:
        years = df["Publication Year"].dropna().astype(int)
        min_y, max_y = int(years.min()), int(years.max())
        windows = [(y, y + window_years - 1) for y in range(min_y, max_y + 1, window_years)]

    graphs = {}
    for start, end in windows:
        mask = df["Publication Year"].between(start, end)
        subset = df[mask]
        if len(subset) == 0:
            continue
        G = build_cooccurrence_graph(subset, column, min_weight=min_weight)
        label = f"{start}-{end}"
        graphs[label] = G
        logger.info("Período {}: {} artículos, {} nodos", label, len(subset), G.number_of_nodes())

    return graphs


def keyword_evolution_metrics(temporal_graphs: dict[str, nx.Graph]) -> pd.DataFrame:
    """Calcula métricas por keyword por período temporal.

    Args:
        temporal_graphs: Diccionario {periodo: grafo} generado por build_temporal_graphs.

    Returns:
        DataFrame con columnas: period, keyword, frequency, degree,
        weighted_degree, betweenness.
    """
    records = []
    for period, G in temporal_graphs.items():
        bc = nx.betweenness_centrality(G, weight="weight")
        for node in G.nodes():
            records.append(
                {
                    "period": period,
                    "keyword": node,
                    "frequency": G.nodes[node].get("frequency", 1),
                    "degree": G.degree(node),
                    "weighted_degree": G.degree(node, weight="weight"),
                    "betweenness": bc.get(node, 0),
                }
            )

    return pd.DataFrame(records)


def detect_emerging_declining(
    temporal_graphs: dict[str, nx.Graph],
    n_early: int = 2,
) -> tuple[set[str], set[str]]:
    """Detecta keywords emergentes y en declive.

    - Emergentes: aparecen en el último período pero no en los primeros n_early.
    - En declive: aparecen en los primeros n_early pero no en el último.

    Args:
        temporal_graphs: Diccionario {periodo: grafo} ordenado cronológicamente.
        n_early: Número de períodos iniciales a considerar como "tempranos".

    Returns:
        Tupla (emerging, declining) con sets de keywords.
    """
    all_periods = sorted(temporal_graphs.keys())

    early_keywords: set[str] = set()
    for period in all_periods[:n_early]:
        early_keywords.update(temporal_graphs[period].nodes())

    late_keywords = set(temporal_graphs[all_periods[-1]].nodes())

    emerging = late_keywords - early_keywords
    declining = early_keywords - late_keywords

    logger.info("Keywords emergentes: {} | En declive: {}", len(emerging), len(declining))
    return emerging, declining
