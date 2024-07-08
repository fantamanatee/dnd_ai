from pymongo import MongoClient
import ssl
import os

# URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/?appName=Cluster91339"
URI = f"mongodb+srv://{os.getenv('DND_AI_DB_USER')}:{os.getenv('DND_AI_DB_PWD')}@cluster91339.czkmuen.mongodb.net/test_db?retryWrites=true&w=majority"


URI_with_options = f"{URI}&ssl=true&connectTimeoutMS=10000&socketTimeoutMS=10000"

# CLIENT = MongoClient(URI)
CLIENT = MongoClient(URI_with_options, tlsAllowInvalidCertificates=True)

DB_NAME = 'test_db'
DB = CLIENT[DB_NAME]

# TODO close client during long periods of inactivity.
