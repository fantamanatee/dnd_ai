class Entity:
    '''
    An entity in the DnD world. Parent class of Character, NPC, and Player.
    '''
    def __init__(self, race, tags, description):
        self.race = race
        self.tags = tags
        self.description = description

    def __str__(self):
        """Returns a string representation of the entity."""
        return f"Race: {self.race}, Tags: {self.tags}, Description: {self.description[:50]}"

class Character(Entity):
    '''
    A DnD Character. Parent class of NPCs and Players. Inherits from Entity.

    This class is not instantiated directly. Instead, use NPC or Player.
    '''
    def __init__(self, name, race, tags, description):
        super().__init__(race=race, tags=tags, description=description)
        self.name = name
        self.lore = []
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
    def __init__(self, role, name, race, tags, description):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.role = role  # Specific role of the NPC, e.g., merchant, guard, etc.

    def __str__(self):
        """Returns a string representation of the NPC."""
        return f"NPC {super().__str__()}, Role: {self.role}"


class Player(Character):
    def __init__(self, player_class, level, name, race, tags, description):
        super().__init__(name=name, race=race, tags=tags, description=description)
        self.player_class = player_class  # Class of the player, e.g., warrior, mage, etc.
        self.level = level  # Level of the player

    def __str__(self):
        """Returns a string representation of the player."""
        return f"Player {super().__str__()}, Class: {self.player_class}, Level: {self.level}"


if __name__ == '__main__':
    # Example NPCs
    npc1 = NPC(role="Merchant", name="Gimble", race="Halfling", tags=["Trader"], description="A jovial halfling merchant.")
    npc2 = NPC(role="Guard", name="Thorn", race="Human", tags=["Guard", "City Watch"], description="A vigilant human guard.")

    # Example Players
    player1 = Player(player_class="Wizard", level=5, name="Elowen", race="Elf", tags=["Adventurer"], description="A wise elven wizard.")
    player2 = Player(player_class="Fighter", level=3, name="Garrick", race="Human", tags=["Mercenary"], description="A skilled human fighter.")

    # Example Entities
    entity1 = Entity(race="Dragonborn", tags=["Mythical", "Dragon"], description="A majestic dragonborn warrior.")
    entity2 = Entity(race="Human", tags=["Commoner"], description="A humble human villager.")

    for entity in [npc1, npc2, player1, player2, entity1, entity2]:
        print(entity)
        print()