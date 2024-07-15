import {
  populateAppendDropdown,
  convertToDropdownItems,
  DialogueHandler,
} from "./util";
import { EntityLike, PromptData, DropdownItem, Bot } from "./interface";
import { API_ENDPOINTS } from "./config";
import { send } from "process";

const dialogueHandler = new DialogueHandler();

// RENDERING //////////////////////////////////////////

/**
 * Renders the home page and then calls setupHome.
 */
export function renderHome() {
  const mainContent = document.getElementById("main-content");
  if (mainContent) {
    mainContent.innerHTML = `
    <section id="home">
      <section id="header">
        <h2>Author</h2>
        <p>Aaron Su -- suaaron.work@gmail.com</p>
    
        <h2>Description</h2>
        <p>
            Powered by LLMs and LangChain. <br>
            Designed for DnD Players and Dungeon Masters. <br>
            Dnd AI provides a toolkit for complex NPC interactions, character building, and more. <br>
            <b>Due to our current hosting limitations, Please allow 50 seconds for the website to spin up! Thank you for your patience.</b>
        </p>
      </section>

      <div id="options" class="collapsible open">
        <section id="options-section">
            <label for="prompterSelect">Prompter:</label>
            <select id="prompterSelect" name="prompter" class="entitylikeDropdown">
              <option value="">Select Prompter</option>
            </select>
            <label for="responderSelect">Responder:</label>
            <select id="responderSelect" name="responder" class="entitylikeDropdown">
              <option value="">Select Responder</option>
            </select>
            <label for="botSelect">Bot:</label>
            <select id="botSelect" name="bot">
              <option value="">Select Bot</option>
            </select>
        </section>
      </div>

      <div class="toggle-container indent-section">
        <label for="collapsible-toggle1">Collapse Options</label>
        <input type="checkbox" id="collapsible-toggle1" class="toggle">
      </div>

      <div id="Character Info" class="collapsible open">
        <section id="jsonDisplay">
          <label for="prompterInfo">Prompter Info:</label>
          <pre id="prompterInfo"></pre>
          <label for="responderInfo">Responder Info:</label>
          <pre id="responderInfo"></pre>
        </section>
      </div>
      
      <div class="toggle-container indent-section">
        <label for="collapsible-toggle2" class="collapsible-toggle">Collapse Character Info</label>
        <input type="checkbox" id="collapsible-toggle2" class="toggle">
      </div>

      <section id="dialogue">
        <div>
          <label for="userInput">Enter Text:</label>
          <input type="text" id="userInput" name="userInput">
          <button id="sendPromptButton">Send Prompt</button>
        </div>
        <div id="response"></div>
      </section>
    </section>
  `;
  }
  setupHome(); // attach all event listeners, load data, etc.
}

// DATA MANIPULATION //////////////////////////////////////

function updateDialogueDisplay(
  prompter: EntityLike,
  responder: EntityLike,
  prompt: string,
  response: string
) {
  const prompterName = prompter.name;
  const responderName = responder.name;

  const responseDiv = document.getElementById("response");
  dialogueHandler.addToDialogue(prompt, response);
  const dialogue = dialogueHandler.getDialogue();
  const dialogueHtml = dialogue
    .slice()
    .reverse()
    .map(
      (entry) => `
      <div>
        <p><strong>${prompterName}:</strong> ${entry.prompt}</p>
        <p><strong>${responderName}:</strong> ${entry.response}</p>
      </div>
    `
    )
    .join("");

  responseDiv!.innerHTML = dialogueHtml;

  // Ensure the responseDiv is scrollable
  responseDiv!.style.overflowY = "auto";
  responseDiv!.style.maxHeight = "300px"; // Set the desired max height for scrolling
}


function getPromptData(): PromptData {
  const userInput = (<HTMLInputElement>document.getElementById("userInput"))
    .value;
  const botSelect = document.getElementById("botSelect") as HTMLSelectElement;
  const prompterSelect = document.getElementById(
    "prompterSelect"
  ) as HTMLSelectElement;
  const responderSelect = document.getElementById(
    "responderSelect"
  ) as HTMLSelectElement;

  const selectedBot = botSelect.selectedOptions[0];
  const BOT_ID = selectedBot.value;
  const botName = selectedBot.text;
  const botType = "default_bot";

  const selectedPrompter = prompterSelect.selectedOptions[0];
  const selectedResponder = responderSelect.selectedOptions[0];
  const PROMPTER_ID = selectedPrompter.value;
  const RESPONDER_ID = selectedResponder.value;

  const prompterType = selectedPrompter.text.split(":")[0];
  const responderType = selectedResponder.text.split(":")[0];
  const prompterName = selectedPrompter.text.split(":")[1];
  const responderName = selectedResponder.text.split(":")[1];

  console.log("_PROMPTER_ID:", PROMPTER_ID);
  console.log("_PROMPTER_NAME:", prompterName);
  console.log("_PROMPTER_TYPE:", prompterType);

  return {
    userInput,
    prompter: {
      _id: PROMPTER_ID,
      name: prompterName,
      type: prompterType,
    },
    responder: {
      _id: RESPONDER_ID,
      name: responderName,
      type: responderType,
    },
    bot: {
      _id: BOT_ID,
      name: botName,
      type: botType,
    },
  };
}

export async function handleSendPrompt(): Promise<void> {
  try {
    const formData = getPromptData();
    const responseMessage = await sendPrompt(formData);
    updateDialogueDisplay(
      formData.prompter,
      formData.responder,
      formData.userInput,
      responseMessage
    );
  } catch (error) {
    console.error("Error handling prompt:", error);
  }
}

async function handleGetEntityLike(
  entity_like: EntityLike
): Promise<void> {
  let data;
  const type = entity_like.type;
  const ID = entity_like._id;

  if (type === "Entity") {
    data = await sendGetEntity(ID);
  } else if (type === "NPC") {
    data = await sendGetNPC(ID);
  } else if (type === "Player") {
    data = await sendGetPlayer(ID);
  } else {
    console.error("Invalid type:", type);
  }

  console.log("data:", data);
  return data;
}

async function handleEntityLikeData(): Promise<{
  entities: EntityLike[];
  npcs: EntityLike[];
  players: EntityLike[];
}> {
  try {
    const data = await sendGetAllEntityLike();
    const entities: EntityLike[] = Array.isArray(data.Entities)
      ? data.Entities
      : [];
    const npcs: EntityLike[] = Array.isArray(data.NPCs) ? data.NPCs : [];
    const players: EntityLike[] = Array.isArray(data.Players)
      ? data.Players
      : [];

    return { entities, npcs, players };
  } catch (error) {
    console.error("Error fetching entity-like data:", error);
    return { entities: [], npcs: [], players: [] };
  }
}

// API CALLS //////////////////////////////////////////

/**
 * Sends a prompt to the server and returns the response.
 *
 * @endpoint {POST} API_ENDPOINTS.PROMPT
 */
async function sendPrompt(formData: any): Promise<any> {
  try {
    const url = API_ENDPOINTS.PROMPT;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        bot: formData.bot,
        prompter: formData.prompter,
        responder: formData.responder,
        userInput: formData.userInput,
      }),
    });
    const answer = await response.json();
    return answer.message;
  } catch (error) {
    console.error("Error:", error);
    throw error; // Propagate the error further
  }
}

/**
 * Sends a GET request to the server to retrieve an entity.
 *
 * @endpoint {GET} API_ENDPOINTS.ENTITY
 */
export async function sendGetEntity(ID: string): Promise<any> {
  const url = `${API_ENDPOINTS.ENTITY}/${ID}`; // Replace with your actual API endpoint
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json(); // Assuming response is JSON
  } catch (error) {
    console.error("Error fetching entity:", error);
    throw error;
  }
}

/**
 * Sends a GET request to the server to retrieve an NPC.
 * @endpoint {GET} API_ENDPOINTS.NPC
 */
export async function sendGetNPC(ID: string): Promise<any> {
  const url = `${API_ENDPOINTS.NPC}/${ID}`; // Replace with your actual API endpoint
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json(); // Assuming response is JSON
  } catch (error) {
    console.error("Error fetching NPC:", error);
    throw error;
  }
}

/**
 * Sends a GET request to the server to retrieve a Player.
 *
 * @endpoint {GET} API_ENDPOINTS.PLAYER
 */
export async function sendGetPlayer(ID: string): Promise<any> {
  const url = `${API_ENDPOINTS.PLAYER}/${ID}`; // Replace with your actual API endpoint
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json(); // Ass  uming response is JSON
  } catch (error) {
    console.error("Error fetching player:", error);
    throw error;
  }
}

/**
 * Sends a GET request to the server to retrieve all entity-like objects.
 *
 * @endpoint {GET} API_ENDPOINTS.ALL
 */
export async function sendGetAllEntityLike(): Promise<any> {
  const url = API_ENDPOINTS.ALL;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Sends a GET request to the server to retrieve all bots.
 *
 * @endpoint {GET} API_ENDPOINTS.BOT
 */
export async function sendGetAllBots(): Promise<any> {
  const url = API_ENDPOINTS.BOT;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// PAGE LOADING AND SETUP //////////////////////////////////

/**
 * Loads the entity-like dropdowns with data from the server.
 */
async function loadEntityLikeDropdown() {
  const { entities, npcs, players } = await handleEntityLikeData();

  const dropdowns = document.querySelectorAll(
    ".entitylikeDropdown"
  ) as NodeListOf<HTMLSelectElement>;

  dropdowns.forEach((dropdown) => {
    dropdown.innerHTML = "";
    populateAppendDropdown(dropdown, convertToDropdownItems(entities));
    populateAppendDropdown(dropdown, convertToDropdownItems(npcs));
    populateAppendDropdown(dropdown, convertToDropdownItems(players));
  });
}

/**
 * Loads the bot dropdown with data from the server.
 */
async function loadBotSelect() {
  const botSelect = document.getElementById("botSelect") as HTMLSelectElement;
  if (botSelect) {
    botSelect.innerHTML = "";
    const data = await sendGetAllBots();
    const bots: Bot[] = Array.isArray(data.Bots) ? data.Bots : [];
    const botSelectItems: DropdownItem[] = bots.map((bot) => ({
      value: bot._id!,
      text: bot.name,
    }));

    populateAppendDropdown(botSelect, botSelectItems);
  } else {
    console.error("Dropdown with ID botSelect not found.");
  }
}

/**
 * Loads the prompter and responder info.
 */
async function updatePrompterResponderInfo() {
  const prompterInfo = document.getElementById("prompterInfo");
  const responderInfo = document.getElementById("responderInfo");

  const prompterSelect = document.getElementById(
    "prompterSelect"
  ) as HTMLSelectElement;
  const responderSelect = document.getElementById(
    "responderSelect"
  ) as HTMLSelectElement;

  if (
    prompterInfo === null ||
    responderInfo === null ||
    prompterSelect === null ||
    responderSelect === null
  ) {
    console.error("Element not found.");
    return;
  }

  const selectedPrompter = prompterSelect.selectedOptions[0];
  const selectedResponder = responderSelect.selectedOptions[0];
  // console.log("selectedPrompter:", selectedPrompter);
  
  const PROMPTER_ID = selectedPrompter.value;
  const RESPONDER_ID = selectedResponder.value;
  const prompterType = selectedPrompter.text.split(":")[0];
  const responderType = selectedResponder.text.split(":")[0];
  const prompterName = selectedPrompter.text.split(":")[1];
  const responderName = selectedResponder.text.split(":")[1];

  // console.log("PROMPTER_ID:", PROMPTER_ID);
  // console.log("PROMPTER_NAME:", prompterName);
  // console.log("PROMPTER_TYPE:", prompterType);
  

  const prompter: EntityLike = {
    _id: PROMPTER_ID,
    name: prompterName,
    type: prompterType,
  };
  const responder: EntityLike = {
    _id: RESPONDER_ID,
    name: responderName,
    type: responderType,
  };


  const prompterJson = await handleGetEntityLike(prompter);
  const responderJson = await handleGetEntityLike(responder);

  prompterInfo.textContent = JSON.stringify(prompterJson, null, 2);
  responderInfo.textContent = JSON.stringify(responderJson, null, 2);
}

/**
 * Sets up the collapsible options.
 */
function setupCollapsibles() {
  console.log("setupCollapsibles called! with querySelectorAll.");

  const toggles = document.querySelectorAll(
    ".toggle"
  ) as NodeListOf<HTMLInputElement>;
  const collapsibles = document.querySelectorAll(
    ".collapsible.open"
  ) as NodeListOf<HTMLElement>;

  if (toggles.length === 0) {
    console.error("No collapsible toggle elements found.");
    return; // Exit function if no toggles found
  }

  if (collapsibles.length === 0) {
    console.error("No collapsible elements found.");
    return; // Exit function if no collapsibles found
  }

  // Add event listeners to each toggle
  toggles.forEach((toggle, index) => {
    const collapsible = collapsibles[index]; // Match each toggle with its corresponding collapsible

    toggle.addEventListener("change", function () {
      console.log(collapsible.classList);

      if (toggle.checked) {
        if (collapsible.classList.contains("open")) {
          collapsible.classList.remove("open");
        }
      } else {
        if (!collapsible.classList.contains("open")) {
          collapsible.classList.add("open");
        }
      }

      console.log(collapsible.classList);
    });
  });
}

/**
 * Sets up everything in the home page.
 */
async function setupHome() {
  console.log("setupHome called!");

  const sendPromptButton = document.getElementById("sendPromptButton");
  const botSelect = document.getElementById("botSelect");
  const prompterSelect = document.getElementById("prompterSelect");
  const responderSelect = document.getElementById("responderSelect");
  const jsonDisplay = document.getElementById("jsonDisplay");

  if (!sendPromptButton) {
    console.error('Button with ID "sendPromptButton" not found.');
    return;
  }
  if (!botSelect) {
    console.error('Dropdown with ID "botSelect" not found.');
    return;
  }
  if (!prompterSelect || !responderSelect || !jsonDisplay) {
    console.error(
      'Missing element: prompterSelect, responderSelect, and/or jsonContent'
    );
    return;
  }

  // Setup event listeners and load data
  sendPromptButton.addEventListener("click", handleSendPrompt);
  loadBotSelect();
  await loadEntityLikeDropdown();
  await updatePrompterResponderInfo();

  // Listen for changes in the entity-like dropdowns
  const entitylikeDropdowns = document.querySelectorAll(".entitylikeDropdown");
  entitylikeDropdowns.forEach(dropdown => {
    dropdown.addEventListener("change", updatePrompterResponderInfo);
  });

  setupCollapsibles();
}

