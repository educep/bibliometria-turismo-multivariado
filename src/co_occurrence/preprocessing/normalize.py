"""Normalización de keywords: diccionario de sinónimos y deduplicación."""

import pandas as pd
from loguru import logger

from co_occurrence.synonyms import KEYWORD_STOPLIST, KEYWORD_SYNONYMS


def normalize_keyword(
    kw: str,
    synonyms: dict[str, str] = KEYWORD_SYNONYMS,
    stoplist: set[str] = KEYWORD_STOPLIST,
) -> str:
    """Normaliza una keyword aplicando sinónimos. Retorna '' si está en stoplist."""
    kw = kw.strip().lower()
    if kw in stoplist:
        return ""
    return synonyms.get(kw, kw)


def normalize_keyword_series(
    series: pd.Series,
    synonyms: dict[str, str] = KEYWORD_SYNONYMS,
) -> pd.Series:
    """Normaliza una Series de keywords ya parseadas (una keyword por fila).

    Args:
        series: Series con una keyword por fila.
        synonyms: Diccionario de sinónimos.

    Returns:
        Series normalizada.
    """
    normalized = series.map(lambda kw: normalize_keyword(kw, synonyms))
    n_mapped = (normalized != series).sum()
    n_stopped = (normalized == "").sum()
    logger.info(
        "Normalizadas {} keywords vía sinónimos, {} eliminadas por stoplist", n_mapped, n_stopped
    )
    return normalized[normalized != ""]


def build_synonym_candidates(series: pd.Series, min_freq: int = 2) -> pd.DataFrame:
    """Detecta posibles sinónimos analizando keywords que comparten tokens.

    Util para expandir el diccionario de sinónimos manualmente.

    Args:
        series: Series de keywords parseadas (una por fila).
        min_freq: Frecuencia mínima para considerar una keyword.

    Returns:
        DataFrame con pares candidatos a sinónimo.
    """
    freq = series.value_counts()
    keywords = freq[freq >= min_freq].index.tolist()

    candidates: list[dict[str, str | int]] = []
    for i, kw_a in enumerate(keywords):
        tokens_a = set(kw_a.split())
        for kw_b in keywords[i + 1 :]:
            tokens_b = set(kw_b.split())
            overlap = tokens_a & tokens_b
            if len(overlap) >= 1 and (kw_a != kw_b):
                candidates.append(
                    {
                        "keyword_a": kw_a,
                        "keyword_b": kw_b,
                        "shared_tokens": " ".join(sorted(overlap)),
                        "freq_a": int(freq[kw_a]),
                        "freq_b": int(freq[kw_b]),
                    }
                )

    return pd.DataFrame(candidates).sort_values("shared_tokens", ascending=False)
