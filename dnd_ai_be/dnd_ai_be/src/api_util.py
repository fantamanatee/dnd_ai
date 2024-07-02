from flask import request, jsonify, Blueprint, Response
from dnd_ai_be.src.characters_gutted import NPC, Player, Entity

query_blueprint = Blueprint('query_blueprint', __name__)

@query_blueprint.route('/query', methods=['POST'])
def handle_query() -> Response:
    ''' Handle POST requests to /query endpoint.
    Returns:
      A JSON response.
    '''
    data = request.json
    user_input = data.get('userInput', '')
    from_id = data.get('FROM_ID', '')
    to_id = data.get('TO_ID', '')
    
    response = f"Invalid Input! userInput: {user_input}, FROM_ID: {from_id}, TO_ID: {to_id}"
    return jsonify({'message': response})

# @query_blueprint.route('/player', methods=['POST'])
# def construct_player() -> str:
#     '''Construct a player object.
#     Returns:
#       A JSON response for successful player creation.
#     '''
#     data = request.json
#     player = Player(**data)
#     id = db_insert_one(player)
#     response = f"Player created: {player}, ID: {id}"
#     return jsonify({'message': response})

# @query_blueprint.route('/npc', methods=['POST'])
# def construct_npc() -> str:
#     '''Construct an NPC object.
#     Returns:
#       A JSON response for successful NPC creation.
#     '''
#     data = request.json
#     npc = NPC(**data)
#     id = db_insert_one(npc)
#     response = f"NPC created: {npc}, ID: {id}"
#     return jsonify({'message': response})

@query_blueprint.route('/entity', methods=['POST'])
def construct_entity() -> str:
    '''Construct an Entity object.

    data:
      contains race, tags, description
    Returns:
      A JSON response for successful Entity creation.
    '''
    data = request.json
    entity = Entity(**data) 
    response = f"Entity created: {entity.to_dict()}"
    return jsonify({'message': response})
    
    



    
