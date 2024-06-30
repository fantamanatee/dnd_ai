from flask import request, jsonify, Blueprint, Response
from dnd_ai_be.src.characters import Character, NPC, Player

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

def construct_player() -> str:
    '''Construct a player object.
    Returns:
      A JSON response for successful player creation.
    '''
    data = request.json
    name = data.get('name', '')
    description = data.get('description', '')
    player_class = data.get('player_class', '')
    lore = data.get('lore', '')
    character = Character(name, description, player_class, level=1)
    # FIXME add to database

    response = f"Character created: {character}"
    return jsonify({'message': response})

def save_character(character: Character) -> None:
    '''Save a character to the database.
    Args:
      character: A Character object.
    '''
    pass

    
    



    
