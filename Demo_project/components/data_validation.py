import json
import sys
import os
import yaml
import pandas as pd
from pandas import DataFrame
from pandas.api.types import is_dtype_equal
from typing import Dict, Any ,Tuple
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging
from Demo_project.utils.main_utils import read_yaml_file, write_yaml_file
from Demo_project.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from Demo_project.entity.config_entity import DataValidationConfig
from Demo_project.constants import SCHEMA_FILE_PATH


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_validation_config: configuration for data validation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config =read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise Credit_card_Exception(e,sys)

    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:
        """
        Method Name :   validate_number_of_columns
        Description :   This method validates the number of columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])
            logging.info(f"Is required column present: [{status}]")
            return status
        except Exception as e:
            raise Credit_card_Exception(e, sys)

    def is_column_exist(self, df: DataFrame) -> bool:
        """
        Method Name :   is_column_exist
        Description :   This method validates the existence of a numerical and categorical columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            dataframe_columns = df.columns
            missing_numerical_columns = []
            missing_categorical_columns = []
            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns)>0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")


            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns)>0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            return False if len(missing_categorical_columns)>0 or len(missing_numerical_columns)>0 else True
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e
        
    
    
    def detect_missing_values(self, dataframe: DataFrame) -> bool:
        """Method Name :   detect_missing_values
        Description :   This method validates if there are any missing values in the data
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            missing_values_status = dataframe.isnull().values.any()
            logging.info(f"Missing values detected: {missing_values_status}")
            return missing_values_status
        except Exception as e:
            raise Credit_card_Exception(e, sys)
        

    
    @staticmethod
    def read_data(file_path) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise Credit_card_Exception(e, sys)
        
    

    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame, ) -> bool:
        """
        Method Name :   detect_dataset_drift
        Description :   This method validates if drift is detected
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            data_drift_profile = Profile(sections=[DataDriftProfileSection()])

            data_drift_profile.calculate(reference_df, current_df)

            report = data_drift_profile.json()
            json_report = json.loads(report)

            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)

            n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]
            n_drifted_features = json_report["data_drift"]["data"]["metrics"]["n_drifted_features"]

            logging.info(f"{n_drifted_features}/{n_features} drift detected.")
            drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]
            return drift_status
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e
        


    def detect_duplicates(self, dataframe: DataFrame) -> bool:
        """Method Name :   detect_duplicates
        Description :   This method validates if there are any duplicate values in the data
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            duplicate_values_status = dataframe.duplicated().any()
            logging.info(f"Duplicate values detected: {duplicate_values_status}")
            return duplicate_values_status
        except Exception as e:
            raise Credit_card_Exception(e, sys)
        
    def check_data_types(self, dataframe: DataFrame) -> bool:
        """
        Method Name :   check_data_types
        Description :   This method validates if the data types of the columns match the schema
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            schema_col_dtype = self._schema_config.get("dtypes",{})
            #print(f"schema_data {schema_col_dtype}")
            schema_dtype=list(schema_col_dtype.values())
            schema_col=list(schema_col_dtype.keys())
            df_dtype=[dtype.name for dtype in dataframe.dtypes]
            #print(f"df_dtype {df_dtype}")
            df_col=list(dataframe.columns)
            #print(f"df_col {df_col}")
            # Create a dictionary from df_col and df_dtype
            dataframe_schema = dict(zip(df_col, df_dtype))
            #print(f"dataframe_schema {dataframe_schema}")
            
            mismatched_columns = []
            extra_columns = []
            missing_columns = []
             # Check for mismatched or missing columns
            for column, dtype in schema_col_dtype.items():
                if column not in dataframe_schema:
                    missing_columns.append(column)
                elif dataframe_schema[column] != dtype:
                    mismatched_columns.append(f"{column}: Expected {dtype}, but got {dataframe_schema[column]}")
                    logging.info(f"Data type mismatch for column: {column}, Expected: {dtype}, Found: {dataframe_schema[column]}")
            for column in dataframe_schema.keys():
                if column not in schema_col_dtype:
                    extra_columns.append(column)

            if len(mismatched_columns)>0:
                logging.info(f"schema data column mismatched with dataframe_columns{mismatched_columns}")

            elif len(missing_columns)>0:
                logging.info(f"schema data missing columns in dataframe {missing_columns}.")

            elif len(extra_columns)>0:
                logging.info(f"Extra columns in dataframe: {extra_columns}")
            else:
                logging.info("Schemas data match perfectly! with dataframe data types.")

            return False if len(mismatched_columns)>0 or len(missing_columns)>0 or len(extra_columns)>0 else True
                
                
        except Exception as e:
            raise Credit_card_Exception(e, sys)

            
        
    def rename_columns(self, dataframe: DataFrame) -> bool:
        """
        Method Name :   rename_columns
        Description :   Renames columns based on the schema's column_rename section.
        Output      :   Returns True if column renaming is successful, False otherwise.
        On Failure  :   Logs the exception and raises it.
        """
        try:
            # Access column_rename mapping from schema
            renamed_columns = self._schema_config.get("column_rename", {})
            if not renamed_columns:
                logging.info("No columns to rename as per schema configuration.")
                return True


            # Rename columns in the dataframe
            dataframe.rename(columns=renamed_columns, inplace=True)
            logging.info(f"Columns successfully renamed: {renamed_columns}.")
            return True
        except Exception as e:
            raise Credit_card_Exception(e, sys)
        
    
    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Method Name :   initiate_data_validation
        Description :   This method initiates the data validation component for the pipeline
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """

        try:
            validation_error_msg = ""
            logging.info("Starting data validation")
            train_df, test_df = (DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path),
                                 DataValidation.read_data(file_path=self.data_ingestion_artifact.test_file_path))

            status = self.validate_number_of_columns(dataframe=train_df)
            logging.info(f"All required columns present in training dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."
            status = self.validate_number_of_columns(dataframe=test_df)

            logging.info(f"All required columns present in testing dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in test dataframe."

            status = self.is_column_exist(df=train_df)

            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."
            status = self.is_column_exist(df=test_df)

            if not status:
                validation_error_msg += f"columns are missing in test dataframe."

            status = self.detect_missing_values(dataframe=train_df)
            if status:
                validation_error_msg += "Missing values detected in training dataframe."


            status = self.detect_missing_values(dataframe=test_df)
            if status:
                validation_error_msg += "Missing values detected in test dataframe."

            
            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status = self.detect_dataset_drift(train_df, test_df)
                if drift_status:
                    logging.info(f"Drift detected.")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected in the dataset."
            else:
                logging.info(f"Validation_error: {validation_error_msg}")


            status = self.detect_duplicates(dataframe=train_df)
            if status:
                validation_error_msg += " Duplicates detected in training dataframe."


            status = self.detect_duplicates(dataframe=test_df)
            if status:
                validation_error_msg += "Duplicates detected in test dataframe."

            status = self.check_data_types(dataframe=train_df)
            logging.info(f"all Columns are data type matched in training dataframe: {status}")
            if not status:
                validation_error_msg += "Data type mismatch in training dataframe."


            status = self.check_data_types(dataframe=test_df)
            logging.info(f"all Columns are  data type matched in testing dataframe: {status}")
            if not status:
                validation_error_msg += "Data type mismatch in test dataframe."




             #Rename columns in training dataframe
            status = self.rename_columns(dataframe=train_df)
            logging.info(f"Columns renamed in training dataframe: {status}")
            if not status:
                validation_error_msg += "Column renaming failed in training dataframe."

           # Rename columns in testing dataframe
            status = self.rename_columns(dataframe=test_df)
            logging.info(f"Columns renamed in testing dataframe: {status}")
            if not status:
                validation_error_msg += "Column renaming failed in testing dataframe."        
            

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                message=validation_error_msg,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise  Credit_card_Exception(e, sys) from e