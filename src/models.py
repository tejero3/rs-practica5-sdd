import json
from dataclasses import asdict, dataclass


@dataclass
class Task:
    """Model d'una tasca acadèmica amb els camps del fitxer JSON."""

    id: int
    titol: str
    assignatura: str
    # Tota tasca nova es crea amb l'estat 'pendent'.
    estat: str = "pendent"
    # Data límit opcional en format YYYY-MM-DD; null si no s'indica.
    data_limit: str | None = None

    def to_dict(self) -> dict:
        """Retorna la tasca com a diccionari amb les claus del model."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialitza la tasca a JSON sense escapar els accents catalans."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dades: dict) -> "Task":
        """Construeix una tasca a partir de les claus catalanes del model."""
        # Les tasques antigues sense data_limit es llegeixen amb None.
        return cls(
            id=dades["id"],
            titol=dades["titol"],
            assignatura=dades["assignatura"],
            estat=dades.get("estat", "pendent"),
            data_limit=dades.get("data_limit"),
        )

    @classmethod
    def from_json(cls, text: str) -> "Task":
        """Deserialitza una cadena JSON i en construeix una tasca."""
        return cls.from_dict(json.loads(text))
