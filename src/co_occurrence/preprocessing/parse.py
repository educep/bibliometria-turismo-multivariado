"""Parseo de campos multi-valor de Web of Science."""

import re

import pandas as pd

from co_occurrence.config import MULTIVALUE_SEP


def parse_multivalue(
    series: pd.Series,
    sep: str = MULTIVALUE_SEP,
    to_lower: bool = True,
) -> pd.Series:
    """Parsea una columna multi-valor separada por `sep`.

    Args:
        series: Columna del DataFrame (puede contener NaN).
        sep: Separador entre valores.
        to_lower: Si True, convierte a minúsculas.

    Returns:
        Series explotada con un valor por fila, indexada al artículo original.
    """
    result = series.dropna().str.split(sep).explode().str.strip()
    if to_lower:
        result = result.str.lower()
    # Eliminar strings vacíos tras split
    return result[result != ""]


def extract_countries_from_addresses(addresses: pd.Series) -> pd.Series:
    """Extrae países de la columna Addresses de WoS.

    El formato WoS es: "[Author] Institution, City, State, Country; ..."
    El país es generalmente el último elemento antes del siguiente ';' o fin.

    Args:
        addresses: Columna 'Addresses' del DataFrame WoS.

    Returns:
        Series explotada con un país por fila, normalizado a minúsculas.
    """
    countries: list[tuple[int, str]] = []
    for idx, addr_str in addresses.dropna().items():
        # Cada dirección está separada por ";"
        for addr in addr_str.split(";"):
            addr = addr.strip()
            # Quitar el tag de autor entre corchetes: [Author1; Author2]
            addr = re.sub(r"\[.*?\]", "", addr).strip()
            parts = [p.strip() for p in addr.split(",")]
            if parts:
                country = parts[-1].strip().lower()
                if country:
                    countries.append((idx, country))  # type: ignore[arg-type]

    result = pd.DataFrame(countries, columns=["article_idx", "country"])
    return result.set_index("article_idx")["country"]
