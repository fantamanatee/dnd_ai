from langchain.schema import Document
from langchain_community.document_loaders.mongodb import MongodbLoader
import json
from typing import Iterable
from dnd_ai_be.src.characters import *


def save_docs_to_jsonl(array: Iterable[Document], file_path: str) -> None:
    """Save a list of Document objects to a JSONL file."""
    with open(file_path, "w") as jsonl_file:
        for doc in array:
            jsonl_file.write(doc.json() + "\n")


def load_docs_from_jsonl(file_path) -> Iterable[Document]:
    """Load a list of Document objects from a JSONL file."""
    array = []
    with open(file_path, "r") as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            obj = Document(**data)
            array.append(obj)
    return array


def entity_like_to_context_str(entity_like: EntityLike) -> str:
    """Returns a string representation of the entity_like for prompt context."""

    # name, player_class, level, role, race, tags, description, stats, lore =
    entity_like_dict = entity_like.to_dict()

    context_string = ""

    order = [
        "name",
        "race",
        "tags",
        "description",
        "stats",
        "lore",
        "role",
        "player_class",
        "level",
    ]

    for key in order:
        if key in entity_like_dict:
            value = entity_like_dict[key]
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            context_string += f"{key}: {value}\n"
        else:
            context_string += f"{key}: N/A\n"

    context_string = context_string.strip()
    # print(context_string)
    # print()

    return context_string


if __name__ == "__main__":
    player_elowen = Player(ID="66aa7c905b9452034bd1256a")
    entity_dragonborn = Entity(ID="66aa7c905b9452034bd1256f")
    npc_mabel = NPC(ID="66aa7c905b9452034bd12567")

    entity_like_to_context_str(player_elowen)
    entity_like_to_context_str(entity_dragonborn)
    entity_like_to_context_str(npc_mabel)
