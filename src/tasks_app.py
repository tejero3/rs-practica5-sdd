"""Aplicació de línia de comandes per gestionar tasques acadèmiques."""

import argparse
import json
import re
from datetime import date
from pathlib import Path

try:
    from models import Task
except ImportError:
    from src.models import Task

# El fitxer de dades es resol des de l'arrel del projecte, no del directori actual.
RUTA_DADES = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def carregar_tasques(ruta=RUTA_DADES):
    """Llegeix les tasques del JSON i el crea buit si encara no existeix."""
    if not ruta.exists():
        # RF-02: un fitxer inexistent s'inicialitza amb una llista buida.
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text("[]", encoding="utf-8")
        return []
    # Cada registre del fitxer es converteix en una instància de Task.
    return [Task.from_dict(dades) for dades in json.loads(ruta.read_text(encoding="utf-8"))]


def desar_tasques(tasques, ruta=RUTA_DADES):
    """Desa la llista de tasques al fitxer JSON de persistència."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    contingut = [tasca.to_dict() for tasca in tasques]
    # ensure_ascii=False conserva els accents dels títols i les assignatures.
    ruta.write_text(json.dumps(contingut, ensure_ascii=False, indent=2), encoding="utf-8")


def es_data_valida(data_limit):
    """Comprova que la data límit sigui real i segueixi el format YYYY-MM-DD."""
    if data_limit is None:
        return True
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data_limit):
        return False
    try:
        date.fromisoformat(data_limit)
    except ValueError:
        return False
    return True


def afegir_tasca(titol, assignatura, ruta=RUTA_DADES, data_limit=None):
    """Crea una tasca nova amb estat 'pendent' i la desa al registre."""
    # RF-06: una data invàlida rebutja l'operació abans de tocar el fitxer.
    if not es_data_valida(data_limit):
        print(f"Error: La data límit '{data_limit}' no és vàlida. Format esperat: YYYY-MM-DD")
        return None
    tasques = carregar_tasques(ruta)
    # L'identificador és superior al de totes les tasques emmagatzemades.
    identificador = max((tasca.id for tasca in tasques), default=0) + 1
    tasca = Task(id=identificador, titol=titol, assignatura=assignatura, data_limit=data_limit)
    tasques.append(tasca)
    desar_tasques(tasques, ruta)
    print(f"Tasca [ID: {tasca.id}] creada amb èxit")
    return tasca


def editar_tasca(identificador, titol=None, assignatura=None, estat=None,
                 data_limit=None, ruta=RUTA_DADES):
    """Modifica els atributs indicats d'una tasca identificada pel seu ID."""
    if not es_data_valida(data_limit):
        print(f"Error: La data límit '{data_limit}' no és vàlida. Format esperat: YYYY-MM-DD")
        return None
    tasques = carregar_tasques(ruta)
    tasca = next((t for t in tasques if t.id == identificador), None)
    if tasca is None:
        # RF-08: un ID inexistent mostra un error explícit i no desa res.
        print(f"Error: No s'ha trobat cap tasca amb ID {identificador}")
        return None
    if titol is not None:
        tasca.titol = titol
    if assignatura is not None:
        tasca.assignatura = assignatura
    if estat is not None:
        tasca.estat = estat
    if data_limit is not None:
        tasca.data_limit = data_limit
    desar_tasques(tasques, ruta)
    print(f"Tasca [ID: {identificador}] actualitzada amb èxit")
    return tasca


def llistar_tasques(ruta=RUTA_DADES):
    """Mostra per pantalla totes les tasques registrades o l'estat buit."""
    tasques = carregar_tasques(ruta)
    if not tasques:
        # GS-02: el registre sense tasques mostra un missatge explícit.
        print("Registre de tasques buit.")
        return
    for tasca in tasques:
        print(f"[{tasca.id}] {tasca.titol} ({tasca.assignatura}) - estat: {tasca.estat}")


def main(argv=None):
    """Configura la CLI i executa l'ordre add, edit o list sol·licitada."""
    analitzador = argparse.ArgumentParser(description="Gestiona les tasques acadèmiques.")
    comandes = analitzador.add_subparsers(dest="comanda", required=True)

    afegir = comandes.add_parser("add", help="Crea una nova tasca")
    afegir.add_argument("--title", required=True, help="Títol de la tasca")
    afegir.add_argument("--subject", required=True, help="Assignatura de la tasca")
    afegir.add_argument("--due", help="Data límit opcional en format YYYY-MM-DD")

    editar = comandes.add_parser("edit", help="Modifica els atributs d'una tasca")
    editar.add_argument("--id", type=int, required=True, help="Identificador de la tasca")
    editar.add_argument("--title", help="Nou títol de la tasca")
    editar.add_argument("--subject", help="Nova assignatura de la tasca")
    editar.add_argument("--status", dest="estat", help="Nou estat de la tasca")
    editar.add_argument("--due", dest="data_limit", help="Nova data límit YYYY-MM-DD")

    comandes.add_parser("list", help="Mostra totes les tasques registrades")

    arguments = analitzador.parse_args(argv)
    if arguments.comanda == "add":
        afegir_tasca(arguments.title, arguments.subject, data_limit=arguments.due)
    elif arguments.comanda == "edit":
        editar_tasca(
            arguments.id,
            titol=arguments.title,
            assignatura=arguments.subject,
            estat=arguments.estat,
            data_limit=arguments.data_limit,
        )
    elif arguments.comanda == "list":
        llistar_tasques()


if __name__ == "__main__":
    main()
