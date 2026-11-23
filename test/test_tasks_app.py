"""Tests d'integració dels escenaris GS-01, GS-02 i GS-03."""

import json

from src.tasks_app import afegir_tasca, llistar_tasques


def ruta_temporal(tmp_path):
    """Retorna la ruta del fitxer JSON dins del directori temporal."""
    # La ruta temporal aïlla les proves del fitxer real del projecte.
    return tmp_path / "data" / "tasks.json"


def test_crear_tasca_amb_estat_pendent(tmp_path, capsys):
    """GS-01: es confirma la creació i la tasca queda al fitxer JSON."""
    ruta = ruta_temporal(tmp_path)
    tasca = afegir_tasca("Pràctica 1", "RS", ruta)

    assert capsys.readouterr().out.strip() == "Tasca [ID: 1] creada amb èxit"
    assert tasca.estat == "pendent"
    assert json.loads(ruta.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": None,
        }
    ]


def test_llistar_tasques_amb_registre_buit(tmp_path, capsys):
    """GS-02: sense registres es mostra el missatge de registre buit."""
    ruta = ruta_temporal(tmp_path)
    llistar_tasques(ruta)

    # Un fitxer inexistent s'inicialitza amb una llista JSON buida.
    assert ruta.read_text(encoding="utf-8") == "[]"
    assert capsys.readouterr().out.strip() == "Registre de tasques buit."


def test_llistar_tasques_amb_registres(tmp_path, capsys):
    """GS-03: el llistat mostra l'ID, el títol, l'assignatura i l'estat."""
    ruta = ruta_temporal(tmp_path)
    afegir_tasca("Pràctica 1", "RS", ruta)
    afegir_tasca("Examen parcial", "SO", ruta)
    # Es descarta la sortida de la creació per llegir només el llistat.
    capsys.readouterr()

    llistar_tasques(ruta)

    assert capsys.readouterr().out.splitlines() == [
        "[1] Pràctica 1 (RS) - estat: pendent",
        "[2] Examen parcial (SO) - estat: pendent",
    ]
