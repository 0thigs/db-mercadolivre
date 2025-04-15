from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config.settings import MONGODB_URI


def get_database():
    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
    return client.mercadolivre
