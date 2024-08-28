
let environment;
console.log('process.env.ENVIRONMENT:',process.env.ENVIRONMENT);
if (process.env.ENVIRONMENT === 'development') {
  environment = {
    ENVIRONMENT: 'development',
    BASE_URL: 'http://localhost:5000'
  };
} else {
  environment = {
    ENVIRONMENT: 'production',
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
  BOT: `${BASE_URL}/bot`,
  SESSION: `${BASE_URL}/session`
  // Add more endpoints as needed
};
