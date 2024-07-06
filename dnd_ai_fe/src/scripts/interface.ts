export interface EntityLike {
  _id: string;
  name: string;
  type: string;
}

export interface Entity {
  _id?: string;
  race: string;
  tags: string[];
  description: string;
}

export interface NPC extends Entity {
  role: string;
  lore: string[];
  name: string;
}

export interface Player extends Entity {
  player_class: string;
  level: number;
  name: string;
  lore: string[];
}

export interface PromptData {
  userInput: string;
  prompter: EntityLike;
  responder: EntityLike;
}

export interface DropdownItem {
  value: string;
  text: string;
}