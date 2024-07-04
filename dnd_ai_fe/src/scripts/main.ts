
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
  try {
    const url = 'http://localhost:5000/prompt'; 
    const formData = getFormData();
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
    updateResponseDisplay(formData.userInput, answer.message);
    // document.getElementById('response')!.innerText = data.message;
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

function populateDropdown(dropdown: HTMLSelectElement, entities: any[], npcs: any[], players: any[]) {
  dropdown.innerHTML = ''; // Clear any existing options

  entities.forEach((entity: any) => {
    const option = document.createElement('option');
    option.value = entity._id;
    option.text = `Entity: ${entity.value}`;
    dropdown.add(option);
  });

  npcs.forEach((npc: any) => {
    const option = document.createElement('option');
    option.value = npc._id;
    option.text = `NPC: ${npc.value}`;
    dropdown.add(option);
  });

  players.forEach((player: any) => {
    const option = document.createElement('option');
    option.value = player._id;
    option.text = `Player: ${player.value}`;
    dropdown.add(option);
  });
}

async function loadEntityLikeDropdown() {
  const { entities, npcs, players } = await fetchEntityLikeData();

  const dropdowns = document.querySelectorAll('.entitylikeDropdown') as NodeListOf<HTMLSelectElement>;
  dropdowns.forEach((dropdown) => {
    populateDropdown(dropdown, entities, npcs, players);
  });
}

// async function loadEntityLikeDropdown() {

//   try {
//       const data = await sendGetAllEntitylike();
//       const entities = data.Entities || [];
//       const npcs = data.NPCs;
//       const players = data.Players;

//       const dropdowns = document.querySelectorAll('.entitylikeDropdown') as NodeListOf<HTMLSelectElement>;
//       dropdowns.forEach((dropdown) => {
//         dropdown.innerHTML = ''; // Clear any existing options

//         entities.forEach((entity: any) => {
//           const option = document.createElement('option');
//           option.value = entity._id;
//           option.text = `Entity: ${entity.value}`;
//           dropdown.add(option);
//         });

//         npcs.forEach((npc: any) => {
//           const option = document.createElement('option');
//           option.value = npc._id;
//           option.text = `NPC: ${npc.value}`;
//           dropdown.add(option);
//         });

//         players.forEach((player: any) => {
//           const option = document.createElement('option');
//           option.value = player._id;
//           option.text = `Player: ${player.value}`;
//           dropdown.add(option);
//         });
//       });
      
//   } catch (error) {
//       console.error('Error fetching entity-like data:', error);
//   }
// }

// Function to get and process HTML elements
function getFormData() {
  const userInput = (<HTMLInputElement>document.getElementById('userInput')).value;
  const prompterSelect = document.getElementById('prompterSelect') as HTMLSelectElement;
  const responderSelect = document.getElementById('responderSelect') as HTMLSelectElement;

  const selectedOption1 = prompterSelect.selectedOptions[0];
  const PROMPTER_ID = selectedOption1.value;
  const selectedOption2 = responderSelect.selectedOptions[0];
  const RESPONDER_ID = selectedOption2.value;

  return {
    userInput,
    prompter: {
      _id: PROMPTER_ID,
      type: selectedOption1.text.split(':')[0]
    },
    responder: {
      _id: RESPONDER_ID,
      type: selectedOption2.text.split(':')[0]
    }
  };
}

// function updateResponseDisplay(message: any) {
//   const responseDiv = document.getElementById('response');
//   responseDiv!.innerText = message;
// }

let dialogue: { prompt: string; response: string }[] = [];

function updateResponseDisplay(prompt: string, response: string) {
  const responseDiv = document.getElementById('response');
  
  // Add the new prompt and response to the dialogue
  dialogue.push({ prompt, response });

  // Keep only the last 5 items in the dialogue
  if (dialogue.length > 5) {
    dialogue.shift();
  }

  // Create the dialogue HTML
  console.log(dialogue)
  const dialogueHtml = dialogue.map(entry => `
    <div>
      <p><strong>Prompt:</strong> ${entry.prompt}</p>
      <p><strong>Response:</strong> ${entry.response}</p>
    </div>
  `).join('');

  // Update the responseDiv with the dialogue HTML
  responseDiv!.innerHTML = dialogueHtml;
}

// event-driven logic
document.addEventListener('DOMContentLoaded', () => {
  const sendPromptButton = document.getElementById('sendPromptButton');
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
});