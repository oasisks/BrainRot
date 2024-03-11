import pymongo.mongo_client
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from typing import List, Dict, Generic


class DataPool:
    """
    Create a datapool instance that connects to the databank that contains all the saved content
    """
    def __init__(self, uri:str | None = None, dbname: str = "BrainRot"):
        """
        Establishes a connection to the MongoDB data cluster
        :param uri: by default it will be None and use the default datapool. Can pass in another URI if there
                    are other clusters.
        """
        load_dotenv()
        default_password = os.getenv("MONGO_PASSWORD")
        default_uri = (f"mongodb+srv://brinitial:{default_password}@brainrotdatapool.ott0cjw.mongodb.net/?retryWrites"
                       f"=true&w=majority&appName=BrainRotDataPool")
        self._uri = uri if uri is not None else default_uri

        self._client = MongoClient(self._uri, server_api=ServerApi('1'))
        try:
            self._client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self._db = self._client[dbname]

    def add_to_collection(self, collection_name, items: List[Dict]) -> bool:
        """
        Adds items to a collection set. If the collection name does not exist, it will create a new collection
        with that name. If success will return True else False
        :param collection_name: The name of the collection
        :param items: A list of items to be added into the collection
                        The items should also include an '_id' key associated with it else the '_id' will be
                        automatically generated
        :return: bool
        """
        collection = self._db[collection_name]
        collection.insert_many(items)


if __name__ == '__main__':
    pool = DataPool()
    pool.add_to_collection(
        collection_name="TEST",
        items=[{
            "_id": "helo",
            "information": "yes"
        }]
    )
