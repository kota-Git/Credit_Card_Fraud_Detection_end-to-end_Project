# Importing necessary libraries
import sys 
import os 
import pymongo
import certifi
from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging
from Demo_project.constants import DATABASE_NAME, MONGODB_URL_KEY , COLLECTION_NAME

# Load the CA certificate file to verify SSL connection with MongoDB server.
ca = certifi.where()

class MongoDBClient:
    """
    class Name: MongoDBClient
    Description: This class handles the connection to the MongoDB database
    output     : connection to MongoDB database
    on Failure : Raises an exception with error message
    """
    client = None
    
    def __init__(self, database_name=DATABASE_NAME) -> None:
        try:
            # Get MongoDB URL from environment variables
            mongo_db_url = os.getenv(MONGODB_URL_KEY)
            if mongo_db_url is None:
                raise Exception(f"environment variable key: {MONGODB_URL_KEY} not set")
            
            # Connect to MongoDB server using the provided URL and CA certificate file
            MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client.get_database(database_name)
            self.database_name = database_name
            logging.info("Connected to MongoDB database successfully")
        except Exception as e:
            raise Credit_card_Exception(e, sys)