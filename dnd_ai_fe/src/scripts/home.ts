// Define your page components
export function renderHome() {
    const mainContent = document.getElementById('main-content');
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

  export async function sendPrompt() {
    /**
     * Sends a prompt to the server with user input and displays the response.
     * 
     * This sends user input to a server endpoint via a POST request.
     * The server's response is then displayed on the webpage.
     * 
     * @async
     * @function sendPrompt
     * @returns {Promise<void>}
     */
    console.log('Sending prompt...')
    try {
      const url = 'http://localhost:5000/prompt'; 
      const formData = getPromptData();
      console.log('prompt body:', JSON.stringify({
        prompter: formData.prompter,
        responder: formData.responder,
        userInput: formData.userInput
      }));
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompter: formData.prompter,
          responder: formData.responder,
          userInput: formData.userInput
        })
      });
      const answer = await response.json();
      updateDialogueDisplay(formData.prompter, formData.responder, formData.userInput, answer.message);
    } catch (error) {
      console.error('Error:', error);
    }
  }
  
  export async function sendGetAllEntitylike(): Promise<any> {
    const url = 'http://localhost:5000/all';
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
  
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  
    return await response.json();
  }
  
  async function fetchEntityLikeData(): Promise<{ entities: any[], npcs: any[], players: any[] }> {
    try {
      const data = await sendGetAllEntitylike();
      const entities = data.Entities || [];
      const npcs = data.NPCs || [];
      const players = data.Players || [];
  
      return { entities, npcs, players };
    } catch (error) {
      console.error('Error fetching entity-like data:', error);
      return { entities: [], npcs: [], players: [] };
    }
  }
  
  function populateAppendDropdown(dropdown: HTMLSelectElement, items: any[], prefix: string = '') {
    items.forEach((item: any) => {
      const option = document.createElement('option');
      option.value = item._id;
      if (prefix === '') {
        option.text = item.value;
      } else {
        option.text = `${prefix}: ${item.value}`;
      }
      dropdown.add(option);
    });
  }
  
  async function loadEntityLikeDropdown() {
    const { entities, npcs, players } = await fetchEntityLikeData();
  
    const dropdowns = document.querySelectorAll('.entitylikeDropdown') as NodeListOf<HTMLSelectElement>;
    dropdowns.forEach((dropdown) => {
      dropdown.innerHTML = '';
      populateAppendDropdown(dropdown, entities, 'Entity');
      populateAppendDropdown(dropdown, npcs, 'NPC');
      populateAppendDropdown(dropdown, players, 'Player');
    });
  }

  interface EntityLike {
    _id: string;
    name: string;
    type: string;
  }
  
  interface PromptData {
    userInput: string;
    prompter: EntityLike;
    responder: EntityLike;
  }

  function getPromptData() : PromptData {
    const userInput = (<HTMLInputElement>document.getElementById('userInput')).value;
    const prompterSelect = document.getElementById('prompterSelect') as HTMLSelectElement;
    const responderSelect = document.getElementById('responderSelect') as HTMLSelectElement;
  
    const selectedOption1 = prompterSelect.selectedOptions[0];
    const selectedOption2 = responderSelect.selectedOptions[0];
    const PROMPTER_ID = selectedOption1.value;
    const RESPONDER_ID = selectedOption2.value;
    const prompterType = selectedOption1.text.split(':')[0];
    const responderType = selectedOption2.text.split(':')[0];
    const prompterName = selectedOption1.text.split(':')[1];
    const responderName = selectedOption2.text.split(':')[1];
  
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
      }
    };
  }

  function updateDialogueDisplay(prompter: EntityLike, responder: EntityLike, prompt: string, response: string) {
    const prompterName = prompter.name;
    const responderName = responder.name;

    const responseDiv = document.getElementById('response');
    dialogueHandler.addToDialogue(prompt, response);
    const dialogue = dialogueHandler.getDialogue();
    const dialogueHtml = dialogue.slice().reverse().map(entry => `
      <div>
        <p><strong>${prompterName}:</strong> ${entry.prompt}</p>
        <p><strong>${responderName}:</strong> ${entry.response}</p>
      </div>
    `).join('');
  
    responseDiv!.innerHTML = dialogueHtml;
  
    // Ensure the responseDiv is scrollable
    responseDiv!.style.overflowY = 'auto';
    responseDiv!.style.maxHeight = '300px';  // Set the desired max height for scrolling
  }

  class DialogueHandler {
    private dialogue: { prompt: string; response: string }[];
  
    constructor() {
      // Initialize dialogue from localStorage or set to an empty array if not found
      const storedDialogue = localStorage.getItem('dialogue');
      this.dialogue = storedDialogue ? JSON.parse(storedDialogue) : [];
    }
  
    public getDialogue(): { prompt: string; response: string }[] {
      return this.dialogue;
    }
  
    public addToDialogue(prompt: string, response: string): void {
      // Add new prompt and response to dialogue
      this.dialogue.push({ prompt, response });
  
      // Limit dialogue to last 5 items
      if (this.dialogue.length > 5) {
        this.dialogue = this.dialogue.slice(-5);
      }
  
      // Save updated dialogue to localStorage
      this.saveDialogueToLocalStorage();
    }
  
    private saveDialogueToLocalStorage(): void {
      localStorage.setItem('dialogue', JSON.stringify(this.dialogue));
    }
  
    public clearDialogue(): void {
      // Clear dialogue and remove from localStorage
      this.dialogue = [];
      localStorage.removeItem('dialogue');
    }
  }
  const dialogueHandler = new DialogueHandler();
  window.addEventListener('beforeunload', () => {
    dialogueHandler.clearDialogue();
  });

  function setupHome() {
    console.log('setupHome called')
    const sendPromptButton = document.getElementById('sendPromptButton');
    console.log()
    if (sendPromptButton) {
      sendPromptButton.addEventListener('click', sendPrompt);
    } else {
      console.error('Button with ID "sendPromptButton" not found.');
    }
  
    const prompterSelect = document.getElementById('prompterSelect');
    const responderSelect = document.getElementById('responderSelect');
    if (prompterSelect && responderSelect) {
      loadEntityLikeDropdown();
    } else {
      console.error('Dropdowns with IDs "prompterSelect" and "responderSelect" not found.');
    }
  }
  