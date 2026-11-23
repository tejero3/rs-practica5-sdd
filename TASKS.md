# TASKS.md - Tasks_app



## Increment 1: MVP - Creació i Llistat de Tasques

Objectiu: Tenir una versió CLI funcional per afegir i consultar tasques en JSON.



### Tasques d'Execució:

- [x] Tasca 1.1: Crear estructura de directoris (`src/`, `test/`, `data/`) i fitxer `data/tasks.json` inicial. (Requisits RF-01 i RF-02) 

- [x] Tasca 1.2: Implementar model de dades `Task` a `src/models.py` amb mètodes de serialització JSON.

- [x] Tasca 1.3: Desenvolupar Tasks_app a `src/tasks_app.py` amb opcions `add` i `list`.(Requisits RF-03 i RF-04)

- [x] Tasca 1.4: Crear test d'integració a `test/test_tasks_app.py` segons els escenaris GS-01, GS-02 i GS-03.

- [x] Tasca 1.5: Validar execució amb OpenCode i verificar que tots els tests passen (`python3 -m pytest test`).


## Increment 2: Dates límit, Edició i Estats

Objectiu: Permetre gestionar dates de venciment, editar atributs, completar tasques i mostrar alertes `[CADUCADA]` i `[URGENT]` al llistat.

### Tasques d'Execució:

- [x] Tasca 2.1: Actualitzar el model `Task` a `src/models.py` incorporant l'atribut opcional `data_limit` (per defecte `None`) i adaptant la serialització/deserialització JSON per mantenir compatibilitat retroactiva. (Requisit RF-05)

- [x] Tasca 2.2: Actualitzar la funció `afegir_tasca` i el subcomandament `add` a `src/tasks_app.py` per acceptar el paràmetre `--due YYYY-MM-DD` i validar el format de la data. (Requisits RF-05 i RF-06, Escenari GS-04)

- [x] Tasca 2.3: Implementar la funcionalitat d'edició `editar_tasca` i el subcomandament `edit --id <ID>` a `src/tasks_app.py` per modificar qualsevol atribut i gestionar IDs inexistents. (Requisits RF-07 i RF-08, Escenaris GS-05 i GS-06)

- [ ] Tasca 2.4: Implementar la funcionalitat `completar_tasca` i el subcomandament `complete --id <ID>` a `src/tasks_app.py` per canviar l'estat a `'completada'`. (Requisits RF-08 i RF-09, Escenari GS-07)

- [ ] Tasca 2.5: Actualitzar `llistar_tasques` (`list`) a `src/tasks_app.py` per mostrar la data límit (quan no sigui nul·la) i calcular les etiquetes `[CADUCADA]` i `[URGENT]` segons la data actual. (Requisits RF-10 i RF-11, Escenari GS-08)

- [ ] Tasca 2.6: Afegir els tests d'integració i unitaris a `test/test_tasks_app.py` per cobrir els escenaris GS-04, GS-05, GS-06, GS-07 i GS-08, i validar amb `python3 -m pytest test`.

