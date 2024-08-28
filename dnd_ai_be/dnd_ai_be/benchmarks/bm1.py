from dnd_ai_be.src.bots import ChatBot
from bson import ObjectId
from dnd_ai_be.src.characters import Player, Entity, NPC
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages.ai import AIMessage
import json
import os
from argparse import ArgumentParser
from dnd_ai_be.benchmarks.util import track_with_mlflow


def get_args() -> dict:
    parser = ArgumentParser()
    parser.add_argument(
        "MAX_RESPONSES", type=int, help="Maximum number of responses for each scenario"
    )
    parser.add_argument(
        "SCENARIO_FILE", type=str, help="File containing benchmark scenarios"
    )
    parser.add_argument("CHATBOT_ID", type=str, help="ChatBot ID")
    args = parser.parse_args()
    return vars(args)


# @track_with_mlflow(experiment_name="bm1-SimpleDialogue", verbose=True)
@track_with_mlflow(experiment_name="bm1-SimpleMultiResponseDialogue", verbose=True)
def main(**kwargs):
    """
    Loads and runs a benchmark.
    Contains 1 player, 1 entity, and 1 npc.
    Tests basic dialogue interactions.
    Do not save session dialogue.

    Outputs:
        A json of the continued dialogue, limited to MAX_RESPONSES.

    Returns:
        result: a dict containing the output file path
    """

    MAX_RESPONSES = kwargs.get("MAX_RESPONSES")
    SCENARIO_FILE = kwargs.get("SCENARIO_FILE")
    CHATBOT_ID = kwargs.get("CHATBOT_ID")

    store = {}

    player_elowen = Player(ID="66aa7c905b9452034bd1256a")
    entity_dragonborn = Entity(ID="66aa7c905b9452034bd1256f")
    npc_mabel = NPC(ID="66aa7c905b9452034bd12567")

    CHARACTERS = {
        "Elowen": player_elowen,
        "Dragonborn": entity_dragonborn,
        "Mabel": npc_mabel,
    }
    # breakpoint()

    # bot = ChatBot(ID="66c38445b7efa0dda2066675")
    bot = ChatBot(store=store, ID=CHATBOT_ID)

    with open(SCENARIO_FILE, "r") as f:
        scenarios = json.load(f)

    ### RUN BENCHMARK ###
    for i, scenario in enumerate(scenarios):
        dialogue = scenario["dialogue"]
        prompter_name = dialogue[-1]["speaker"]
        responder_name = dialogue[-2]["speaker"] if len(dialogue) > 1 else None
        prompter = CHARACTERS[prompter_name]
        responder = CHARACTERS[responder_name]
        session_id = f"{prompter_name}_{responder_name}_{i}"

        messages = ChatMessageHistory()
        for j, d in enumerate(dialogue[:-1]):
            content = d["content"]
            speaker = d["speaker"]
            message = AIMessage(content=content)
            messages.add_message(message)
        store[session_id] = messages
        input_text = dialogue[-1]["content"]

        # breakpoint()  # are they chatmessages?

        for k in range(MAX_RESPONSES):
            if responder is None:
                break
            # breakpoint()
            response = bot.generate_response(
                input_text, prompter, responder, session_id=session_id
            )

            # speaker = responder.get_name()
            # message = ChatMessage(role=f"{speaker}_response{k}", content=response)
            # store[scenario_id].add_message(message)

            # Swap prompter and responder
            prompter, responder = responder, prompter
            input_text = response

        # breakpoint()  # are they still chatmessages?

    ### SAVE OUTPUTS ###
    script_name = os.path.basename(__file__).split(".")[0]
    output_file = f"./outputs/{script_name}_mr{MAX_RESPONSES}.json"

    data_out = {}
    for session_id, scenario in store.items():
        data_out[session_id] = [(m.type, m.content) for m in scenario.messages]

    # Write the data to a well-formatted JSON file
    with open(output_file, "w") as file:
        json.dump(data_out, file, indent=4)
        print(f"Output saved to {output_file}")
        result = {"output_file_path": output_file}
        return result


if __name__ == "__main__":
    args = get_args()
    main(**args)
