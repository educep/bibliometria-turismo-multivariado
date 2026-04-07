"""Exportación de grafos y métricas: GEXF para Gephi, CSV."""

from pathlib import Path

import networkx as nx
import pandas as pd
from loguru import logger

from co_occurrence.config import OUTPUT_DIR


def export_gexf(G: nx.Graph, name: str, output_dir: Path = OUTPUT_DIR) -> Path:
    """Exporta un grafo en formato GEXF para Gephi.

    Args:
        G: Grafo networkx con atributos en nodos y aristas.
        name: Nombre base del archivo (sin extensión).
        output_dir: Directorio de salida.

    Returns:
        Ruta del archivo generado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}.gexf"
    nx.write_gexf(G, str(path))
    logger.info(
        "GEXF exportado: {} ({} nodos, {} aristas)", path, G.number_of_nodes(), G.number_of_edges()
    )
    return path


def export_csv(df: pd.DataFrame, name: str, output_dir: Path = OUTPUT_DIR) -> Path:
    """Exporta un DataFrame a CSV.

    Args:
        df: DataFrame a exportar.
        name: Nombre base del archivo (sin extensión).
        output_dir: Directorio de salida.

    Returns:
        Ruta del archivo generado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    logger.info("CSV exportado: {} ({} filas)", path, len(df))
    return path
