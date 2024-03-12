from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.cursor import Cursor
from bson import ObjectId
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Mapping
import gridfs


class DataPool:
    """
    Create a datapool instance that connects to the databank that contains all the saved content
    """
    def __init__(self, uri: str | None = None, dbname: str = "BrainRot"):
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

        EXAMPLE:
        --------
        item = {
            "_id": 1234,
            "info": "yes"
        }
        """
        collection = self._db[collection_name]
        try:
            collection.insert_many(items)
        except Exception as e:
            pass

    def delete_from_collection(self, collection_name: str, collection_filter: Mapping[str, Any]) -> bool:
        """
        Deletes items from a collection set. Selects all items with 'field' that contains a particular 'value'
        :param collection_name: The name of the collection
        :param collection_filter: There are multiple filters that can be done, please check the MongoDB Website for extensive
                        capabilities
        :return: bool

        EXAMPLE:
        --------
        delete_from_collection("TEST_COLLECTION", {'_id': ObjectID("Dsadsad21edasd")})
        Goes to TEST_COLLECTION and deletes any items with '_id': ObjectID(Dsadsad21edasd)

        delete_from_collection("TEST_COLLECTION", {"age" : {"$gt": 26}})
        Goes to TEST_COLLECTION and deletes any items that has the age field and has value greater than 26.

        https://www.mongodb.com/docs/manual/reference/operator/query/
        """

        collection = self._db[collection_name]
        try:
            result = collection.delete_many(collection_filter)
            print(f"Deleted {result.deleted_count} items.")
            return True
        except Exception as e:
            return False

    def get_from_collection(self, collection_name: str, collection_filter: Mapping[str, Any]) -> Cursor:
        """
        Returns all items from a collection given query. You could give a collection name that does not exist, but
        that would always result in a return of 0 items because that collection name will be by default empty.
        :param collection_name: the name of the collection
        :param collection_filter: There are multiple filters that can be done, please check the MongoDB Website
                        for extensive capabilities
        :return: bool

        EXAMPLE:
        --------
        get_from_collection("TEST_COLLECTION", {'_id': ObjectID("Dsadsad21edasd")})
        Goes to TEST_COLLECTION and finds any items with '_id': ObjectID(Dsadsad21edasd)

        get_from_collection("TEST_COLLECTION", {"age" : {"$gt": 26}})
        Goes to TEST_COLLECTION and finds any items that has the age field and has value greater than 26.
        """
        collection = self._db[collection_name]

        try:
            return collection.find(collection_filter)
        except Exception as e:
            print(e)

    def add_video_to_collection(self, collection_name: str = "fs",
                                chunk_size_bytes: int = 261120,
                                filename: str = "test",
                                file_dir: str = "../../final_videos/hello_testing.mp4") -> ObjectId:
        """
        Given the filename and also the directory of the video file, it will store the bytes onto the database
        There is an invariant where there is only one file name in the a collection at a time
        :param collection_name: The collection this video will exist in. If collection doesn't exist it creates one
        :param chunk_size_bytes: the default is 255 KB
        :param filename: The name of the file
        :param file_dir: the directory leading to the file
        :return: returns the Object ID of the file
        """
        fs = gridfs.GridFSBucket(self._db, collection_name, chunk_size_bytes)
        with open(file_dir, "rb") as videoFile:
            file_id = fs.upload_from_stream(
                filename,
                videoFile
            )
            return file_id

    def delete_video_from_collection(self, file_id: ObjectId):
        """
        Given the file_id of the file, we will get rid of all files having the file_id
        :param file_id: the file id
        :return:
        """
        pass

    def get_video_from_collection(self, collection_filter: Mapping[str, Any], collection_name: str = "fs"):
        """
        Given the collection_filter, it grabs all the videos matching the filter. However, if given an empty mapping,
        it will return all videos within the Collection
        :param collection_filter: the filter we want (see below for examples)
        :param collection_name: the name of the collection
        :return:

        EXAMPLES:
        ---------
        collection_filter = {'filename': 'test'} grabs all files that has test as the filename
        collection_filter = {} grabs all files
        collection_filter = {'chunkSize': 261120} grabs all files with chunk sizes of 255 KB
        """

        # first we go to the file collection
        _collection_name = f"{collection_name}.files"
        collection = self._db[_collection_name]


if __name__ == '__main__':
    pool = DataPool()
    # pool.add_to_collection(
    #     collection_name="TEST",
    #     items=[{
    #         "_id": "hello",
    #         "information": "No"
    #     },
    #     ]
    # )
    # pool.delete_from_collection(
    #     collection_name="TEST",
    #     field="dsad",
    #     value="dsada"
    # )
    pool.add_video_to_collection("Videos")
    cursor = pool.get_video_from_collection({}, "Videos")
    for doc in cursor:
        print(doc)