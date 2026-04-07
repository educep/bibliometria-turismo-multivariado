"""Análisis de Correspondencias (CA) y Análisis de Correspondencias Múltiple (MCA)."""

import pandas as pd
from loguru import logger

from co_occurrence.config import DEFAULTS, MULTIVALUE_SEP
from co_occurrence.preprocessing.normalize import normalize_keyword

_DEGENERATE_THRESHOLD = 0.99


def _build_contingency(
    df: pd.DataFrame,
    row_column: str,
    col_column: str,
    sep: str,
    normalize_rows: bool,
    min_freq: int = 2,
) -> pd.DataFrame:
    """Construye y filtra la tabla de contingencia row × col."""
    rows_expanded = df[[row_column, col_column]].dropna(subset=[row_column, col_column])

    rows_exploded = rows_expanded.assign(
        **{row_column: rows_expanded[row_column].str.split(sep)}
    ).explode(row_column)
    rows_exploded[row_column] = rows_exploded[row_column].str.strip().str.lower()

    if normalize_rows:
        rows_exploded[row_column] = rows_exploded[row_column].map(normalize_keyword)
        rows_exploded = rows_exploded[rows_exploded[row_column] != ""]

    if rows_exploded[col_column].str.contains(sep, na=False).any():
        rows_exploded = rows_exploded.assign(
            **{col_column: rows_exploded[col_column].str.split(sep)}
        ).explode(col_column)
        rows_exploded[col_column] = rows_exploded[col_column].str.strip().str.lower()

    rows_exploded = rows_exploded.reset_index(drop=True)
    contingency = pd.crosstab(rows_exploded[row_column], rows_exploded[col_column])

    while True:
        row_mask = contingency.sum(axis=1) >= min_freq
        col_mask = contingency.sum(axis=0) >= min_freq
        filtered = contingency.loc[row_mask, col_mask]
        if filtered.shape == contingency.shape:
            break
        contingency = filtered

    return contingency


def compute_ca(
    df: pd.DataFrame,
    row_column: str = "Author Keywords",
    col_column: str = "Source Title",
    sep: str = MULTIVALUE_SEP,
    n_components: int = DEFAULTS.dimred_n_components,
    normalize_rows: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Análisis de Correspondencias simple sobre tabla de contingencia.

    Proyecta filas (ej. keywords) y columnas (ej. revistas) en el mismo espacio.
    Salta automáticamente dimensiones degeneradas (eigenvalue ≈ 1.0) causadas
    por pares exclusivos keyword-revista.

    Args:
        df: DataFrame WoS.
        row_column: Columna para filas de la tabla de contingencia.
        col_column: Columna para columnas de la tabla de contingencia.
        sep: Separador en campos multi-valor.
        n_components: Número de componentes útiles (se extraen más si hay degenerados).
        normalize_rows: Si True y row_column es keywords, normaliza con sinónimos.

    Returns:
        Tupla (row_coords, col_coords) como DataFrames con columnas x, y.
    """
    import prince

    logger.info("CA: construyendo tabla de contingencia {} x {}...", row_column, col_column)

    contingency = _build_contingency(df, row_column, col_column, sep, normalize_rows)
    logger.info("CA: tabla de contingencia {}x{}", *contingency.shape)

    # Extraer componentes extra para poder saltar los degenerados
    max_components = min(contingency.shape) - 1
    n_extract = min(n_components + 4, max_components)

    ca = prince.CA(n_components=n_extract)
    ca.fit(contingency)

    eigenvalues = ca.eigenvalues_
    total_inertia = ca.total_inertia_

    # Identificar dimensiones degeneradas (eigenvalue ≈ 1.0)
    n_degenerate = sum(1 for ev in eigenvalues if ev >= _DEGENERATE_THRESHOLD)
    if n_degenerate > 0:
        logger.warning(
            "CA: {} dimensiones degeneradas detectadas (eigenvalue >= {:.2f}), saltando",
            n_degenerate,
            _DEGENERATE_THRESHOLD,
        )

    row_all = ca.row_coordinates(contingency)
    col_all = ca.column_coordinates(contingency)

    # Seleccionar las primeras n_components dimensiones NO degeneradas
    good_dims = [i for i, ev in enumerate(eigenvalues) if ev < _DEGENERATE_THRESHOLD]
    dims_to_use = good_dims[:n_components]

    if len(dims_to_use) < n_components:
        logger.warning(
            "CA: solo {} dimensiones no-degeneradas disponibles (pedidas {})",
            len(dims_to_use),
            n_components,
        )

    row_coords = row_all.iloc[:, dims_to_use].copy()
    col_coords = col_all.iloc[:, dims_to_use].copy()

    col_names = (
        ["x", "y"] if len(dims_to_use) == 2 else [f"dim_{i}" for i in range(len(dims_to_use))]
    )
    row_coords.columns = col_names
    col_coords.columns = col_names

    # Frecuencia marginal para tamaño de puntos
    row_coords["frequency"] = contingency.sum(axis=1)
    col_coords["frequency"] = contingency.sum(axis=0)

    # Contribución a la inercia (para decidir qué etiquetar)
    row_coords["contribution"] = (row_coords["x"] ** 2 + row_coords["y"] ** 2) * row_coords[
        "frequency"
    ]
    col_coords["contribution"] = (col_coords["x"] ** 2 + col_coords["y"] ** 2) * col_coords[
        "frequency"
    ]

    row_coords["entity_type"] = row_column
    col_coords["entity_type"] = col_column

    # Varianza explicada por las dimensiones usadas
    pct = [eigenvalues[d] / total_inertia * 100 for d in dims_to_use]
    dim_labels = [f"dim{d + 1}" for d in dims_to_use]
    for lbl, p in zip(dim_labels, pct):
        logger.info("CA inercia {}: {:.1f}%", lbl, p)
    logger.info("CA inercia acumulada 2D: {:.1f}%", sum(pct[:2]))
    row_coords.attrs["explained_inertia"] = pct
    col_coords.attrs["explained_inertia"] = pct

    logger.info(
        "CA completado: {} filas, {} columnas proyectadas", len(row_coords), len(col_coords)
    )
    return row_coords, col_coords
