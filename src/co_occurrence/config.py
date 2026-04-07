"""Configuración global del proyecto: paths, parámetros por defecto."""

from pathlib import Path

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_FILE = DATA_DIR / "anal multiv 331 artic completo.xlsx"
SHEET_NAME = "savedrecs"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

VAULT_DIR = PROJECT_ROOT / "vault_bibliometria"

# ---------------------------------------------------------------------------
# Separador por defecto en campos multi-valor WoS
# ---------------------------------------------------------------------------
MULTIVALUE_SEP = ";"


# ---------------------------------------------------------------------------
# Parámetros por defecto para construcción de grafos y análisis
# ---------------------------------------------------------------------------
class GraphDefaults(BaseModel):
    """Parámetros por defecto para la construcción y análisis de grafos."""

    min_cooccurrence_weight: int = 2
    min_cocitation_weight: int = 5
    louvain_resolution: float = 1.0
    temporal_window_years: int = 5
    top_keywords_per_community: int = 5
    dimred_n_components: int = 2
    dimred_random_state: int = 42
    community_seed: int = 42


DEFAULTS = GraphDefaults()
