// config.ts
// const BASE_URL = "http://localhost:5000";
const BASE_URL = "https://dnd-ai-server.onrender.com"

export const API_ENDPOINTS = {
  PROMPT: `${BASE_URL}/prompt`,
  ENTITY: `${BASE_URL}/entity`,
  NPC: `${BASE_URL}/npc`,
  PLAYER: `${BASE_URL}/player`,
  ALL: `${BASE_URL}/all`,
  BOT: `${BASE_URL}/bot`
  // Add more endpoints as needed
};
