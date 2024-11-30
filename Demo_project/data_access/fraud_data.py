# import necessary libraries
import numpy as np
import pandas as pd
import sys
from typing import Optional
from Demo_project.exception import Credit_card_Exception
from Demo_project.constants import DATABASE_NAME
from Demo_project.configuration.mongo_db_connection import MongoDBClient

class Credit_Fraud_Data:
    """
    this class help to export entire Mongo db records as pandas DataFrame 
   """
    def __init__(self):
        """
        initialize MongoDBClient to connect to the database
        """
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise Credit_card_Exception(e, sys)
    
    def export_collection_as_dataframe(self, collection_name:str, database_name:Optional[str]=None)->pd.DataFrame:
        try:
            """
            export entire collectin as dataframe:
            return pd.DataFrame of collection
            """
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client.database[database_name][collection_name]
            
            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na":np.nan}, inplace=True)
            return df
        except Exception as e:
            raise Credit_card_Exception(e, sys)
            
            