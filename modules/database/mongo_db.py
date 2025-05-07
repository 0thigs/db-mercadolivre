from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database


class MongoDBConnection:
    _client = None
    _db = None

    @classmethod
    def get_database(cls) -> Database:
        if cls._db is None:
            cls._client = MongoClient(
                "mongodb+srv://admin:banana10@ml-database.fkyncut.mongodb.net/?retryWrites=true&w=majority&appName=ML-Database",
                server_api=ServerApi("1"),
            )
            cls._db = cls._client["mercadolivre"]
        return cls._db

    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.get_database()[collection_name]
