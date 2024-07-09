import { DropdownItem, EntityLike, Entity, NPC, Player, Bot } from "./interface";

export function populateAppendDropdown(
  dropdown: HTMLSelectElement,
  items: DropdownItem[],
) {
  items.forEach((item: DropdownItem) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.text = item.text;
    dropdown.add(option);
  });
}

export function convertToDropdownItem(obj: any): DropdownItem {
  return {
    value: obj._id,
    text: obj.name,
  };
}

export function convertToDropdownItems(
  entityLikes: EntityLike[]
): DropdownItem[] {
  return entityLikes.map((entity) => ({
    value: entity._id,
    text: `${entity.type}: ${entity.name}`,
  }));
}

/**
 * Validates if an object conforms to the Entity interface.
 * @param {any} obj - The object to validate.
 * @returns {Entity} - The validated Entity.
 * @throws Will throw an error if validation fails.
 */
export function validateEntity(obj: any): Entity {
  if (
    obj &&
    typeof obj.race === 'string' &&
    Array.isArray(obj.tags) &&
    obj.tags.every((tag: any) => typeof tag === 'string') &&
    typeof obj.description === 'string'
  ) {
    return obj as Entity;
  } else {
    throw new Error('Invalid Entity format.');
  }
}

/**
 * Validates if an object conforms to the NPC interface.
 * @param {any} obj - The object to validate.
 * @returns {NPC} - The validated NPC.
 * @throws Will throw an error if validation fails.
 */
export function validateNPC(obj: any): NPC {
  const entity = validateEntity(obj);
  if (
    entity &&
    typeof obj.name === 'string' &&
    typeof obj.role === 'string' &&
    Array.isArray(obj.lore) &&
    obj.lore.every((item: any) => typeof item === 'string')
  ) {
    return obj as NPC;
  } else {
    throw new Error('Invalid NPC format.');
  }
}

/**
 * Validates if an object conforms to the Player interface.
 * @param {any} obj - The object to validate.
 * @returns {Player} - The validated Player.
 * @throws Will throw an error if validation fails.
 */
export function validatePlayer(obj: any): Player {
  const entity = validateEntity(obj);
  if (
    entity &&
    typeof obj.name === 'string' &&
    typeof obj.player_class === 'string' &&
    typeof obj.level === 'number'
  ) {
    return obj as Player;
  } else {
    throw new Error('Invalid Player format.');
  }
}
/**
 * Validates if an object conforms to the Bot interface.
 * @param {any} obj - The object to validate.
 * @returns {Bot} - The validated Entity.
 * @throws Will throw an error with specific type check failures if validation fails.
 */
export function validateBot(obj: any): Bot {
  if (!obj) throw new Error('Invalid Bot format: Missing object');
  if (typeof obj.name !== 'string') throw new Error('Invalid Bot format: name must be a string');
  if (typeof obj.contextualize_q_system_prompt !== 'string') throw new Error('Invalid Bot format: contextualize_q_system_prompt must be a string');
  if (typeof obj.qa_system_prompt !== 'string') throw new Error('Invalid Bot format: qa_system_prompt must be a string');
  if (typeof obj.config !== 'object') throw new Error('Invalid Bot format: config must be an object');
  if (typeof obj.config.model !== 'string') throw new Error('Invalid Bot format: config.model must be a string');
  if (typeof obj.config.temperature !== 'number') throw new Error('Invalid Bot format: config.temperature must be a number');
  return obj as Bot;
}

