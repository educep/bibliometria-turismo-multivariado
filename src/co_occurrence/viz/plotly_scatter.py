"""Scatter plots de centralidades y biplots con Plotly."""

from pathlib import Path

import pandas as pd
from loguru import logger


def plot_degree_vs_betweenness(
    centralities: pd.DataFrame,
    title: str = "Degree vs Betweenness Centrality",
    height: int = 600,
    save_path: Path | None = None,
) -> object:
    """Scatter plot degree vs betweenness con cuadrantes.

    Keywords en el cuadrante alto-alto son pilares del campo.
    Keywords con alto betweenness pero bajo degree son puentes interdisciplinarios.

    Args:
        centralities: DataFrame de compute_centralities() con columnas
                      keyword, weighted_degree, betweenness, frequency, [community].
        title: Título del gráfico.
        height: Altura en píxeles.
        save_path: Ruta para guardar HTML.

    Returns:
        Figura Plotly.
    """
    import plotly.express as px

    color_col = "community" if "community" in centralities.columns else "frequency"

    fig = px.scatter(
        centralities,
        x="weighted_degree",
        y="betweenness",
        size="frequency",
        color=color_col,
        hover_name="keyword",
        hover_data=["frequency", "closeness", "eigenvector", "pagerank"],
        title=title,
        labels={
            "weighted_degree": "Grado ponderado",
            "betweenness": "Betweenness Centrality",
        },
        height=height,
        color_continuous_scale="Viridis",
    )

    # Líneas de cuadrante en medianas
    median_degree = centralities["weighted_degree"].median()
    median_between = centralities["betweenness"].median()

    fig.add_hline(y=median_between, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=median_degree, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(template="plotly_white")

    if save_path:
        fig.write_html(str(save_path), include_plotlyjs="cdn")
        logger.info("Scatter guardado en {}", save_path)

    return fig


def plot_manifold_scatter(
    coords: pd.DataFrame,
    partition: dict[str, int] | None = None,
    method: str = "UMAP",
    top_n_labels: int = 20,
    height: int = 700,
    save_path: Path | None = None,
) -> object:
    """Scatter plot de coordenadas de reducción dimensional coloreado por comunidad.

    Args:
        coords: DataFrame con columnas keyword, x, y, frequency (de reduce_*).
        partition: Diccionario {keyword: community_id} para colorear.
        method: Nombre del método (para el título).
        top_n_labels: Número de keywords más frecuentes con etiqueta visible.
        height: Altura en píxeles.
        save_path: Ruta para guardar HTML.

    Returns:
        Figura Plotly.
    """
    import plotly.express as px

    df = coords.copy()

    if partition:
        df["community"] = df["keyword"].map(partition).fillna(-1).astype(int).astype(str)
        color_col = "community"
        color_seq = None
    else:
        color_col = "frequency"
        color_seq = "Viridis"

    fig = px.scatter(
        df,
        x="x",
        y="y",
        size="frequency",
        color=color_col,
        hover_name="keyword",
        hover_data=["frequency"],
        title=f"Mapa de keywords — {method}",
        labels={"x": f"{method} dim 1", "y": f"{method} dim 2"},
        height=height,
        size_max=40,
        color_continuous_scale=color_seq,
    )

    # Etiquetas para las top-N keywords más frecuentes
    import plotly.graph_objects as go

    top = df.nlargest(top_n_labels, "frequency")
    fig.add_trace(
        go.Scatter(
            x=top["x"],
            y=top["y"],
            mode="text",
            text=top["keyword"],
            textposition="top center",
            textfont=dict(size=9, color="black"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(template="plotly_white")

    if save_path:
        fig.write_html(str(save_path), include_plotlyjs="cdn")
        logger.info("Manifold scatter guardado en {}", save_path)

    return fig


def plot_ca_biplot(
    row_coords: pd.DataFrame,
    col_coords: pd.DataFrame,
    title: str = "Biplot — Análisis de Correspondencias",
    top_n_row_labels: int = 25,
    top_n_col_labels: int = 15,
    height: int = 800,
    save_path: Path | None = None,
) -> object:
    """Biplot del Análisis de Correspondencias: filas y columnas en el mismo espacio.

    Args:
        row_coords: Coordenadas de filas (ej. keywords) con columnas x, y, entity_type,
                    frequency, contribution.
        col_coords: Coordenadas de columnas (ej. revistas) con columnas x, y, entity_type,
                    frequency, contribution.
        title: Título del gráfico.
        top_n_row_labels: Número de filas con etiqueta visible (por contribución).
        top_n_col_labels: Número de columnas con etiqueta visible (por contribución).
        height: Altura en píxeles.
        save_path: Ruta para guardar HTML.

    Returns:
        Figura Plotly.
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    # Extraer varianza explicada si está disponible
    pct = row_coords.attrs.get("explained_inertia", [None, None])
    dim1_label = f"Dim 1 ({pct[0]:.1f}%)" if pct[0] else "Dim 1"
    dim2_label = f"Dim 2 ({pct[1]:.1f}%)" if pct[1] else "Dim 2"

    has_freq = "frequency" in row_coords.columns
    has_contrib = "contribution" in row_coords.columns

    row_name = row_coords["entity_type"].iloc[0] if len(row_coords) > 0 else "rows"
    col_name = col_coords["entity_type"].iloc[0] if len(col_coords) > 0 else "cols"

    # --- Filas (keywords): todos los puntos ---
    row_size: pd.Series | int
    if has_freq:
        row_freq = row_coords["frequency"].clip(lower=2)
        row_size = (row_freq / row_freq.max() * 20 + 4).astype(int)
    else:
        row_size = 6
    fig.add_trace(
        go.Scatter(
            x=row_coords["x"],
            y=row_coords["y"],
            mode="markers",
            marker=dict(
                size=row_size,
                color="steelblue",
                symbol="circle",
                opacity=0.6,
                line=dict(width=0.5, color="white"),
            ),
            name=row_name,
            customdata=(
                list(
                    zip(
                        row_coords.index,
                        row_coords.get("frequency", [""]) * len(row_coords.index),
                    )
                )
                if has_freq
                else None
            ),
            hovertemplate=(
                (
                    "<b>%{customdata[0]}</b><br>freq: %{customdata[1]}<br>"
                    "x: %{x:.3f}, y: %{y:.3f}<extra></extra>"
                )
                if has_freq
                else None
            ),
        )
    )

    # Etiquetas solo para las top-N keywords por contribución
    if has_contrib:
        top_rows = row_coords.nlargest(top_n_row_labels, "contribution")
    else:
        top_rows = row_coords.head(top_n_row_labels)
    fig.add_trace(
        go.Scatter(
            x=top_rows["x"],
            y=top_rows["y"],
            mode="text",
            text=top_rows.index,
            textposition="top center",
            textfont=dict(size=9, color="steelblue", family="Arial"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # --- Columnas (revistas): todos los puntos ---
    col_size: pd.Series | int
    if has_freq:
        col_freq = col_coords["frequency"].clip(lower=2)
        col_size = (col_freq / col_freq.max() * 24 + 5).astype(int)
    else:
        col_size = 8
    fig.add_trace(
        go.Scatter(
            x=col_coords["x"],
            y=col_coords["y"],
            mode="markers",
            marker=dict(
                size=col_size,
                color="coral",
                symbol="triangle-up",
                opacity=0.7,
                line=dict(width=0.5, color="white"),
            ),
            name=col_name,
            customdata=(
                list(
                    zip(
                        col_coords.index,
                        col_coords.get("frequency", [""]) * len(col_coords.index),
                    )
                )
                if has_freq
                else None
            ),
            hovertemplate=(
                (
                    "<b>%{customdata[0]}</b><br>freq: %{customdata[1]}<br>"
                    "x: %{x:.3f}, y: %{y:.3f}<extra></extra>"
                )
                if has_freq
                else None
            ),
        )
    )

    # Etiquetas solo para las top-N revistas por contribución
    if has_contrib:
        top_cols = col_coords.nlargest(top_n_col_labels, "contribution")
    else:
        top_cols = col_coords.head(top_n_col_labels)
    fig.add_trace(
        go.Scatter(
            x=top_cols["x"],
            y=top_cols["y"],
            mode="text",
            text=top_cols.index,
            textposition="bottom center",
            textfont=dict(size=8, color="coral", family="Arial"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Ejes cruzados en el origen
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.4)
    fig.add_vline(x=0, line_dash="dot", line_color="gray", opacity=0.4)

    fig.update_layout(
        title=title,
        template="plotly_white",
        xaxis_title=dim1_label,
        yaxis_title=dim2_label,
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    if save_path:
        fig.write_html(str(save_path), include_plotlyjs="cdn")
        logger.info("Biplot guardado en {}", save_path)

    return fig
