import os
import sys

import numpy as np
import pandas as pd
from Demo_project.entity.config_entity import CreditCardPredictorConfig
from Demo_project.entity.S3_estimator import CreditCardEstimator
from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging
from Demo_project.utils.main_utils import read_yaml_file
from pandas import DataFrame


class CreditCardData:
    def __init__(self,
                LIMIT_BAL,
                EDUCATION,
                MARRIAGE,
                PAY_0,
                PAY_2,
                PAY_3,
                PAY_4,
                PAY_5,
                PAY_6,
                BILL_AMT1,
                BILL_AMT6,
                PAY_AMT1,
                PAY_AMT2,
                PAY_AMT3,
                PAY_AMT4,
                PAY_AMT5,
                PAY_AMT6
                ):
        """
        creditcard Data constructor
        Input: all features of the trained model for prediction
        """
        try:
            self.LIMIT_BAL = LIMIT_BAL
            self.EDUCATION = EDUCATION
            self.MARRIAGE = MARRIAGE
            self.PAY_0 = PAY_0
            self.PAY_2 = PAY_2
            self.PAY_3 = PAY_3
            self.PAY_4 = PAY_4
            self.PAY_5 = PAY_5
            self.PAY_6 = PAY_6
            self.BILL_AMT1 = BILL_AMT1
            self.BILL_AMT6 = BILL_AMT6
            self.PAY_AMT1 = PAY_AMT1
            self.PAY_AMT2 = PAY_AMT2
            self.PAY_AMT3 = PAY_AMT3
            self.PAY_AMT4 = PAY_AMT4
            self.PAY_AMT5 = PAY_AMT5
            self.PAY_AMT6 = PAY_AMT6


        except Exception as e:
            raise Credit_card_Exception(e, sys) from e

    def get_CreditCard_input_data_frame(self)-> DataFrame:
        """
        This function returns a DataFrame from CreditcardData class input
        """
        try:
            
            CreditCard_input_dict = self.get_CreditCard_data_as_dict()
            return DataFrame(CreditCard_input_dict)
        
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e


    def get_CreditCard_data_as_dict(self):
        """
        This function returns a dictionary from creditcard Data class input 
        """
        logging.info("Entered get_creditcard_data_as_dict method as creditcardData class")

        try:
            input_data = {
                "LIMIT_BAL": [self.LIMIT_BAL],
                "EDUCATION": [self.EDUCATION],
                "MARRIAGE": [self.MARRIAGE],
                "PAY_0": [self.PAY_0],
                "PAY_2": [self.PAY_2],
                "PAY_3": [self.PAY_3],
                "PAY_4": [self.PAY_4],
                "PAY_5": [self.PAY_5],
                "PAY_6": [self.PAY_6],
                "BILL_AMT1": [self.BILL_AMT1],
                "BILL_AMT6": [self.BILL_AMT6],
                "PAY_AMT1": [self.PAY_AMT1],
                "PAY_AMT2": [self.PAY_AMT2],
                "PAY_AMT3": [self.PAY_AMT3],
                "PAY_AMT4": [self.PAY_AMT4],
                "PAY_AMT5": [self.PAY_AMT5],
                "PAY_AMT6": [self.PAY_AMT6],
                
            }

            logging.info("Created CreditCard data dict")

            logging.info("Exited get_CreditCard_data_as_dict method as CreditCardData class")

            return input_data

        except Exception as e:
            raise Credit_card_Exception(e, sys) from e

class CreditCardClassifier:
    def __init__(self,prediction_pipeline_config: CreditCardPredictorConfig = CreditCardPredictorConfig(),) -> None:
        """
        :param prediction_pipeline_config: Configuration for prediction the value
        """
        try:
            # self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self.prediction_pipeline_config = prediction_pipeline_config
        except Exception as e:
            raise Credit_card_Exception (e, sys)

    def predict(self, dataframe) -> str:
        """
        This is the method of CreditCardClassifier
        Returns: Prediction in string format
        """
        try:
            logging.info("Entered predict method of CreditcardClassifier class")
            model = CreditCardEstimator(
                bucket_name=self.prediction_pipeline_config.model_bucket_name,
                model_path=self.prediction_pipeline_config.model_file_path,
            )
            result =  model.predict(dataframe)
            
            return result
        
        except Exception as e:
            raise Credit_card_Exception(e, sys)