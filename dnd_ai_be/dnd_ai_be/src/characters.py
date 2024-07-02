from pymongo import MongoClient
from typing import List
import json
import os
from bson import ObjectId
from flask import Blueprint

character_blueprint = Blueprint('character_blueprint', __name__)

URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/?appName=Cluster91339"
CLIENT = MongoClient(URI)
DB_NAME = 'test_db'
DB = CLIENT[DB_NAME]



class Entity:
    '''
    An entity in the DnD world. Parent class of Character, NPC, and Player.

    This class has no local variables except for ID. All other CRUD operations are 
        handled by the database.
    '''
    def __init__(self, race:str=None, tags: List[str]=None, description: str=None, ID:ObjectId=None):
        ''' Initialize a new entity, either by creating a new entry in the database or by
        retrieving an existing entry. 
        This may be called with only the ID argument or with all arguments except ID.
        Ex: 
            Entity(ID=ObjectId('66808f6bef8163e460149f49'))
            Entity(race,tags,description)
        '''
        self.col = DB.Entities 

        if not ID is None:
            if self.col.find_one({"_id": ObjectId(ID)}) is None:
                raise ValueError("ID does not exist in database.")
            else:
                self.ID = ID
        else:
            ID = self._create_entity(race,tags,description)
            self.ID = ID

    def _create_entity(self, race, tags, description) -> ObjectId:
        entity_data = {
            'race': race,
            'tags': tags,
            'description': description
        }
        result = self.col.insert_one(entity_data)
        return result.inserted_id
    
    def get_race(self) -> str:
        return self.col.find_one({'_id': self.ID})['race']

    def set_race(self, race: str) -> None:
        self.col.update_one({'_id': self.ID}, {'$set': {'race': race}})

    def get_tags(self) -> List[str]:
        return self.col.find_one({'_id': self.ID})['tags']

    def set_tags(self, tags: List[str]) -> None:
        self.col.update_one({'_id': self.ID}, {'$set': {'tags': tags}})

    def get_description(self) -> str:
        return self.col.find_one({'_id': self.ID})['description']

    def set_description(self, description: str) -> None:
        self.col.update_one({'_id': self.ID}, {'$set': {'description': description}})
    
    def to_dict(self) -> dict:
        return self.col.find_one({'_id': self.ID})
    
    def get_context_str(self) -> str:
        ''' Returns a string representation of the entity for prompt context.
        '''
        context = f"Entity information: \nRace: {self.get_race()} \nTags: {self.get_tags()} \nDescription: {self.get_description()}"
        return context

class Character(Entity):
    '''
    A DnD Character. Parent class of NPCs and Players. Inherits from Entity.
    Each character has lore and memory. Memory is used to record in game events, 
    while lore is used for background information.

    This class is not instantiated directly. Instead, use NPC or Player.
    '''
    def __init__(self, race, tags, description, name, ID=None):
        ''' Initialize a new character.
        '''
        super().__init__(race=race, tags=tags, description=description)
        self.name = name
        self.lore = []
        self.memory = []
        

    def add_lore(self, lore_entry):
        """Adds a new lore entry to the person."""
        self.lore.append(lore_entry)
    
    def wipe_lore(self):
        """Wipes the lore of the person."""
        self.lore = []

    def add_memory(self, interaction):
        """Adds a new interaction to the person's memory."""
        self.memory.append(interaction)
    
    def wipe_memory(self):
        """Wipes the memory of the person."""
        self.memory = []

    def reset(self):
        """Resets the person's lore and memory."""
        self.wipe_lore()
        self.wipe_memory()

    def get_context_str(self) -> str:
        ''' Returns a string representation of the entity for prompt context.
        '''

        context = f"""Entity information:
            Race: {self.race}
            Tags: {self.tags}
            Description: {self.description}
            """
        return context
    
    
class NPC(Character):
    def __init__(self, role:str, name:str, race:str, tags:List[str], description:str):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.role = role  # Specific role of the NPC, e.g., merchant, guard, etc.


class Player(Character):
    def __init__(self, player_class:str, level:int , name:str, race:str, tags:List[str], description:str):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.player_class = player_class  # Class of the player, e.g., warrior, mage, etc.
        self.level = level  # Level of the player


if __name__ == '__main__':
    entity1 = Entity(race="Dragonborn", tags=["Friendly", "Mythical", "Dragon"], description="A majestic dragonborn warrior.")


    # SPEED TEST #
    # Test setters and getters
    print("Original entity:")
    print(f"Race: {entity1.get_race()}")
    print(f"Tags: {entity1.get_tags()}")
    print(f"Description: {entity1.get_description()}")

    for i in range(100):
        # Modify attributes using setters
        entity1.set_race(f"Elf{i}")
        entity1.set_tags([f"Graceful{i}", f"Forest{i}", f"Elf{i}"])
        entity1.set_description(f"An agile and wise elf of the forest.{i}")
        print('.', end='')

    # Test getters again after modification
    print("\nModified entity:")
    print(f"Race: {entity1.get_race()}")
    print(f"Tags: {entity1.get_tags()}")
    print(f"Description: {entity1.get_description()}")