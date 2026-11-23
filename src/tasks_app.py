"""Aplicació de línia de comandes per afegir i llistar tasques acadèmiques."""

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
    """Configura la CLI i executa l'ordre add o list sol·licitada."""
    analitzador = argparse.ArgumentParser(description="Gestiona les tasques acadèmiques.")
    comandes = analitzador.add_subparsers(dest="comanda", required=True)

    afegir = comandes.add_parser("add", help="Crea una nova tasca")
    afegir.add_argument("--title", required=True, help="Títol de la tasca")
    afegir.add_argument("--subject", required=True, help="Assignatura de la tasca")
    afegir.add_argument("--due", help="Data límit opcional en format YYYY-MM-DD")

    comandes.add_parser("list", help="Mostra totes les tasques registrades")

    arguments = analitzador.parse_args(argv)
    if arguments.comanda == "add":
        afegir_tasca(arguments.title, arguments.subject, data_limit=arguments.due)
    elif arguments.comanda == "list":
        llistar_tasques()


if __name__ == "__main__":
    main()
