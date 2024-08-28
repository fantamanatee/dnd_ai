from pymongo import MongoClient
from typing import List, Union
from bson import ObjectId
from dnd_ai_be.src.db_util import DB


class EntityLike:
    """
    An entity in the DnD world. Parent class of Character, NPC, and Player.

    This class does not interface with the DB
    """

    def __init__(
        self,
        race: str = None,
        tags: List[str] = [],
        description: str = None,
        stats: Union[dict, str] = None,
        ID: str = None,
    ):
        """Initialize a new entity, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex:
            Entity(ID=ObjectId('66808f6bef8163e460149f49'))
            Entity(race,tags,description)
        """

        self.race = race
        self.tags = tags
        self.description = description
        self.stats = stats
        self.ID = ID
        self.col = None  # Placeholder for collection

        if stats is None:
            self.stats = {
                "strength": 0,
                "dexterity": 0,
                "constitution": 0,
                "intelligence": 0,
                "wisdom": 0,
                "charisma": 0,
            }

        elif stats == "average":
            self.stats = {
                "strength": 12,
                "dexterity": 12,
                "constitution": 12,
                "intelligence": 12,
                "wisdom": 12,
                "charisma": 12,
            }
        else:
            assert all(
                [
                    stat in stats.keys()
                    for stat in [
                        "strength",
                        "dexterity",
                        "constitution",
                        "intelligence",
                        "wisdom",
                        "charisma",
                    ]
                ]
            ), "Stats must include all 6 ability scores."
            self.stats = stats

    def get_name(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("name", "unknown")

    def set_name(self, name: str) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"name": name}})

    def get_race(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("race", "unknown")

    def set_race(self, race: str) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"race": race}})

    def get_tags(self) -> List[str]:
        return self.col.find_one({"_id": self.ID}).get("tags", [])

    def set_tags(self, tags: List[str]) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"tags": tags}})

    def get_description(self) -> str:
        return self.col.find_one({"_id": self.ID}).get(
            "description", "No description available."
        )

    def set_description(self, description: str) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"description": description}})

    def get_stats(self) -> dict:
        return self.col.find_one({"_id": self.ID}).get("stats", {})

    def set_stats(self, stats: dict) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"stats": stats}})

    def to_dict(self, show_id=False) -> dict:
        return self.col.find_one({"_id": self.ID}, {"_id": show_id})

    # def get_context_str(self) -> str:
    #     """Returns a string representation of the entity for prompt context."""
    #     pass


class Entity(EntityLike):
    """
    An entity in the DnD world. Parent class of Character, NPC, and Player.

    This class has no local variables except for ID. All other CRUD operations are
        handled by the database.
    """

    def __init__(
        self,
        race: str = None,
        tags: List[str] = [],
        description: str = None,
        stats: Union[dict, str] = None,
        ID: str = None,
    ):
        """Initialize a new entity, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex:
            Entity(ID=ObjectId('66808f6bef8163e460149f49'))
            Entity(race,tags,description)
        """

        super().__init__(race, tags, description, stats, ID)

        ID = ObjectId(ID) if ID else None
        self.col = DB.Entities

        if not ID is None:
            if self.col.find_one({"_id": ID}) is None:
                raise ValueError(
                    f"ID {ID} does not exist in {self.col.database.name}.{self.col.name}."
                )
            else:
                self.ID = ID
        else:
            data = {
                "name": f"{race}1",
                "race": race,
                "tags": tags,
                "description": description,
                "stats": self.stats,
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id


class Character:
    """
    A DnD Character. Parent class of NPCs and Players. Inherits from Entity.
    Each character has lore. Lore is used for background information, and can be updated as the game progresses.

    This class is not instantiated directly. Instead, use Entity, NPC, or Player.
    """

    col = None  # no defined Character collection. Placeholder for child classes.
    ID = None  # no defined ID. Placeholder for child classes.

    def add_lore(self, lore_entry: str) -> None:
        self.col.update_one({"_id": self.ID}, {"$push": {"lore": lore_entry}})

    def wipe_lore(self) -> None:
        self.col.update_one({"_id": self.ID}, {"$set": {"lore": []}})

    def get_lore(self) -> List[str]:
        return self.col.find_one({"_id": self.ID}).get("lore", [])


class NPC(Character, EntityLike):
    def __init__(
        self,
        role: str = None,
        name: str = None,
        lore: List[str] = [],
        race: str = None,
        tags: List[str] = [],
        description: str = None,
        stats: Union[dict, str] = None,
        ID: str = None,
    ):
        """
        Initialize a new NPC, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex:
            NPC(ID=ObjectId('66808f6bef8163e460149f49'))
            NPC(role, name, lore, race, tags, description)
        """
        ID = ObjectId(ID) if ID else None
        self.col = DB.NPCs

        if not ID is None:
            obj = self.col.find_one({"_id": ID})
            if obj is None:
                raise ValueError(
                    f"ID {ID} does not exist in {self.col.database.name}.{self.col.name}."
                )
            self.ID = ID
        else:
            data = {
                "role": role,
                "name": name,
                "race": race,
                "tags": tags,
                "description": description,
                "stats": stats,
                "lore": lore,
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id

    def get_role(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("role", "unknown")

    def get_name(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("name", "unknown")

    # def get_context_str(self) -> str:
    #     """Returns a string representation of the npc for prompt context."""
    #     context = f"NPC information:\nRole: {self.get_role()}\nName: {self.get_name()}\nRace: {self.get_race()}\nTags: {self.get_tags()}\nDescription: {self.get_description()} \nStats: {self.get_stats()} \nLore: {self.get_lore()}"
    #     return context


class Player(Character, EntityLike):
    def __init__(
        self,
        player_class: str = None,
        level: int = None,
        name: str = None,
        lore: List[str] = [],
        race: str = None,
        tags: List[str] = [],
        description: str = None,
        stats: Union[dict, str] = None,
        ID: str = None,
    ):
        """
        Initialize a new Player, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex:
            Player(ID=ObjectId('66808f6bef8163e460149f49'))
            Player(player_class, level, name, lore, race, tags, description)
        """
        ID = ObjectId(ID) if ID else None
        self.col = DB.Players

        if not ID is None:
            obj = self.col.find_one({"_id": ID})
            if obj is None:
                raise ValueError(
                    f"ID {ID} does not exist in {self.col.database.name}.{self.col.name}."
                )
            self.ID = ID
        else:
            data = {
                "player_class": player_class,
                "level": level,
                "name": name,
                "race": race,
                "tags": tags,
                "description": description,
                "stats": stats,
                "lore": lore,
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id

    def get_player_class(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("player_class", "unknown")

    def get_level(self) -> int:
        return self.col.find_one({"_id": self.ID}).get("level", "unknown")

    def get_name(self) -> str:
        return self.col.find_one({"_id": self.ID}).get("name", "unknown")

    # def get_context_str(self) -> str:
    #     """Returns a string representation of the player for prompt context."""
    #     context = f"Player information:\nPlayer Class: {self.get_player_class()}\nLevel: {self.get_level()}\nName: {self.get_name()}\nRace: {self.get_race()}\nTags: {self.get_tags()}\nDescription: {self.get_description()} \nStats: {self.get_stats()} \nLore: {self.get_lore()}"
    #     return context


entity_like_classes = {"Entity": Entity, "NPC": NPC, "Player": Player}

# if __name__ == "__main__":
#     pass

#     # Example Entity
#     example_entity = Entity(
#         race="Orc",
#         tags=["Hostile"],
#         description="A brutish, aggressive, ugly, and malevolent monster",
#         stats={
#             "strength": 16,
#             "dexterity": 10,
#             "constitution": 14,
#             "intelligence": 7,
#             "wisdom": 8,
#             "charisma": 6,
#         },
#     )

#     print(example_entity.get_context_str())

#     # Example Player
#     example_player = Player(
#         player_class="Ranger",
#         level=5,
#         name="Legolas",
#         lore=[
#             "Trained in the art of archery from a young age",
#             "Guardian of the forest",
#         ],
#         race="Elf",
#         tags=["Friendly", "Archer", "Stealthy"],
#         description="A skilled archer with a knack for stealth and agility.",
#         stats={
#             "strength": 12,
#             "dexterity": 18,
#             "constitution": 14,
#             "intelligence": 14,
#             "wisdom": 16,
#             "charisma": 10,
#         },
#     )
#     print(example_player.get_context_str())

#     example_npc = NPC(
#         role="Scout",
#         name="Gobbo",
#         lore=[
#             "Known to ambush travelers",
#             "Has a network of tunnels",
#         ],
#         race="Goblin",
#         tags=["Hostile", "Cunning"],
#         description="A small, green creature known for his cunning and mischief.",
#         stats={
#             "strength": 8,
#             "dexterity": 16,
#             "constitution": 10,
#             "intelligence": 12,
#             "wisdom": 10,
#             "charisma": 8,
#         },
#     )
#     print(example_player.get_context_str())
