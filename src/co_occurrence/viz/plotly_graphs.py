"""Visualización de grafos con Plotly (interactivos)."""

from pathlib import Path

import networkx as nx
import pandas as pd
from loguru import logger


def _community_short_label(label: str) -> str:
    """Extrae las 2-3 primeras keywords de un label de comunidad como nombre corto."""
    parts = label.split(" / ")
    short = " / ".join(parts[:3])
    return short


def plot_network(
    G: nx.Graph,
    coords: pd.DataFrame,
    partition: dict[str, int] | None = None,
    community_labels: dict[int, str] | None = None,
    title: str = "Red de co-ocurrencia",
    min_degree_label: int = 5,
    height: int = 700,
    save_path: Path | None = None,
) -> object:
    """Dibuja un grafo interactivo con Plotly usando coordenadas pre-calculadas.

    Args:
        G: Grafo de co-ocurrencia.
        coords: DataFrame con columnas 'keyword', 'x', 'y'.
        partition: Diccionario {nodo: comunidad} para colorear.
        community_labels: Diccionario {id_comunidad: etiqueta} para la leyenda.
        title: Título del gráfico.
        min_degree_label: Solo mostrar labels para nodos con grado >= este valor.
        height: Altura del gráfico en píxeles.
        save_path: Si se provee, guarda el HTML en esta ruta.

    Returns:
        Figura Plotly.
    """
    import plotly.graph_objects as go

    # Paleta de colores discretos para comunidades
    COMMUNITY_COLORS = [
        "#1f77b4",  # azul
        "#ff7f0e",  # naranja
        "#2ca02c",  # verde
        "#d62728",  # rojo
        "#9467bd",  # púrpura
        "#8c564b",  # marrón
        "#e377c2",  # rosa
        "#7f7f7f",  # gris
        "#bcbd22",  # oliva
        "#17becf",  # cian
        "#aec7e8",  # azul claro
        "#ffbb78",  # naranja claro
    ]

    pos = dict(zip(coords["keyword"], zip(coords["x"], coords["y"])))

    # Traces de aristas
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for u, v in G.edges():
        if u in pos and v in pos:
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=0.3, color="#888"),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Nodos — un trace por comunidad para leyenda discreta
    node_data = coords[coords["keyword"].isin(G.nodes())].copy()
    if partition:
        node_data["community"] = node_data["keyword"].map(partition).fillna(-1).astype(int)
    node_data["degree"] = node_data["keyword"].map(
        lambda n: G.degree(n, weight="weight") if n in G else 0
    )
    degree_max = node_data["degree"].max()

    if partition:
        community_ids = sorted(node_data["community"].unique())
        for cid in community_ids:
            subset = node_data[node_data["community"] == cid]
            color = COMMUNITY_COLORS[cid % len(COMMUNITY_COLORS)]

            if community_labels and cid in community_labels:
                legend_name = _community_short_label(community_labels[cid])
            else:
                legend_name = f"Comunidad {cid}"

            hover = subset.apply(
                lambda r: (
                    f"{r['keyword']}<br>"
                    f"Freq: {r['frequency']}<br>"
                    f"Degree: {r['degree']}<br>"
                    f"Comunidad: {legend_name}"
                ),
                axis=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=subset["x"],
                    y=subset["y"],
                    mode="markers+text",
                    marker=dict(
                        size=subset["degree"].clip(lower=3) / degree_max * 30 + 5,
                        color=color,
                        line=dict(width=0.5, color="white"),
                    ),
                    text=[
                        n if G.degree(n) >= min_degree_label else ""
                        for n in subset["keyword"]
                    ],
                    textposition="top center",
                    textfont=dict(size=8),
                    hovertext=hover,
                    hoverinfo="text",
                    name=legend_name,
                    legendgroup=str(cid),
                )
            )
    else:
        node_data["hover"] = node_data.apply(
            lambda r: f"{r['keyword']}<br>Freq: {r['frequency']}<br>Degree: {r['degree']}",
            axis=1,
        )
        fig.add_trace(
            go.Scatter(
                x=node_data["x"],
                y=node_data["y"],
                mode="markers+text",
                marker=dict(
                    size=node_data["degree"].clip(lower=3) / degree_max * 30 + 5,
                    color=node_data["frequency"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Frecuencia"),
                ),
                text=[
                    n if G.degree(n) >= min_degree_label else ""
                    for n in node_data["keyword"]
                ],
                textposition="top center",
                textfont=dict(size=8),
                hovertext=node_data["hover"],
                hoverinfo="text",
                showlegend=False,
            )
        )

    fig.update_layout(
        title=title,
        showlegend=bool(partition),
        legend=dict(title="Comunidades", font=dict(size=10)),
        template="plotly_white",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=height,
        margin=dict(l=0, r=0, t=40, b=0),
    )

    if save_path:
        fig.write_html(str(save_path), include_plotlyjs="cdn")
        logger.info("Grafo guardado en {}", save_path)

    return fig
