"""Lectura del archivo Excel exportado de Web of Science."""

from pathlib import Path

import pandas as pd
from loguru import logger

from co_occurrence.config import DATA_FILE, SHEET_NAME


def load_wos_data(
    path: Path = DATA_FILE,
    sheet_name: str = SHEET_NAME,
) -> pd.DataFrame:
    """Lee el archivo Excel de WoS y retorna un DataFrame limpio.

    Args:
        path: Ruta al archivo Excel.
        sheet_name: Nombre de la hoja a leer.

    Returns:
        DataFrame con los 331 registros WoS.
    """
    logger.info("Leyendo datos WoS desde {}", path)
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    logger.info("Cargados {} registros con {} columnas", len(df), len(df.columns))

    # Strip whitespace de nombres de columna
    df.columns = df.columns.str.strip()

    return df
