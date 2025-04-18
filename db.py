from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime

from config import DATABASE_NAME, MONGO_URI

class MongoDBHandler:
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the MongoDB connection.

        :param connection_string: MongoDB connection string.
        :param database_name: Name of the database to connect to.
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    async def connect(self):
        """
        Connect to the MongoDB server and set up the database and collection.
        """
        try:
            self.client = MongoClient(self.connection_string)
            # Verify the connection
            self.client.admin.command('ping')
            print("Connected to MongoDB successfully!")
            self.db = self.client[self.database_name]
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")

    def insert_document(self,collection:str, document: dict ):
        """
        Insert a single document into the collection.

        :param document: A dictionary representing the document to insert.
        :param collection: A string representing the collection name
        :return: The ID of the inserted document.
        """
        if  self.db == None:
            raise ValueError("Collection not initialized. Call connect() first.")
        try:
            now = datetime.utcnow()
            document['created_date'] = now
            document['last_updated'] = now
            result = self.db[collection].insert_one(document)
            print(f"Inserted document with ID: {result.inserted_id}")
            return result.inserted_id
        except OperationFailure as e:
            print(f"Failed to insert document: {e}")

    def find_documents(self, collection:str, query: dict = None):
        """
        Find documents in the collection that match the query.
        :param collection: The name of the collection.
        :param query: A dictionary representing the query (e.g., {"equipment_id": "machine1"}).
        :return: A list of matching documents.
        """
    
        try:
            if query is None:
                query = {}
            documents = list(self.db[collection].find(query))
            print(f"Found {len(documents)} documents.")
            return jsonable_encoder(documents, custom_encoder={ObjectId: str})
        except OperationFailure as e:
            print(f"Failed to find documents: {e}")
    
    def find_one_document(self, collection:str, query: dict):
        """
        Find a document in the collection that match the query.
        :param collection: The name of the collection.
        :param query: A dictionary representing the query (e.g., {"equipment_id": "machine1"}).
        :return: A  matching document or.
        """
    
        try:
            print("query", self.db)  
            document = self.db[collection].find_one(query)
            return document
        except OperationFailure as e:
            print(f"Failed to find documents: {e}")


    def update_document(self, collection: str, query: dict, update_data: dict):
      """
      Updates a document in the collection, setting the last_updated field.

      :param collection: The name of the collection.
      :param query: A dictionary specifying which document(s) to update.
      :param update_data: A dictionary containing the update operations (e.g., {"$set": {"field": "new_value"}}).
      :return: The result of the update operation.
      """
      if self.db is None:
          raise ValueError("Collection not initialized. Call connect() first.")

      try:
          now = datetime.utcnow()
          update_data["$set"] = {**update_data.get("$set", {}), "last_updated": now} 

          result = self.db[collection].update_one(query, update_data)
          print(f"Updated {result.modified_count} document(s) in {collection}.")
          return result
      except OperationFailure as e:
          print(f"Failed to update document: {e}")
          return None #or raise the exception.
      
    async def close(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
        else:
            print("No active MongoDB connection to close.")
    
    def get_document_count(self, collection:str, query: dict) -> int:
    
        try:
            count = self.db[collection].count_documents({})
            return count
        except OperationFailure as e:
            print(f"Failed to find documents: {e}")
            


database_handler = MongoDBHandler(connection_string=MONGO_URI,database_name=DATABASE_NAME)