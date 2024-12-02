import sys
from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging

from Demo_project.components.data_ingenstion import DataIngestion

from Demo_project.entity.config_entity import (DataIngestionConfig)
                                
from Demo_project.entity.artifact_entity import (DataIngestionArtifact)
                                       


class TrainPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        


    def start_data_ingestion(self) -> DataIngestionArtifact:
        """
        This method of TrainPipeline class is responsible for starting data ingestion component
        """
        try:
            logging.info("Entered the start_data_ingestion method of TrainPipeline class")
            logging.info("Getting the data from mongodb")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Got the train_set and test_set from mongodb")
            logging.info(
                "Exited the start_data_ingestion method of TrainPipeline class"
            )
            return data_ingestion_artifact
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e
    

    def run_pipeline(self,) -> None:
        """
        This method of TrainPipeline class is responsible for running the training pipeline
        """
        try:
            logging.info("Entered the run_pipeline method of TrainPipeline class")
            data_ingestion_artifact = self.start_data_ingestion()
            logging.info("Data Ingestion is done")
            
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e