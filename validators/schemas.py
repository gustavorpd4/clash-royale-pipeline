#VALIDADOR DE JSON

from pydantic import BaseModel, ValidationError
from typing import Optional
import json

class Card(BaseModel):
    name: str
    id: int
    maxLevel: int
    maxEvolutionLevel: Optional[int] = None
    elixirCost: Optional[int] = None
    rarity: str

def validar_carta(data: dict):
    try:
        carta = Card(**data)
        return carta, None
    except ValidationError as e:
        return None, e

def validar_lista(lista_dict:list   ):
    validas = []
    rechazadas = []
    for item in lista_dict:
        carta, error = validar_carta(item)
        if error:
            rechazadas.append({"data":item, "error": error})
        else:
            validas.append(carta)
    return validas, rechazadas


if __name__ == "__main__":
    data = json.load(open("tests/mock_card.json"))["items"]
    validas, rechazadas = validar_lista(data)
    print(f"Validas: {len(validas)}")
    print(f"Rechazadas: {len(rechazadas)}")