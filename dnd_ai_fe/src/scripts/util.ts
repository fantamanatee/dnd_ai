import { DropdownItem, EntityLike, Entity, NPC, Player } from "./interface";

export function populateAppendDropdown(
  dropdown: HTMLSelectElement,
  items: DropdownItem[],
) {
  console.log("populateAppendDropdown called");
  console.log("items:", items);
  items.forEach((item: DropdownItem) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.text = item.text;
    dropdown.add(option);
  });
}

export function convertToDropdownItem(entity: EntityLike): DropdownItem {
  return {
    value: entity._id,
    text: entity.name,
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
