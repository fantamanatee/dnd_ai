from pymongo import MongoClient
from typing import List
import json
import os
from bson import ObjectId
from flask import Blueprint

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
            data = {
                'race': race,
                'tags': tags,
                'description': description
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id        
    
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
        context = f"Entity information:\n\nRace: {self.get_race()} \nTags: {self.get_tags()} \nDescription: {self.get_description()}"
        return context


class Character(Entity):
    '''
    A DnD Character. Parent class of NPCs and Players. Inherits from Entity.
    Each character has lore. Lore is used for background information, and can be updated as the game progresses.

    This class is not instantiated directly. Instead, use Entity, NPC, or Player.
    '''

    col = None # no defined Character collection. Placeholder for child classes.
    ID = None # no defined ID. Placeholder for child classes.
        
    def add_lore(self, lore_entry: str) -> None:
        self.col.update_one(
            {'_id': self.ID},
            {'$push': {'lore': lore_entry}}
        )
    
    def wipe_lore(self) -> None:
        self.col.update_one(
            {'_id': self.ID},
            {'$set': {'lore': []}}
        )
    
    def get_lore(self) -> List[str]:
        return self.col.find_one({'_id': self.ID}).get('lore', [])

    
class NPC(Character):
    def __init__(self, role:str, name:str, race:str, tags:List[str], description:str, ID:ObjectId=None):
        '''
        Initialize a new NPC, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex: 
            NPC(ID=ObjectId('66808f6bef8163e460149f49'))
            NPC(role, name, race, tags, description)
        '''
        self.col = DB.NPC 

        if not ID is None:
            obj = self.col.find_one({"_id": ObjectId(ID)})
            if obj is None:
                raise ValueError("ID does not exist in database.")
            self.ID = ID
        else:
            data = {
                'role': role,
                'name': name,
                'race': race,
                'tags': tags,
                'description': description,
                'lore': []
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id

    def get_role(self) -> str:
        return self.col.find_one({'_id': self.ID}).get('role', [])

    def get_name(self) -> str:
        return self.col.find_one({'_id': self.ID}).get('name', [])
    
    def get_context_str(self) -> str:
        ''' Returns a string representation of the npc for prompt context.
        '''
        context = f"NPC information:\n\nRole: {self.get_role()}\nName: {self.get_name()}\nRace: {self.get_race()}\nTags: {self.get_tags()}\nDescription: {self.get_description()}\nLore: {self.get_lore()}"
        return context


class Player(Character):
    def __init__(self, player_class:str, level:int , name:str, race:str, tags:List[str], description:str, ID:ObjectId=None):
        '''
        Initialize a new Player, either by creating a new entry in the database or by
        retrieving an existing entry.
        This may be called with only the ID argument or with all arguments except ID.
        Ex: 
            Player(ID=ObjectId('66808f6bef8163e460149f49'))
            Player(player_class, level, name, race, tags, description)
        '''
        self.col = DB.Player 

        if not ID is None:
            obj = self.col.find_one({"_id": ObjectId(ID)})
            if obj is None:
                raise ValueError("ID does not exist in database.")
            self.ID = ID
        else:
            data = {
                'player_class': player_class,
                'level': level,
                'name': name,
                'race': race,
                'tags': tags,
                'description': description,
                'lore': []
            }
            result = self.col.insert_one(data)
            self.ID = result.inserted_id

    def get_player_class(self) -> str:
        return self.col.find_one({'_id': self.ID}).get('player_class', [])
    
    def get_level(self) -> int:
        return self.col.find_one({'_id': self.ID}).get('level', [])
    
    def get_name(self) -> str:
        return self.col.find_one({'_id': self.ID}).get('name', [])
    
    def get_context_str(self) -> str:
        ''' Returns a string representation of the player for prompt context.
        '''
        context = f"Player information:\n\nPlayer Class: {self.get_player_class()}\nLevel: {self.get_level()}\nName: {self.get_name()}\nRace: {self.get_race()}\nTags: {self.get_tags()}\nDescription: {self.get_description()}\nLore: {self.get_lore()}"
        return context


if __name__ == '__main__':
    npc = NPC(role="Merchant", name="Gim", race="Halfling", tags=["Friendly", "Trader"], description="A jovial halfling merchant.")
    npc.add_lore("Gim is known for his excellent prices. His brother is a famous bard who writes songs about their adventures.")
    npc.add_lore("Gim has a secret stash of rare items hidden in his shop.")
    print(npc.get_lore())
    print(npc.get_context_str())
    npc.wipe_lore()
    print(npc.get_lore())

    player = Player(player_class="Wizard", level=5, name="El", race="Elf", tags=["Adventurer"], description="A wise elven wizard.")
    player.add_lore("El is a member of the Arcane Order, a group of powerful wizards who protect the realm.")
    player.add_lore("El is searching for a lost artifact that could change the course of history.")
    print(player.get_lore())
    print(player.get_context_str())
    player.wipe_lore()
    print(player.get_lore())
    
    # entity1 = Entity(race="Dragonborn", tags=["Friendly", "Mythical", "Dragon"], description="A majestic dragonborn warrior.")


    # # SPEED TEST #
    # # Test setters and getters
    # print("Original entity:")
    # print(f"Race: {entity1.get_race()}")
    # print(f"Tags: {entity1.get_tags()}")
    # print(f"Description: {entity1.get_description()}")

    # for i in range(100):
    #     # Modify attributes using setters
    #     entity1.set_race(f"Elf{i}")
    #     entity1.set_tags([f"Graceful{i}", f"Forest{i}", f"Elf{i}"])
    #     entity1.set_description(f"An agile and wise elf of the forest.{i}")
    #     print('.', end='')

    # # Test getters again after modification
    # print("\nModified entity:")
    # print(f"Race: {entity1.get_race()}")
    # print(f"Tags: {entity1.get_tags()}")
    # print(f"Description: {entity1.get_description()}")