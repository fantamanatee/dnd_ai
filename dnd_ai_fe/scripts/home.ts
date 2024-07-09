import { populateAppendDropdown, convertToDropdownItems } from "./util";
import { EntityLike, PromptData, DropdownItem, Bot } from "./interface";
import { API_ENDPOINTS } from "./config";

// Define your page components testing
export function renderHome() {
  const mainContent = document.getElementById("main-content");
  if (mainContent) {
    mainContent.innerHTML = `
        <section id="home">
          <h2>Author</h2>
          <p>Aaron Su -- suaaron.work@gmail.com</p>
  
          <h2>Description</h2>
          <p>
              Powered by LLMs and LangChain. <br>
              Designed for DnD Players and Dungeon Masters. <br>
              Dnd AI provides a toolkit for complex NPC interactions, character building, and more.
          </p>
  
          <div>
            <label for="botSelect">Bot:</label>
            <select id="botSelect" name="bot">
              <option value="">Select Bot</option>
            </select>
            <label for="prompterSelect">Prompter:</label>
            <select id="prompterSelect" name="prompter" class="entitylikeDropdown">
              <option value="">Select Prompter</option>
            </select>
            <label for="responderSelect">Responder:</label>
            <select id="responderSelect" name="responder" class="entitylikeDropdown">
              <option value="">Select Responder</option>
            </select>
  
            <label for="userInput">Enter Text:</label>
            <input type="text" id="userInput" name="userInput">
  
            <button id="sendPromptButton">Send Prompt</button>
          </div>
          <div id="response"></div>
        </section>
      `;
  }
  setupHome(); // attach all event listeners, load data, etc.
}

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

async function fetchEntityLikeData(): Promise<{
  entities: EntityLike[];
  npcs: EntityLike[];
  players: EntityLike[];
}> {
  try {
    const data = await sendGetAllEntityLike();
    // Validate and ensure each item in arrays is of type EntityLike
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

async function loadEntityLikeDropdown() {
  const { entities, npcs, players } = await fetchEntityLikeData();


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
  const botType = 'default_bot'

  const selectedPrompter = prompterSelect.selectedOptions[0];
  const selectedResponder = responderSelect.selectedOptions[0];
  const PROMPTER_ID = selectedPrompter.value;
  const RESPONDER_ID = selectedResponder.value;

  const prompterType = selectedPrompter.text.split(":")[0];
  const responderType = selectedResponder.text.split(":")[0];
  const prompterName = selectedPrompter.text.split(":")[1];
  const responderName = selectedResponder.text.split(":")[1];

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

class DialogueHandler {
  private dialogue: { prompt: string; response: string }[];

  constructor() {
    this.dialogue = [];
  }

  public getDialogue(): { prompt: string; response: string }[] {
    return this.dialogue;
  }

  public addToDialogue(prompt: string, response: string): void {
    this.dialogue.push({ prompt, response });

    if (this.dialogue.length > 5) {
      this.dialogue = this.dialogue.slice(-5);
    }
  }

  public clearDialogue(): void {
    this.dialogue = [];
  }
}
const dialogueHandler = new DialogueHandler();

function setupHome() {
  const sendPromptButton = document.getElementById("sendPromptButton");
  if (sendPromptButton) {
    sendPromptButton.addEventListener("click", handleSendPrompt);
  } else {
    console.error('Button with ID "sendPromptButton" not found.');
  }
  const botSelect = document.getElementById("botSelect");
  if (botSelect) {
    loadBotSelect();
  } else {
    console.error('Dropdown with ID "botSelect" not found.');
  }
  const prompterSelect = document.getElementById("prompterSelect");
  const responderSelect = document.getElementById("responderSelect");
  if (prompterSelect && responderSelect) {
    loadEntityLikeDropdown();
  } else {
    console.error(
      'Dropdowns with IDs "prompterSelect" and "responderSelect" not found.'
    );
  }
}
