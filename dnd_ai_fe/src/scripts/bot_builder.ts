import axios from "axios";

import { API_ENDPOINTS } from "./config";
import {
  populateAppendDropdown,
  validateEntity,
  validateNPC,
  validatePlayer,
  validateBot,
  convertToDropdownItem
} from "./util";
import { Entity, NPC, Player, Bot, EntityLike, DropdownItem } from "./interface";

export function renderBotBuilder() {
  const mainContent = document.getElementById("main-content");
  // Assuming this part is within your script where you update the mainContent
  if (mainContent) {
    mainContent.innerHTML = `
        <section id="bot-builder">
            <h2>Bot Builder</h2>
            <div>
                <label for="botSelect">Bot Type:</label>
                <select id="botSelect">
                    <option value="">Select Bot Type</option>
                </select>
            </div>

            <label for="userInput">Enter Bot Config/Prompts:</label>
            <textarea id="userInput"></textarea>

            <button id="createBotButton">Create Bot</button>
            <div id="response"></div>
        </section>
    `;
  }
  setupBotBuilder();
}
const exampleBot = {
  name: "default_bot1",
  contextualize_q_system_prompt: "Given a chat history and the latest prompt which might reference context in the chat history, formulate a standalone prompt which can be understood without the chat history. Do NOT answer the prompt, just reformulate it if needed and otherwise return it as is.",
  qa_system_prompt: "You are a role playing chatbot for a Dungeons and Dragons game. There are two fictional characters: a prompter and a responder. You must respond to the prompt as if you are the responder. Use the following pieces of retrieved context to answer the prompt. If the context does not apply, respond in a way that makes sense. Use three sentences maximum, and keep the answer concise.\n\n{context}",
  config: {
    model: "gpt-3.5-turbo",
    temperature: 0,
  },
}

async function loadBotTypeSelect() {
  const botSelect = document.getElementById(
    "botSelect"
  ) as HTMLSelectElement;
  if (botSelect) {
    botSelect.innerHTML = "";
    const data = [
      {
        value: "default_bot",
        text: "default_bot",
      },
    ]
    populateAppendDropdown(botSelect, data);
  } else {
    console.error("Dropdown with ID botSelect not found.");
  }
}






export async function sendConstructBot(data: Bot): Promise<string> {
  try {
    const response = await axios.post(API_ENDPOINTS.BOT, data);
    return response.data.message;
  } catch (error) {
    console.error("Error constructing bot:", error);
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

export async function handleSendCreateBot(): Promise<void> {
  const userInput = document.getElementById("userInput") as HTMLTextAreaElement;
  const botSelect = document.getElementById(
    "botSelect"
  ) as HTMLSelectElement;
  const selectedType = botSelect.selectedOptions[0].value;
  let response;
  try {
    if (selectedType === "default_bot") {
      console.log("Creating bot...");
      console.log("userInput.value:", userInput.value)
      const bot : Bot = validateBot(JSON.parse(userInput.value));
      response = await sendConstructBot(bot);
    } else {
      console.error("Invalid Bot Type selected.");
      return;
    }
  } catch (error) {
    console.error(error);
    userInput.value = JSON.stringify(exampleBot, null, 2); // reset to example entity
    response = "Invalid input for " + selectedType + ". Try again."; // Corrected concatenation
  }
  updateResponseDiv(response!);
}

function setupBotBuilder() {
  const botSelect = document.getElementById("botSelect") as HTMLSelectElement;
  const userInput = document.getElementById("userInput") as HTMLTextAreaElement;
  
  botSelect.addEventListener("change", function() {
    console.log('changed!')
    switch (botSelect.value) {
        case "default_bot":
            userInput.value = JSON.stringify(exampleBot, null, 2);
            break;
        default:
            console.error("Invalid Bot Type selected.");
    }
  }); 

  loadBotTypeSelect();


  userInput.value = JSON.stringify(exampleBot, null, 2);

  const createBotButton = document.getElementById(
    "createBotButton"
  );
  if (createBotButton) {
    createBotButton.addEventListener("click", () => {
      handleSendCreateBot();
    });
  } else {
    console.error('Button with id="createBotButton" not found.');
  }
}
