"""Tests d'integració i unitaris dels escenaris GS-01 a GS-08."""

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from src.models import Task
from src.tasks_app import (
    afegir_tasca,
    completar_tasca,
    editar_tasca,
    es_data_valida,
    etiqueta_venciment,
    llistar_tasques,
)


RUTA_SRC = Path(__file__).resolve().parent.parent / "src"


def ruta_temporal(tmp_path):
    """Retorna la ruta del fitxer JSON dins del directori temporal."""
    # La ruta temporal aïlla les proves del fitxer real del projecte.
    return tmp_path / "data" / "tasks.json"


def executar_cli(tmp_path, dades_inicials, *arguments):
    """Executa la CLI en una còpia temporal i retorna sortida i ruta JSON."""
    arrel = tmp_path / "projecte"
    (arrel / "src").mkdir(parents=True)
    (arrel / "data").mkdir()
    for nom in ("models.py", "tasks_app.py"):
        shutil.copy(RUTA_SRC / nom, arrel / "src" / nom)
    ruta_dades = arrel / "data" / "tasks.json"
    ruta_dades.write_text(json.dumps(dades_inicials, ensure_ascii=False), encoding="utf-8")
    resultat = subprocess.run(
        [sys.executable, str(arrel / "src" / "tasks_app.py"), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    return resultat, ruta_dades


def tasca_inicial(identificador=1, estat="pendent", data_limit=None):
    """Retorna una tasca de prova amb els valors dels escenaris GS-05 i GS-07."""
    return {
        "id": identificador,
        "titol": "Pràctica 1",
        "assignatura": "RS",
        "estat": estat,
        "data_limit": data_limit,
    }


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


def test_crear_tasca_amb_data_limit_valida(tmp_path):
    """GS-04: la data límit vàlida queda desada amb la tasca."""
    resultat, ruta = executar_cli(
        tmp_path, [], "add", "--title", "Lliurament SDD",
        "--subject", "RS", "--due", "2026-12-02",
    )

    assert resultat.returncode == 0
    assert resultat.stdout.strip() == "Tasca [ID: 1] creada amb èxit"
    assert json.loads(ruta.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Lliurament SDD",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-02",
        }
    ]


def test_rebutjar_data_limit_invalid(tmp_path):
    """RF-06: una data invàlida rebutja l'add sense desar la tasca."""
    resultat, ruta = executar_cli(
        tmp_path, [], "add", "--title", "Mala",
        "--subject", "RS", "--due", "02-12-2026",
    )

    assert "no és vàlida. Format esperat: YYYY-MM-DD" in resultat.stdout
    assert json.loads(ruta.read_text(encoding="utf-8")) == []


def test_editar_tasca_existent(tmp_path):
    """GS-05: l'edició actualitza el títol i la data límit persistits."""
    resultat, ruta = executar_cli(
        tmp_path, [tasca_inicial()], "edit", "--id", "1",
        "--title", "Pràctica 1 Refinada", "--due", "2026-12-10",
    )

    assert resultat.stdout.strip() == "Tasca [ID: 1] actualitzada amb èxit"
    assert json.loads(ruta.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1 Refinada",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-10",
        }
    ]


def test_editar_tasca_inexistent(tmp_path):
    """GS-06: un ID inexistent mostra l'error exacte i no modifica res."""
    dades = [tasca_inicial()]
    resultat, ruta = executar_cli(
        tmp_path, dades, "edit", "--id", "99", "--title", "Nova",
    )

    assert resultat.stdout.strip() == "Error: No s'ha trobat cap tasca amb ID 99"
    assert json.loads(ruta.read_text(encoding="utf-8")) == dades


def test_completar_tasca(tmp_path):
    """GS-07: complete posa l'estat a completada i ho desa."""
    resultat, ruta = executar_cli(
        tmp_path, [tasca_inicial()], "complete", "--id", "1",
    )

    assert resultat.stdout.strip() == "Tasca [ID: 1] marcada com a completada"
    assert json.loads(ruta.read_text(encoding="utf-8"))[0]["estat"] == "completada"


def test_completar_tasca_inexistent(tmp_path):
    """RF-08: complete amb un ID inexistent mostra el mateix error."""
    resultat, ruta = executar_cli(tmp_path, [], "complete", "--id", "99")

    assert resultat.stdout.strip() == "Error: No s'ha trobat cap tasca amb ID 99"
    assert json.loads(ruta.read_text(encoding="utf-8")) == []


def test_llistar_tasques_amb_etiquetes_davis(tmp_path, capsys):
    """GS-08: el llistat mostra la data límit i els avisos d'urgència."""
    ruta = ruta_temporal(tmp_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "titol": "Tasca antiga",
                    "assignatura": "RS",
                    "estat": "pendent",
                    "data_limit": "2026-11-20",
                },
                {
                    "id": 2,
                    "titol": "Tasca propera",
                    "assignatura": "SO",
                    "estat": "pendent",
                    "data_limit": "2026-11-27",
                },
                {
                    "id": 3,
                    "titol": "Tasca llunyana",
                    "assignatura": "BD",
                    "estat": "pendent",
                    "data_limit": "2026-12-15",
                },
                {
                    "id": 4,
                    "titol": "Tasca ja feta",
                    "assignatura": "RS",
                    "estat": "completada",
                    "data_limit": "2026-11-18",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    llistar_tasques(ruta, avui=date(2026, 11, 23))

    assert capsys.readouterr().out.splitlines() == [
        "[1] Tasca antiga (RS) - estat: pendent - límit: 2026-11-20 [CADUCADA]",
        "[2] Tasca propera (SO) - estat: pendent - límit: 2026-11-27 [URGENT]",
        "[3] Tasca llunyana (BD) - estat: pendent - límit: 2026-12-15",
        "[4] Tasca ja feta (RS) - estat: completada - límit: 2026-11-18",
    ]


@pytest.mark.parametrize(
    ("data_limit", "esperat"),
    [
        (None, True),
        ("2026-12-02", True),
        ("2026-02-30", False),
        ("02-12-2026", False),
        ("2026-12-2", False),
        ("", False),
    ],
)
def test_es_data_valida(data_limit, esperat):
    """Unitari: només s'accepten dates reals en format YYYY-MM-DD."""
    assert es_data_valida(data_limit) is esperat


def test_etiqueta_venciment():
    """Unitari: les etiquetes depenen de l'estat i dels dies restants."""
    avui = date(2026, 11, 23)
    casos = [
        ("2026-11-22", "pendent", " [CADUCADA]"),
        ("2026-11-23", "pendent", " [URGENT]"),
        ("2026-11-29", "pendent", " [URGENT]"),
        ("2026-11-30", "pendent", ""),
        ("2026-11-22", "completada", ""),
        (None, "pendent", ""),
    ]
    for data_limit, estat, esperat in casos:
        tasca = Task(1, "Tasca", "RS", estat, data_limit)
        assert etiqueta_venciment(tasca, avui) == esperat
