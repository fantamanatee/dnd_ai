from flask import request, jsonify, Blueprint, Response
from dnd_ai_be.src.characters import NPC, Player, Entity, entity_like_classes
from dnd_ai_be.src.db_util import DB
from dnd_ai_be.src.bots import ChatBot, ReasoningBot
from dnd_ai_be.src.agents import Agent
from time import time
from dnd_ai_be.src.util import timer

query_blueprint = Blueprint("query_blueprint", __name__)

# Time to load bot: 0.37419724464416504
# Time to load entity1: 0.1994762420654297
# Time to load entity2: 0.02063918113708496
# Time to get answer: 2.5123660564422607


class ROUTES:
    PROMPT = "/prompt"
    ENTITY = "/entity"
    NPC = "/npc"
    PLAYER = "/player"
    ALL = "/all"
    BOT = "/bot"
    AGENT = "/agent"
    SESSION = "/session"


@query_blueprint.route(ROUTES.PROMPT, methods=["POST"])
@timer()
def handle_prompt() -> Response:
    """Handle POST requests to /prompt endpoint.
    Returns:
      A JSON response.
    """
    data = request.json
    user_input = data.get("userInput", "")

    prompter_data = data.get("prompter", None)
    responder_data = data.get("responder", None)
    bot_data = data.get("bot", None)

    if bot_data:
        bot_id = bot_data.get("_id", None)
    else:
        raise ValueError("Bot not found in request data.")

    if prompter_data:
        prompter_type = prompter_data.get("type", None)
        prompter_id = prompter_data.get("_id", None)
    else:
        raise ValueError("Prompter not found in request data.")

    if responder_data:
        responder_type = responder_data.get("type", None)
        responder_id = responder_data.get("_id", None)
    else:
        raise ValueError("Responder not found in request data.")

    bot = ChatBot(ID=bot_id)

    prompter, responder = None, None
    if prompter_type in entity_like_classes:
        prompter = entity_like_classes[prompter_type](ID=prompter_id)
    else:
        raise ValueError(f"Prompter type {prompter_type} not found in request data.")

    if responder_type in entity_like_classes:
        responder = entity_like_classes[responder_type](ID=responder_id)
    else:
        raise ValueError(f"Responder type {responder_type} not found in request data.")

    answer = bot.generate_response(user_input, prompter, responder)

    return jsonify({"message": answer})


@query_blueprint.route(ROUTES.ENTITY, methods=["POST"])
def handle_construct_entity() -> Response:
    data = request.json
    entity = Entity(**data)
    response = f"Entity created: {entity.get_name()}"
    return jsonify({"message": response})


@query_blueprint.route(ROUTES.NPC, methods=["POST"])
def handle_construct_npc() -> Response:
    data = request.json
    npc = NPC(**data)
    response = f"NPC created: {npc.get_name()}"
    print(response)
    return jsonify({"message": response})


@query_blueprint.route(ROUTES.PLAYER, methods=["POST"])
def handle_construct_player() -> Response:
    data = request.json
    player = Player(**data)
    response = f"Player created: {player.get_name()}"
    print(response)
    return jsonify({"message": response})


@query_blueprint.route(ROUTES.ALL, methods=["GET"])
def handle_get_all_entity_like() -> Response:

    entities = DB.Entities.find(
        {"race": {"$exists": "1", "$ne": "null", "$ne": "None"}}, {"race": 1}
    )
    npcs = DB.NPCs.find(
        {"name": {"$exists": "1", "$ne": "null", "$ne": "None"}}, {"name": 1}
    )
    players = DB.Players.find(
        {"name": {"$exists": "1", "$ne": "null", "$ne": "None"}}, {"name": 1}
    )

    entities = [
        {"_id": str(e.get("_id")), "name": str(e.get("race")), "type": "Entity"}
        for e in entities
    ]
    npcs = [
        {"_id": str(n.get("_id")), "name": str(n.get("name")), "type": "NPC"}
        for n in npcs
    ]
    players = [
        {"_id": str(p.get("_id")), "name": str(p.get("name")), "type": "Player"}
        for p in players
    ]

    response = {"Entities": entities, "NPCs": npcs, "Players": players}

    return jsonify(response)


@query_blueprint.route(f"{ROUTES.ENTITY}/<string:_id>", methods=["GET"])
def handle_get_entity(_id: str):
    try:
        entity = Entity(ID=_id)
        entity_data = entity.to_dict()
        if not entity_data:
            return jsonify({"message": f"Entity with ID {_id} does not exist."}), 404
        return jsonify(entity_data)
    except Exception as e:
        return jsonify({"message": f"Error retrieving entity: {str(e)}"}), 500


@query_blueprint.route(f"{ROUTES.NPC}/<string:_id>", methods=["GET"])
def handle_get_npc(_id: str) -> Response:
    try:
        npc = NPC(ID=_id)
    except:
        return jsonify({"message": f"NPC with ID {_id} does not exist."})
    response = npc.to_dict()
    return jsonify(response)


@query_blueprint.route(f"{ROUTES.PLAYER}/<string:_id>", methods=["GET"])
def handle_get_player(_id: str) -> Response:
    try:
        player = Player(ID=_id)
    except:
        return jsonify({"message": f"Player with ID {_id} does not exist."})
    response = player.to_dict()
    return jsonify(response)


@query_blueprint.route(f"{ROUTES.BOT}/<string:bot_type>", methods=["POST"])
def handle_construct_bot(bot_type: str) -> Response:
    print("Constructing bot...")
    data = request.json
    if bot_type == "ChatBot":
        bot = ChatBot(**data)
    elif bot_type == "ReasoningBot":
        bot = ReasoningBot(**data)
    else:
        return jsonify({"message": f"Bot type {bot_type} not found."}), 404

    response = f"Bot created: {bot.get_name()}"
    print(response)
    return jsonify({"message": response})


@query_blueprint.route(ROUTES.AGENT, methods=["POST"])
def handle_construct_agent() -> Response:
    print("Constructing agent...")
    data = request.json
    agent = Agent(**data)
    response = f"Agent created: {agent.get_name()}"
    print(response)
    return jsonify({"message": response})


@query_blueprint.route(ROUTES.BOT, methods=["GET"])
def handle_get_all_bots() -> Response:
    bots = DB.Bots.find(
        {"_id": {"$exists": "1", "$ne": "null"}, "name": {"$exists": "1"}}
    )
    bots = [b for b in bots]
    for b in bots:
        b["_id"] = str(b["_id"])
    response = {"Bots": bots}
    return jsonify(response)


@query_blueprint.route(ROUTES.SESSION, methods=["DELETE"])
def handle_clear_all_sessions() -> Response:
    DB.Sessions.delete_many({})
    print("cleared sessions")
    response = f"All Sessions cleared. In collection {DB.name}.{DB.Sessions.name}."
    return jsonify(response)
