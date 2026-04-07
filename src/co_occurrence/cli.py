"""CLI del proyecto co-occurrence usando Typer."""

from pathlib import Path

import typer
from loguru import logger

app = typer.Typer(
    name="co-occurrence",
    help="Análisis bibliométrico multivariado — co-ocurrencia, comunidades y grafos.",
)


@app.command()
def load(
    path: Path = typer.Option(None, help="Ruta al Excel WoS (default: data/)"),
) -> None:
    """Carga y muestra resumen de los datos WoS."""
    from co_occurrence.config import DATA_FILE
    from co_occurrence.io.loader import load_wos_data

    df = load_wos_data(path or DATA_FILE)
    typer.echo(f"Registros: {len(df)}")
    typer.echo(f"Columnas: {len(df.columns)}")
    typer.echo(f"Años: {int(df['Publication Year'].min())}-{int(df['Publication Year'].max())}")
    typer.echo(f"Keywords no nulas: {df['Author Keywords'].notna().sum()}")


@app.command()
def build_keywords(
    min_weight: int = typer.Option(1, help="Peso mínimo para aristas"),
    min_frequency: int = typer.Option(2, help="Frecuencia mínima de un keyword"),
) -> None:
    """Construye el grafo de co-ocurrencia de Author Keywords."""
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_gexf

    df = load_wos_data()
    G = build_cooccurrence_graph(
        df, column="Author Keywords", min_weight=min_weight, min_frequency=min_frequency
    )
    export_gexf(G, "keyword_cooccurrence")
    typer.echo(f"Grafo: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")


@app.command()
def build_coauthors(
    min_weight: int = typer.Option(1, help="Peso mínimo para aristas"),
) -> None:
    """Construye el grafo de co-autoría."""
    from co_occurrence.graphs.coauthor import build_coauthor_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_gexf

    df = load_wos_data()
    G = build_coauthor_graph(df, min_weight=min_weight)
    export_gexf(G, "coauthor_network")
    typer.echo(f"Grafo: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")


@app.command()
def communities(
    algorithm: str = typer.Option("louvain", help="Algoritmo: louvain o leiden"),
    resolution: float = typer.Option(1.0, help="Resolución (solo Louvain)"),
) -> None:
    """Detecta comunidades en el grafo de co-ocurrencia de keywords."""
    from co_occurrence.analysis.communities import (
        detect_leiden,
        detect_louvain,
        label_communities,
    )
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv

    df = load_wos_data()
    G = build_cooccurrence_graph(df, min_weight=1, min_frequency=2)

    if algorithm == "leiden":
        partition = detect_leiden(G)
    else:
        partition = detect_louvain(G, resolution=resolution)

    labels = label_communities(G, partition)
    export_csv(labels, "communities_labeled")
    typer.echo(labels.to_string(index=False))


@app.command()
def centralities() -> None:
    """Calcula métricas de centralidad cruzada."""
    from co_occurrence.analysis.centrality import compute_centralities
    from co_occurrence.analysis.communities import detect_louvain
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv

    df = load_wos_data()
    G = build_cooccurrence_graph(df, min_weight=1, min_frequency=2)
    partition = detect_louvain(G)
    df_cent = compute_centralities(G, partition=partition)
    export_csv(df_cent, "centralities")
    typer.echo(df_cent.head(20).to_string(index=False))


@app.command()
def evolution(
    window: int = typer.Option(5, help="Tamaño de ventana en años"),
) -> None:
    """Analiza evolución temporal de keywords."""
    from co_occurrence.analysis.temporal import (
        build_temporal_graphs,
        detect_emerging_declining,
        keyword_evolution_metrics,
    )
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv

    df = load_wos_data()
    graphs = build_temporal_graphs(df, window_years=window)
    df_evo = keyword_evolution_metrics(graphs)
    export_csv(df_evo, "keyword_evolution")

    emerging, declining = detect_emerging_declining(graphs)
    typer.echo(f"\nKeywords emergentes ({len(emerging)}):")
    for kw in sorted(emerging)[:20]:
        typer.echo(f"  + {kw}")
    typer.echo(f"\nKeywords en declive ({len(declining)}):")
    for kw in sorted(declining)[:20]:
        typer.echo(f"  - {kw}")


@app.command()
def dimred(
    method: str = typer.Option("umap", help="Método: mds, tsne o umap"),
    top_labels: int = typer.Option(20, help="Keywords con etiqueta visible"),
) -> None:
    """Reducción dimensional del grafo de co-ocurrencia + scatter interactivo."""
    from co_occurrence.analysis.communities import detect_louvain
    from co_occurrence.dimred.manifold import reduce_mds, reduce_tsne, reduce_umap
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv
    from co_occurrence.viz.plotly_scatter import plot_manifold_scatter

    df = load_wos_data()
    G = build_cooccurrence_graph(df, min_weight=1, min_frequency=2)
    partition = detect_louvain(G)

    reducers = {"mds": reduce_mds, "tsne": reduce_tsne, "umap": reduce_umap}
    if method not in reducers:
        typer.echo(f"Método no válido: {method}. Usa: mds, tsne, umap")
        raise typer.Exit(1)

    coords = reducers[method](G)
    export_csv(coords, f"dimred_{method}")

    from co_occurrence.config import OUTPUT_DIR

    save_path = OUTPUT_DIR / f"dimred_{method}.html"
    plot_manifold_scatter(
        coords,
        partition=partition,
        method=method.upper(),
        top_n_labels=top_labels,
        save_path=save_path,
    )
    typer.echo(f"{method.upper()}: {len(coords)} keywords -> {save_path}")


@app.command()
def ca(
    row_column: str = typer.Option("Author Keywords", help="Columna para filas"),
    col_column: str = typer.Option("Source Title", help="Columna para columnas"),
) -> None:
    """Análisis de Correspondencias: biplot keyword × revista en el mismo espacio."""
    from co_occurrence.config import OUTPUT_DIR
    from co_occurrence.dimred.correspondence import compute_ca
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv
    from co_occurrence.viz.plotly_scatter import plot_ca_biplot

    df = load_wos_data()
    row_coords, col_coords = compute_ca(df, row_column=row_column, col_column=col_column)

    save_path = OUTPUT_DIR / "ca_biplot.html"
    plot_ca_biplot(row_coords, col_coords, save_path=save_path)

    export_csv(row_coords.reset_index(), "ca_row_coords")
    export_csv(col_coords.reset_index(), "ca_col_coords")

    typer.echo(f"CA: {len(row_coords)} filas × {len(col_coords)} columnas -> {save_path}")


@app.command()
def vault() -> None:
    """Genera vault Obsidian con keywords, autores, revistas y comunidades."""
    from co_occurrence.analysis.centrality import compute_centralities
    from co_occurrence.analysis.communities import detect_louvain, label_communities
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.obsidian import generate_vault

    df = load_wos_data()
    G = build_cooccurrence_graph(df, min_weight=1, min_frequency=2)
    partition = detect_louvain(G)
    df_cent = compute_centralities(G, partition=partition)
    df_comm = label_communities(G, partition)
    community_names = dict(zip(df_comm["community"], df_comm["name"]))
    vault_path = generate_vault(G, partition, df_cent, df, community_names=community_names)
    typer.echo(f"Vault generado en {vault_path}")


@app.command()
def pipeline() -> None:
    """Ejecuta el pipeline completo: grafos, comunidades, centralidades, exportación."""
    from co_occurrence.analysis.centrality import compute_centralities, compute_structural_holes
    from co_occurrence.analysis.communities import (
        detect_louvain,
        label_communities,
    )
    from co_occurrence.analysis.temporal import (
        build_temporal_graphs,
        keyword_evolution_metrics,
    )
    from co_occurrence.config import OUTPUT_DIR
    from co_occurrence.dimred.correspondence import compute_ca
    from co_occurrence.dimred.manifold import reduce_umap
    from co_occurrence.graphs.coauthor import build_coauthor_graph
    from co_occurrence.graphs.cooccurrence import build_cooccurrence_graph
    from co_occurrence.graphs.weights import apply_all_normalizations
    from co_occurrence.io.loader import load_wos_data
    from co_occurrence.viz.export import export_csv, export_gexf
    from co_occurrence.viz.plotly_scatter import plot_ca_biplot, plot_manifold_scatter

    logger.info("=== Pipeline completo ===")

    # 1. Cargar datos
    df = load_wos_data()

    # 2. Grafos (min_weight=1, min_frequency=2 para densidad sin ruido)
    G_kw = build_cooccurrence_graph(df, column="Author Keywords", min_weight=1, min_frequency=2)
    G_coauthor = build_coauthor_graph(df)

    # 3. Normalización de pesos
    apply_all_normalizations(G_kw)

    # 4. Comunidades
    partition = detect_louvain(G_kw)
    labels = label_communities(G_kw, partition)

    # 5. Centralidades
    df_cent = compute_centralities(G_kw, partition=partition)

    # 6. Structural holes
    df_struct = compute_structural_holes(G_kw)

    # 7. Evolución temporal
    temporal = build_temporal_graphs(df)
    df_evo = keyword_evolution_metrics(temporal)

    # 8. Reducción dimensional (UMAP)
    coords_umap = reduce_umap(G_kw)
    plot_manifold_scatter(
        coords_umap,
        partition=partition,
        method="UMAP",
        save_path=OUTPUT_DIR / "dimred_umap.html",
    )

    # 9. Análisis de Correspondencias (keyword × revista)
    row_ca, col_ca = compute_ca(df)
    plot_ca_biplot(row_ca, col_ca, save_path=OUTPUT_DIR / "ca_biplot.html")

    # 10. Exportar
    export_gexf(G_kw, "keyword_cooccurrence")
    export_gexf(G_coauthor, "coauthor_network")
    export_csv(labels, "communities_labeled")
    export_csv(df_cent, "centralities")
    export_csv(df_struct, "structural_holes")
    export_csv(df_evo, "keyword_evolution")
    export_csv(coords_umap, "dimred_umap")
    export_csv(row_ca.reset_index(), "ca_row_coords")
    export_csv(col_ca.reset_index(), "ca_col_coords")

    logger.info("=== Pipeline completado ===")
    typer.echo("Pipeline completado. Outputs en output/")


if __name__ == "__main__":
    app()
