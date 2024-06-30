from pymongo import MongoClient
from dnd_ai_be.src.characters import Entity, NPC, Player

# from langchain_core.load.serializable import Serializable
# from langchain_core.documents import Document

from typing import Union
import os

URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/?appName=Cluster91339"
CLIENT = MongoClient(URI)
DB_NAME = 'test_db'
DB = CLIENT[DB_NAME]

# TODO close client during long periods of inactivity.


def db_insert_one(object: Union[Player, NPC, Entity]) -> None:
    '''
    Insert an instance of Entity, NPC, or Player into the database.
    '''

    # check in order of children to parent
    if isinstance(object, Player):
        result = DB.Players.insert_one(object.to_dict())
    elif isinstance(object, NPC):
        result = DB.NPCs.insert_one(object.to_dict())
    elif isinstance(object, Entity):
        result = DB.Entities.insert_one(object.to_dict())
    else:
        raise ValueError("Object must be an instance of Entity, NPC, or Player.")
    
    print(f"Inserted {type(object)} with ID: {result.inserted_id}")