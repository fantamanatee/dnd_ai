from pymongo import MongoClient
from dnd_ai_be.src.characters import Entity, NPC, Player

# from langchain_core.load.serializable import Serializable
# from langchain_core.documents import Document

from typing import Union, List
import os

# URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/?appName=Cluster91339"
URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/test_db?retryWrites=true&w=majority"


URI_with_options = f"{URI}&ssl=true&connectTimeoutMS=30000&socketTimeoutMS=30000"

# CLIENT = MongoClient(URI)
CLIENT = MongoClient(URI_with_options)

DB_NAME = 'test_db'
DB = CLIENT[DB_NAME]

# TODO close client during long periods of inactivity.
