"""Exportación de grafos interactivos con pyvis."""

from pathlib import Path

import networkx as nx
from loguru import logger


def export_pyvis(
    G: nx.Graph,
    output_path: Path,
    height: str = "800px",
    width: str = "100%",
    bgcolor: str = "#ffffff",
    partition: dict[str, int] | None = None,
) -> Path:
    """Exporta un grafo como HTML interactivo con pyvis.

    Args:
        G: Grafo networkx.
        output_path: Ruta del archivo HTML de salida.
        height: Altura del canvas.
        width: Ancho del canvas.
        bgcolor: Color de fondo.
        partition: Diccionario {nodo: comunidad} para colorear nodos.

    Returns:
        Ruta del archivo generado.
    """
    from pyvis.network import Network

    net = Network(height=height, width=width, bgcolor=bgcolor, notebook=False)

    # Paleta de colores para comunidades
    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#aec7e8",
        "#ffbb78",
        "#98df8a",
        "#ff9896",
        "#c5b0d5",
    ]

    for node in G.nodes():
        freq = G.nodes[node].get("frequency", 1)
        size = max(10, min(50, freq * 3))
        color = "#1f77b4"
        if partition and node in partition:
            color = colors[partition[node] % len(colors)]
        net.add_node(
            node,
            label=node,
            size=size,
            color=color,
            title=f"{node}\nFreq: {freq}",
        )

    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 1)
        net.add_edge(u, v, value=weight, title=f"weight: {weight}")

    net.show(str(output_path), notebook=False)
    logger.info("Grafo pyvis exportado a {}", output_path)
    return output_path
