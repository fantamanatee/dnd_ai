# Inspired by https://arxiv.org/pdf/2304.03442, which uses observations, planning, and reflections to simulate agents.
# We will only use observations and reflections for our role-play agents.


class Agent:
    def __init__(self, reasoning_bots, db_collection):
        """
        Initializes the Agent with reasoning bots and a database collection.

        Args:
            reasoning_bots (dict): Dictionary mapping bots to their application frequency.
            db_collection (MongoDBCollection): The MongoDB collection for storing observations and reflections.
        """
        self.reasoning_bots = reasoning_bots
        self.col = db_collection
        self.turn_count = 0
        self.history = []

    def handle_input(self, input_text, prompter, responder, chatbot_response):
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

        # Store the chatbot response in the history
        self.history.append(chatbot_response)

        # Select the reasoning bots based on the turn count
        selected_reasoning_bots = self.select_reasoning_bots()

        # Generate reasoning responses (observations and/or reflections)
        reasoning_responses = []
        for bot in selected_reasoning_bots:
            response = bot.generate_response(self.history)
            reasoning_responses.append(response)
            self.store_reasoning_response(response)

        return chatbot_response, reasoning_responses

    def select_reasoning_bots(self):
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

    def store_reasoning_response(self, response):
        """
        Stores the reasoning response in the database.

        Args:
            response (str): The reasoning response to be stored.
        """
        self.col.insert_one({"turn": self.turn_count, "response": response})

    def reset(self):
        """
        Resets the agent for a new session.
        """
        self.turn_count = 0
        self.history = []
