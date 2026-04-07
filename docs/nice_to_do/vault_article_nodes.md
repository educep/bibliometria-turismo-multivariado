# Notas de Artículos en el Vault Obsidian — Nice to Do

## Qué es y por qué hacerlo

Actualmente el vault tiene 4 tipos de nodos: **keywords**, **autores**, **journals** y **comunidades**. Los artículos NO son nodos — solo aparecen como texto plano (lista bullet) dentro de las notas de autores.

Esto significa que en el graph view de Obsidian, los **autores son hojas**: enlazan a keywords, journals y coautores, pero nadie enlaza de vuelta a ellos de forma significativa. No hay forma de navegar "desde una keyword, ver qué artículos la usan, y de ahí saltar a sus otros autores o métodos".

## Qué cambiaría

Añadir una nota `.md` por cada uno de los 331 artículos. Cada nota enlazaría vía wikilinks a:

- Sus **autores** → `[[Author Name]]`
- Su **journal** → `[[Source Title]]`
- Sus **keywords** → `[[keyword]]`
- Su **comunidad dominante** → `[[SEM & Behavioral Models]]` (la comunidad de su keyword más frecuente)

### Frontmatter propuesto

```yaml
---
type: article
title: "Article Title"
year: 2019
doi: "10.1234/..."
journal: "Tourism Management"
community: "SEM & Behavioral Models"
n_authors: 3
n_keywords: 5
tags:
  - article
  - year-2019
---
```

### Estructura del grafo resultante

```
Comunidades ← Keywords ↔ Keywords
                ↑
            Articles  ← nuevo nodo intermedio
           ↙    ↓    ↘
     Authors  Journals  Keywords
```

Los artículos se convierten en el nodo conector central: cada artículo es la evidencia concreta de que un conjunto de autores, keywords y un journal están relacionados. Los autores dejan de ser hojas.

## Valor añadido

1. **Navegación contextual:** desde "cluster analysis" → ver los 15 artículos que la usan → explorar sus autores y journals específicos
2. **Graph view más rico:** los artículos crean puentes entre autores que no son coautores pero trabajan en las mismas keywords
3. **Queries Dataview potentes:**
   - "Artículos de la comunidad SEM publicados después de 2020"
   - "Journals con más artículos en la comunidad Time Series"
   - "Autores que publican en más de una comunidad"
4. **Detección de artículos puente:** artículos cuyas keywords pertenecen a 2+ comunidades son interdisciplinarios

## Implementación

Añadir `generate_article_notes()` en `obsidian.py`:

```python
def generate_article_notes(
    df: pd.DataFrame,
    partition: dict[str, int],
    community_names: dict[int, str],
    vault_path: Path = VAULT_DIR,
) -> None:
    for _, row in df.iterrows():
        title = str(row.get("Article Title", ""))
        # Asignar comunidad dominante via keyword más frecuente
        # Enlazar a autores, keywords, journal
        ...
```

Y llamar desde `generate_vault()` y el CLI `vault`.

## Consideraciones

- **331 notas adicionales** — incremento modesto, Obsidian maneja miles sin problema
- **Nombres de archivo:** sanitizar títulos largos (truncar a ~80 chars + hash corto para unicidad)
- **DOI como identificador:** incluir en frontmatter para link externo a WoS/publisher
- **Comunidad dominante del artículo:** se asigna como la comunidad de la keyword con mayor frecuencia global entre las keywords del artículo. Si hay empate, tomar la keyword con mayor betweenness.

## Estimación de esfuerzo

~2-3 horas: función de generación + integración con vault command + queries Dataview de ejemplo en el INDEX.
