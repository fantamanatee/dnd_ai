require('dotenv').config();
// const backend_url = 

export async function sendQuery() {
  /**
   * Sends a query to the server with user input and displays the response.
   * 
   * This sends user input to a server endpoint via a POST request.
   * The server's response is then displayed on the webpage.
   * 
   * @async
   * @function sendQuery
   * @returns {Promise<void>}
   */
  try {
    const userInput = (<HTMLInputElement>document.getElementById('userInput')).value;
    const FROM_ID = (<HTMLInputElement>document.getElementById('FROM_ID')).value;
    const TO_ID = (<HTMLInputElement>document.getElementById('TO_ID')).value;
    const url = process.env.BACKEND_URL!;  // Replace with your Flask backend URL
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        FROM_ID: FROM_ID,
        TO_ID: TO_ID,
        userInput: userInput,
      })
    });
    const data = await response.json();
    document.getElementById('response')!.innerText = data.message;
    } catch (error) {
      console.error('Error:', error);
    }
  }

// Add event listener for DOMContentLoaded // FIXME this doesnt work rn. Still using onclick
document.addEventListener('DOMContentLoaded', () => {
  const sendQueryButton = document.getElementById('sendQueryButton');
  if (sendQueryButton) {
    sendQueryButton.addEventListener('click', sendQuery);
  } else {
    console.error('Button with ID "sendQueryButton" not found.');
  }
});