---
type: index
tags:
  - dashboard
---

# Analisis Bibliometrico -- Turismo y Tecnicas Multivariadas

> Corpus: **331** articulos | Keywords: **124** | Co-ocurrencias: **365** | Comunidades: **7**

## Navegacion

- `keywords/` -- keywords y sus co-ocurrencias
- `authors/` -- autores y sus colaboraciones
- `journals/` -- revistas y su perfil tematico
- `communities/` -- clusters tematicos detectados

## Uso del graph view

1. Abrir Graph View (Ctrl+G)
2. Filtrar por `tag:#keyword` para ver solo la red de co-ocurrencia
3. Filtrar por `tag:#author` para ver solo la red de co-autoria
4. Filtrar por `tag:#comunidad-N` para aislar una comunidad
5. Colorear por tags para distinguir tipos de nodo

## Queries Dataview

### Top 10 keywords por frecuencia

```dataview
TABLE frequency, degree, betweenness, community
FROM "keywords"
SORT frequency DESC
LIMIT 10
```

### Keywords puente (alto betweenness, bajo degree)

```dataview
TABLE frequency, degree, betweenness
FROM "keywords"
WHERE betweenness > 0.05 AND degree < 20
SORT betweenness DESC
```
