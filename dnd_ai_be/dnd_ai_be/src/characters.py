class Character:
    '''
    A DnD Character. Parent class of NPCs and Players.
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
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
        return f"Name: {self.name}, Description: {self.description}"
    
    
class NPC(Character):
    def __init__(self, name, description, role):
        super().__init__(name, description)
        self.role = role  # Specific role of the NPC, e.g., merchant, guard, etc.

    def __str__(self):
        """Returns a string representation of the NPC."""
        return f"NPC {super().__str__()}, Role: {self.role}"


class Player(Character):
    def __init__(self, name, description, player_class, level):
        super().__init__(name, description)
        self.player_class = player_class  # Class of the player, e.g., warrior, mage, etc.
        self.level = level  # Level of the player

    def __str__(self):
        """Returns a string representation of the player."""
        return f"Player {super().__str__()}, Class: {self.player_class}, Level: {self.level}"
