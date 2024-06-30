from typing import List

class Entity:
    '''
    An entity in the DnD world. Parent class of Character, NPC, and Player.
    '''
    def __init__(self, race:str, tags:List[str], description:str):
        self.race = race
        self.tags = tags
        self.description = description
    
    def get_description(self):
        ''' Get the description of the entity.
        '''
        return self.description
    
    def get_tags(self):
        ''' Get the tags of the entity.
        '''
        return self.tags
    
    def get_race(self):
        ''' Get the race of the entity.
        ''' 
        return self.race

    def __str__(self):
        """Returns a string representation of the entity."""
        return f"Race: {self.race}, Tags: {self.tags}, Description: {self.description[:50]}"

    def to_dict(self):
        ''' Convert the entity to a dictionary.
        '''
        return vars(self)

class Character(Entity):
    '''
    A DnD Character. Parent class of NPCs and Players. Inherits from Entity.
    Each character has lore and memory. Memory is used to record in game events, 
    while lore is used for background information.

    This class is not instantiated directly. Instead, use NPC or Player.
    '''
    def __init__(self, name, race, tags, description):
        ''' Initialize a new character.
        '''
        super().__init__(race=race, tags=tags, description=description)
        self.name = name
        self.lore = ""
        self.memory = []

    def add_lore(self, lore_entry):
        """Adds a new lore entry to the person."""
        self.lore.append(lore_entry)

    def get_lore(self):
        """Returns the compiled lore of the person."""
        return " ".join(self.lore)
    
    def wipe_lore(self):
        """Wipes the lore of the person."""
        self.lore = []

    def add_memory(self, interaction):
        """Adds a new interaction to the person's memory."""
        self.memory.append(interaction)

    def get_memory(self):
        """Returns the compiled memory of the person."""
        return " ".join(self.memory)
    
    def wipe_memory(self):
        """Wipes the memory of the person."""
        self.memory = []

    def reset(self):
        """Resets the person's lore and memory."""
        self.wipe_lore()
        self.wipe_memory()

    def __str__(self):
        """Returns a string representation of the person."""
        return f"Name: {self.name}, {super().__str__()}"
    
    
class NPC(Character):
    def __init__(self, role:str, name:str, race:str, tags:List[str], description:str):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.role = role  # Specific role of the NPC, e.g., merchant, guard, etc.

    def __str__(self):
        """Returns a string representation of the NPC."""
        return f"NPC {super().__str__()}, Role: {self.role}"


class Player(Character):
    def __init__(self, player_class:str, level:int , name:str, race:str, tags:List[str], description:str):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.player_class = player_class  # Class of the player, e.g., warrior, mage, etc.
        self.level = level  # Level of the player

    def __str__(self):
        """Returns a string representation of the player."""
        return f"Player {super().__str__()}, Class: {self.player_class}, Level: {self.level}"


