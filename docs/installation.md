# Guía de instalación — co-occurrence-library

## Requisitos previos

| Herramienta | Versión mínima | Notas |
|-------------|---------------|-------|
| Python | 3.13 | El proyecto requiere exactamente `>=3.13` |
| Git | cualquiera reciente | Para clonar el repositorio |
| uv | cualquiera reciente | Gestor de entornos y paquetes (recomendado) |

### Instalar uv

`uv` es el gestor de paquetes que usa el proyecto. Si aún no lo tienes:

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

O con Make:
```bash
make install_uv
```

---

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

---

## 2. Crear el entorno virtual

```bash
make venv
```

Esto crea `.venv/` en la raíz del proyecto usando `uv venv`.

### Activar el entorno

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows — PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows — Git Bash:**
```bash
source .venv/Scripts/activate
```

**Windows — cmd.exe:**
```bat
.venv\Scripts\activate.bat
```

> Puedes consultar en cualquier momento el comando correcto con `make activate`.

---

## 3. Instalar el paquete

### Instalación de desarrollo (recomendada)

Instala el paquete en modo editable junto con todas las dependencias opcionales y las herramientas de desarrollo (linters, tests):

```bash
make install
```

Equivale a:
```bash
uv pip install -e ".[dev]"
```

### Instalación mínima (solo dependencias base)

Si solo necesitas el núcleo del paquete sin herramientas de desarrollo:

```bash
uv pip install -e .
```

Las dependencias base incluyen: `loguru`, `networkx`, `openpyxl`, `pandas`, `pydantic`, `python-dotenv`, `pyyaml` y `typer`.

---

## 4. Dependencias opcionales

Instala solo los grupos que necesites según el tipo de análisis:

| Grupo | Paquetes | Cuándo instalarlo |
|-------|----------|-------------------|
| `viz` | plotly, pyvis, matplotlib | Visualización interactiva de grafos |
| `dimred` | scikit-learn, umap-learn, prince | Reducción dimensional (MDS, t-SNE, UMAP, CA) |
| `communities` | igraph, leidenalg, python-louvain | Detección de comunidades (Leiden, Louvain) |
| `topics` | bertopic | Modelado de tópicos sobre abstracts |
| `publish` | itables | Tablas interactivas para publicación Quarto |

### Instalar uno o varios grupos

```bash
# Un solo grupo
uv pip install -e ".[viz]"

# Varios grupos
uv pip install -e ".[viz,dimred,communities]"

# Todos los grupos opcionales
uv pip install -e ".[all]"
```

---

## 5. Verificar la instalación

```bash
python -m co_occurrence --help
```

Deberías ver la lista de comandos disponibles. Para verificar que los datos se cargan correctamente:

```bash
python -m co_occurrence load
```

Para ejecutar el pipeline completo:

```bash
python -m co_occurrence pipeline
```

El ejecutable de línea de comandos también está disponible directamente como:

```bash
co-occurrence --help
```

---

## 6. Instalar hooks de pre-commit (opcional, recomendado en desarrollo)

```bash
make pre_commit
```

Esto configura black, isort, flake8, bandit y mypy para que se ejecuten automáticamente antes de cada commit.

---

## Referencia rápida de comandos Make

| Comando | Descripción |
|---------|-------------|
| `make install_uv` | Instala uv (gestor de paquetes) |
| `make venv` | Crea el entorno virtual `.venv/` |
| `make install` | Instala el proyecto y todas las dependencias de desarrollo |
| `make activate` | Muestra el comando de activación para tu shell |
| `make pre_commit` | Instala los hooks de pre-commit |
| `make format` | Formatea el código con black e isort |
| `make lint` | Ejecuta todos los linters (format + flake8 + bandit + mypy) |
| `make test` | Ejecuta los tests con pytest |
| `make check-all` | lint + tests completos |
| `make clean` | Elimina el entorno virtual |

---

## Solución de problemas frecuentes

### `python` apunta a una versión anterior a 3.13

`uv` selecciona automáticamente la versión de Python correcta si está instalada. Comprueba la versión disponible:

```bash
python --version
uv python list
```

Si Python 3.13 no aparece, instálalo desde [python.org](https://www.python.org/downloads/) o con `uv python install 3.13`.

### Error al instalar `leidenalg` o `python-louvain` en Windows

Estos paquetes requieren un compilador C. Instala las **Build Tools para Visual Studio** desde [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) y vuelve a intentarlo.

### Error al instalar `umap-learn`

`umap-learn` depende de `numba`, que a su vez requiere `llvmlite`. Si la instalación falla, asegúrate de tener una versión de Python compatible con los wheels precompilados disponibles en PyPI para tu sistema operativo.

### `python -m co_occurrence` no encuentra el módulo

Asegúrate de que el entorno virtual está activado y de que el paquete se instaló en modo editable (`-e`). Verifica con:

```bash
pip show co-occurrence-library
```

La salida debe mostrar `Location: ...src` y `Editable project location`.

### Windows: `Activate.ps1` bloqueado por política de ejecución

Ejecuta en PowerShell como administrador:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### El archivo de datos no se encuentra

El archivo fuente `data/anal multiv 331 artic completo.xlsx` debe estar presente en la raíz del proyecto. No mover ni renombrar este archivo. Los outputs generados se guardan en `output/`.
