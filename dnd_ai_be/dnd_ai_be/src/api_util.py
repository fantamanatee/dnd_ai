from flask import request, jsonify, Blueprint, Response
from dnd_ai_be.src.characters import NPC, Player, Entity, entity_like_classes
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
    bot_data = data.get('bot', None)

    if bot_data:
        bot_id = bot_data.get('_id', None)
    else:
        raise ValueError('Bot not found in request data.')

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
    
    bot = Chatbot(ID=bot_id)
    
    prompter, responder = None, None
    if prompter_type in entity_like_classes:
        prompter = entity_like_classes[prompter_type](ID=prompter_id)
    else:
        raise ValueError(f'Prompter type {prompter_type} not found in request data.')
  
    if responder_type in entity_like_classes:
        responder = entity_like_classes[responder_type](ID=responder_id)
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

    entities = DB.Entities.find({'race':{'$exists':'1', '$ne': 'null', '$ne': 'None'}},{'race':1})
    npcs = DB.NPCs.find({'name':{'$exists':'1', '$ne': 'null', '$ne': 'None'}},{'name':1})
    players = DB.Players.find({'name':{'$exists':'1', '$ne': 'null', '$ne': 'None'}},{'name':1})

    entities = [{'_id': str(e.get('_id')), 'name': str(e.get('race')), 'type':'Entity'} for e in entities]
    npcs = [{'_id': str(n.get('_id')), 'name': str(n.get('name')), 'type':'NPC'} for n in npcs]
    players = [{'_id': str(p.get('_id')), 'name': str(p.get('name')), 'type':'Player'} for p in players]

    response = {
        'Entities': entities,
        'NPCs': npcs,
        'Players': players
    }

    return jsonify(response)

@query_blueprint.route('/entity', methods=['GET'])
def handle_get_entity() -> Response:
    data = request.json
    entity = Entity(**data)
    response = entity.get_data()
    return jsonify(response)

@query_blueprint.route('/bot', methods=['POST'])
def handle_construct_bot() -> Response:
    print('Constructing bot...')
    data = request.json
    bot = Chatbot(**data)
    response = f"Bot created: {bot.get_name()}"
    print(response)
    return jsonify({'message':response})

@query_blueprint.route('/bot', methods=['GET'])
def handle_get_all_bots() -> Response:
    bots = DB.Bots.find({'_id':{'$exists':'1', '$ne': 'null'}, 'name':{'$exists':'1'}})
    bots = [b for b in bots]
    for b in bots:
        b['_id'] = str(b['_id'])
    response = {
        'Bots' : bots
    }
    return jsonify(response)



    
