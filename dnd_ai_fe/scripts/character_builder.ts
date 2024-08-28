import axios from "axios";

import { API_ENDPOINTS } from "./config";
import {
  populateAppendDropdown,
  validateEntity,
  validateNPC,
  validatePlayer,
} from "./util";
import { Entity, NPC, Player, DropdownItem } from "./interface";

export function renderCharacterBuilder() {
  const mainContent = document.getElementById("main-content");
  // Assuming this part is within your script where you update the mainContent
  if (mainContent) {
    mainContent.innerHTML = `
        <section id="character-builder">
            <h2>Character Builder</h2>
            <div>
                <label for="entityLikeTypeSelect">Character Type:</label>
                <select id="entityLikeTypeSelect">
                    <option value="">Select Character Type</option>
                </select>
            </div>

            <label for="userInput">Enter Entity Data:</label>
            <textarea id="userInput"></textarea>

            <button id="createCharacterButton">Create Character</button>

            <div id="response"></div>



            <!-- ^ Display JSON output here -->
        </section>
    `;
  }
  setupCharacterBuilder();
}

const exampleEntity: Entity = {
  race: "Orc",
  tags: ["Hostile"],
  description: "A brutish, aggressive, ugly, and malevolent monster",
  stats:{
    strength: 16,
    dexterity: 10,
    constitution: 14,
    intelligence: 7,
    wisdom: 8,
    charisma: 6
  }
};
const examplePlayer: Player = {
  name: "Legolas",
  race: "Elf",
  tags: ["Archer", "Stealthy"],
  description: "A skilled archer with a knack for stealth and agility.",
  player_class: "Ranger",
  level: 5,
  lore: [
    "Trained in the art of archery from a young age",
    "Guardian of the forest",
  ],
  stats: {
    strength: 12,
    dexterity: 18,
    constitution: 14,
    intelligence: 14,
    wisdom: 16,
    charisma: 10
  },
};
const exampleNPC: NPC = {
  name: "Gobbo",
  race: "Goblin",
  tags: ["Enemy", "Cunning"],
  description: "A small, green creature known for his cunning and mischief.",
  role: "Scout",
  lore: ["Known to ambush travelers", "Has a network of tunnels"],
  stats: {
    strength: 8,
    dexterity: 16,
    constitution: 10,
    intelligence: 12,
    wisdom: 10,
    charisma: 8
  },
};

async function loadEntityLikeTypeSelect() {
  const entityTypeDropdown = document.getElementById(
    "entityLikeTypeSelect"
  ) as HTMLSelectElement;
  if (entityTypeDropdown) {
    entityTypeDropdown.innerHTML = "";
    const options = ["Entity", "NPC", "Player"];
    const dropdownItems: DropdownItem[] = options.map((option) => ({
      value: option.toLowerCase(),
      text: option,
    }));
    populateAppendDropdown(entityTypeDropdown, dropdownItems);
  } else {
    console.error("Dropdown with ID entityLikeTypeDropdown not found.");
  }
}

export async function sendConstructEntity(data: Entity): Promise<string> {
  try {
    const response = await axios.post(API_ENDPOINTS.ENTITY, data);
    return response.data.message;
  } catch (error) {
    console.error("Error constructing entity:", error);
    throw error;
  }
}

export async function sendConstructNPC(data: NPC): Promise<string> {
  try {
    const response = await axios.post(API_ENDPOINTS.NPC, data);
    return response.data.message;
  } catch (error) {
    console.error("Error constructing NPC:", error);
    throw error;
  }
}

export async function sendConstructPlayer(data: Player): Promise<string> {
  try {
    const response = await axios.post(API_ENDPOINTS.PLAYER, data);
    return response.data.message;
  } catch (error) {
    console.error("Error constructing player:", error);
    throw error;
  }
}

// Array to store the most recent JSON outputs
const recentOutputs: string[] = [];

// Function to update the response div
function updateResponseDiv(response: string) {
  recentOutputs.unshift(JSON.stringify(response, null, 2)); // Add the new output to the beginning of the array
  if (recentOutputs.length > 5) {
    recentOutputs.pop(); // Keep only the 5 most recent outputs
  }
  const responseDiv = document.getElementById("response");
  if (responseDiv) {
    responseDiv.innerHTML = recentOutputs
      .map((output) => `<pre>${output}</pre>`)
      .join("");
  }
}

export async function handleSendCreateCharacter(): Promise<void> {
  const userInput = document.getElementById("userInput") as HTMLTextAreaElement;
  const entityLikeTypeSelect = document.getElementById(
    "entityLikeTypeSelect"
  ) as HTMLSelectElement;
  const selectedType = entityLikeTypeSelect.selectedOptions[0].value;
  let response;
  try {
    if (selectedType === "entity") {
      const entity = validateEntity(JSON.parse(userInput.value));
      response = await sendConstructEntity(entity);
    } else if (selectedType === "npc") {
      const npc = validateNPC(JSON.parse(userInput.value));
      response = await sendConstructNPC(npc);
    } else if (selectedType === "player") {
      const plaver = validatePlayer(JSON.parse(userInput.value));
      response = await sendConstructPlayer(plaver);
    } else {
      console.error("Invalid Entity Type selected.");
      return;
    }
  } catch (error) {
    console.error(error);
    userInput.value = JSON.stringify(exampleEntity, null, 2); // reset to example entity
    response = "Invalid input for " + selectedType + ". Try again."; // Corrected concatenation
  }
  updateResponseDiv(response!);
}

function setupCharacterBuilder() {

  const entityLikeTypeSelect = document.getElementById("entityLikeTypeSelect") as HTMLSelectElement;
  const userInput = document.getElementById("userInput") as HTMLTextAreaElement;

  loadEntityLikeTypeSelect();
  entityLikeTypeSelect.addEventListener("change", function() {
    switch (entityLikeTypeSelect.value) {
        case "entity":
            userInput.value = JSON.stringify(exampleEntity, null, 2);
            break;
        case "npc":
            userInput.value = JSON.stringify(exampleNPC, null, 2);
            break;
        case "player":
            userInput.value = JSON.stringify(examplePlayer, null, 2);
            break;
        default:
            console.error("Invalid Entity Type selected.");
    }
  });

  userInput.value = JSON.stringify(exampleEntity, null, 2);

  const createCharacterButton = document.getElementById(
    "createCharacterButton"
  );
  if (createCharacterButton) {
    createCharacterButton.addEventListener("click", () => {
      handleSendCreateCharacter();
    });
  } else {
    console.error('Button with id="createCharacterButton" not found.');
  }
}
