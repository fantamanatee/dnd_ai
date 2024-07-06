from flask import request, jsonify, Blueprint, Response
from dnd_ai_be.src.characters import NPC, Player, Entity
from dnd_ai_be.src.db_util import DB
from dnd_ai_be.src.chatbot import Chatbot
from time import time
from dnd_ai_be.src.util import timer

query_blueprint = Blueprint('query_blueprint', __name__)

# Time to load bot: 0.37419724464416504
# Time to load entity1: 0.1994762420654297
# Time to load entity2: 0.02063918113708496
# Time to get answer: 2.5123660564422607

@query_blueprint.route('/prompt', methods=['POST'])
@timer()
def handle_prompt() -> Response:
    ''' Handle POST requests to /prompt endpoint.
    Returns:
      A JSON response.
    '''
    data = request.json
    user_input = data.get('userInput', '')

    prompter_data = data.get('prompter', None)
    responder_data = data.get('responder', None)

    if prompter_data:
        prompter_type = prompter_data.get('type', None)
        prompter_id = prompter_data.get('_id', None)
    else:
        raise ValueError('Prompter not found in request data.')
  
    if responder_data:
        responder_type = responder_data.get('type', None)
        responder_id = responder_data.get('_id', None)
    else: 
        raise ValueError('Responder not found in request data.')
    
    # contextualize_q_system_prompt = "Given a chat history and the latest prompt which might reference context in the chat history, formulate a standalone prompt which can be understood without the chat history. Do NOT answer the prompt, just reformulate it if needed and otherwise return it as is."
    # qa_system_prompt = "You are a role playing chatbot for a Dungeons and Dragons game. There are two fictional characters: a prompter and a responder. You must respond to the prompt as if you are the responder. Use the following pieces of retrieved context to answer the prompt. If the context does not apply, respond in a way that makes sense. Use three sentences maximum, and keep the answer concise.\n\n{context}"
    # bot = Chatbot(contextualize_q_system_prompt, qa_system_prompt)
    bot = Chatbot(ID='66860333855efbe743f85ad1')

    entity_classes = {
        'Entity': Entity,
        'NPC': NPC,
        'Player': Player
    }
    
    prompter, responder = None, None
    if prompter_type in entity_classes:
        prompter = entity_classes[prompter_type](ID=prompter_id)
    else:
        raise ValueError(f'Prompter type {prompter_type} not found in request data.')
  
    if responder_type in entity_classes:
        responder = entity_classes[responder_type](ID=responder_id)
    else:
        raise ValueError(f'Responder type {responder_type} not found in request data.')    

    answer = bot.qa(user_input, prompter, responder) 
    
    return jsonify({'message': answer})

@query_blueprint.route('/entity', methods=['POST'])
def handle_construct_entity() -> Response:
    data = request.json
    entity = Entity(**data) 
    response = f"Entity created: {entity.get_name()}"
    return jsonify({'message':response})

@query_blueprint.route('/npc', methods=['POST'])
def handle_construct_npc() -> Response:
    data = request.json
    npc = NPC(**data)
    response = f"NPC created: {npc.get_name()}"
    print(response)
    return jsonify({'message':response})

@query_blueprint.route('/player', methods=['POST'])
def handle_construct_player() -> Response:
    data = request.json
    player = Player(**data)
    response = f"Player created: {player.get_name()}"
    print(response)
    return jsonify({'message':response})

@query_blueprint.route('/all', methods=['GET'])
def handle_get_all_entity_like() -> Response:
    
    entities = DB.Entities.find({'race':{'$exists':'1'}},{'race':1})
    npcs = DB.NPCs.find({'name':{'$exists':'1'}},{'name':1})
    players = DB.Players.find({'name':{'$exists':'1'}},{'name':1})

    entities = [{'_id': str(e.get('_id')), 'name': str(e.get('race')), 'type':'Entity'} for e in entities]
    npcs = [{'_id': str(n.get('_id')), 'name': str(n.get('name')), 'type':'NPC'} for n in npcs]
    players = [{'_id': str(p.get('_id')), 'name': str(p.get('name')), 'type':'Player'} for p in players]

    response = {
        'Entities': entities,
        'NPCs': npcs,
        'Players': players
    }

    return jsonify(response)


    



    
