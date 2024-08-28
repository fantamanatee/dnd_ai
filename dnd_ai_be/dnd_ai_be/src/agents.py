# Inspired by https://arxiv.org/pdf/2304.03442, which uses observations, planning, and reflections to simulate agents.
# We will only use observations and reflections for our role-play agents.

from typing import List, Dict
from dnd_ai_be.src.bots import ChatBot, ReasoningBot
from dnd_ai_be.src.characters import Player, NPC, Entity
from bson import ObjectId
from dnd_ai_be.src.db_util import DB, URI, DB_NAME


class Agent:
    def __init__(
        self,
        name: str = None,
        reasoning_bots: Dict[ReasoningBot, int] = None,
        chat_bots: List[ChatBot] = None,
        ID: str = None,
    ):
        """
        Initializes the Agent with reasoning bots and a database collection.

        Args:
            reasoning_bots (dict): Dictionary mapping reasoning bots to their call frequency.
            memory_stream (MongoDBCollection): The MongoDB collection for storing observations and reflections.
            ID (str): The unique identifier for the Agent.
        """
        self.name = name
        self.reasoning_bots = reasoning_bots
        self.chat_bots = chat_bots
        self.turn_count = 0

        # FIXME persist agents in DB.Agents?
        # if not ID is None:
        #     if self.col.find_one({"_id": ObjectId(ID)}) is None:
        #         raise ValueError("BOT_ID does not exist in database.")
        #     else:
        #         self.ID = ID
        #         self.name = self.col.find_one({"_id": ObjectId(ID)})["name"]
        #         self.reasoning_bots = self.col.find_one({"_id": ObjectId(ID)})["reasoning_bots"]
        #         self.chat_bots = self.col.find_one({"_id": ObjectId(ID)})["chat_bots"]

        #         print("Chatbot loaded with BOT_ID:", ID)
        # else:

    def handle_input(self, input_text, prompter, responder):
        """
        Handles user input and determines the appropriate bot to generate responses.

        Args:
            input_text (str): The user's input text.
            prompter (Character): The character initiating the interaction.
            responder (Character): The character responding to the interaction.
            chatbot_response (str): The response from either the DialogueBot or ActingBot.

        Returns:
            tuple: The chatbot response and the generated reasoning responses (observations and/or reflections).
        """
        self.turn_count += 1

        chatbot = self.chat_bots[0]  # FIXME make this dynamic later
        chatbot_response = chatbot.generate_response(input_text, prompter, responder)

        # Store the chatbot response in the history

        # Select the reasoning bots based on the turn count
        selected_reasoning_bots = self.select_reasoning_bots()

        # Generate reasoning responses (observations and/or reflections)
        reasoning_responses = []
        for reasoning_bot in selected_reasoning_bots:
            k = self.reasoning_bots[reasoning_bot]
            response = reasoning_bot.generate_response(
                input_text, prompter, responder, k
            )
            reasoning_responses.append(response)

        return chatbot_response, reasoning_responses

    def select_reasoning_bots(self) -> List[ReasoningBot]:
        """
        Selects the appropriate reasoning bots based on the turn count.

        Returns:
            list: The selected reasoning bots.
        """
        selected_bots = []
        for bot, frequency in self.reasoning_bots.items():
            if self.turn_count % frequency == 0:
                selected_bots.append(bot)

        return selected_bots

    def reset(self):
        """
        Resets the agent for a new session.
        """
        self.turn_count = 0
        self.history = []


if __name__ == "__main__":
    # Initialize the Agent
    observation_bot = ReasoningBot(
        name="ObservationBot1",
        reasoning_collection_name="Sessions",
        reasoning_system_prompt="Use the most recent chat entry to generate a new observation about the character(s). Try to make inferences rather than simply repeating information. Be direct and brief. Use NER and to identify entities and relationships. \n\n{context}",
    )
    reflection_bot = ReasoningBot(
        name="ReflectionBot1",
        reasoning_collection_name="Memories",
        reasoning_system_prompt="Use the provided observations to generate a new reflection about the character(s) and their actions/ dialogue. Try to make inferences rather than simply repeating information, and try to incorporate all significant details in your reflection. Write a one sentence summary of the provided . Use NER to identify entities and relationships. \n\n{context}",
    )

    # observation_bot = ReasoningBot(ID="669fe418fa6996a3780c1531")
    reasoning_bots = {
        observation_bot: 1,
        reflection_bot: 4,
    }

    NER1 = ChatBot(ID="6696c90e56b00a88e374791a")
    chat_bots = [NER1]

    agent = Agent(name="agent1", reasoning_bots=reasoning_bots, chat_bots=chat_bots)
    prompter = Player(ID="66997d89afca9066c9e31804")  # Legolas
    responder = NPC(ID="66997d86afca9066c9e31803")  # Gobbo

    while True:
        prompt = input("Enter a prompt: ")
        response, reasoning = agent.handle_input(prompt, prompter, responder)
        print("response:", response)
        print("reasoning:", reasoning)
