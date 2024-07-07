export interface EntityLike {
  _id: string;
  name: string;
  type: string;
}

export interface BotLike {
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

export interface Bot {
  _id?: string;
  name: string;
  contextualize_q_system_prompt: string;
  config: {
    model: string;
    temperature: number;
  };
}

export interface PromptData {
  userInput: string;
  prompter: EntityLike;
  responder: EntityLike;
  bot: BotLike;
}

export interface DropdownItem {
  value: string;
  text: string;
}
