
let environment;

if (process.env.NODE_ENV === 'development') {
  environment = {
    ENVIRONMENT: 'DEV',
    BASE_URL: 'http://localhost:5000'
  };
} else {
  environment = {
    ENVIRONMENT: 'PROD',
    BASE_URL: 'https://dnd-ai-server.onrender.com'
  };
}
const BASE_URL = environment.BASE_URL;
console.log(`Using BASE_URL: ${BASE_URL}`);


export const API_ENDPOINTS = {
  PROMPT: `${BASE_URL}/prompt`,
  ENTITY: `${BASE_URL}/entity`,
  NPC: `${BASE_URL}/npc`,
  PLAYER: `${BASE_URL}/player`,
  ALL: `${BASE_URL}/all`,
  BOT: `${BASE_URL}/bot`
  // Add more endpoints as needed
};
