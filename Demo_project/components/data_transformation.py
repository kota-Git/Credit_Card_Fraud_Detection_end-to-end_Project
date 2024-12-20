import sys
import os
import numpy as np
import pandas as pd
from pandas import DataFrame
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from statsmodels.stats.outliers_influence import variance_inflation_factor

from Demo_project.constants import TARGET_COLUMN, SCHEMA_FILE_PATH
from Demo_project.entity.config_entity import DataTransformationConfig
from Demo_project.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging
from Demo_project.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file, drop_columns
#from Demo_project.entity.estimator import TargetValueMapping


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: Configuration for data transformation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise Credit_card_Exception(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise Credit_card_Exception(e, sys)


    @staticmethod
    def replace_to_zero(df, columns):
        """
        Replace invalid values (-2, -1, 0) in specified columns with 0.
        """
        try:
            for col in columns:
                fil = (df[col] == -2) | (df[col] == -1) | (df[col] == 0)
                df.loc[fil, col] = 0
            return df
        except Exception as e:
            raise Credit_card_Exception(e, sys)
        
    @staticmethod
    def replace_education_values(df):
        """
        Replace values 4, 5, 6 with 0 in the EDUCATION column.
       """
        try:
            df["EDUCATION"] = df["EDUCATION"].replace({4: 0, 5: 0, 6: 0})
            return df
        except Exception as e:
            raise Credit_card_Exception(e, sys)

    @staticmethod
    def replace_marriage_values(df):
       """
       Replace value 0 with 3 in the MARRIAGE column.
       """
       try:
           if "MARRIAGE" in df.columns:
               df["MARRIAGE"] = df["MARRIAGE"].replace({0:3})
           else:
               raise ValueError("Column 'MARRIAGE' not found in DataFrame.")
           return df
       except Exception as e:
            raise Credit_card_Exception(e, sys)
    
        

    

    
    #@staticmethod
    #def remove_outliers(df, columns):
    #   """
    #    Remove outliers using IQR method for specified columns.
    #   """
    #   try:
    #       for col in columns:
    #            Q1 = df[col].quantile(0.25)
    #           Q3 = df[col].quantile(0.75)
    #            IQR = Q3 - Q1
    #            lower_bound = Q1 - 1.5 * IQR
    #            upper_bound = Q3 + 1.5 * IQR
    #            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    #       return df
    #    except Exception as e:
    #        raise Credit_card_Exception(e, sys)


    @staticmethod
    def remove_duplicates(df):
        """
        Remove duplicate rows from the DataFrame.
       """
        try:
            before_count = df.shape[0]
            df = df.drop_duplicates()
            after_count = df.shape[0]
            logging.info(f"Removed {before_count - after_count} duplicate rows.")
            logging.info(f"Removed  duplicate rows.")
            return df
        except Exception as e:
            raise Credit_card_Exception(e, sys)


    def get_data_transformer_object(self) -> Pipeline:
        """
        Method Name :   get_data_transformer_object
        Description :   This method creates and returns a data transformer object for the data
        
        Output      :   data transformer object is created and returned 
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info(
            "Entered get_data_transformer_object method of DataTransformation class"
        )

        try:
            logging.info("Got numerical cols from schema config")

            numeric_transformer = StandardScaler()

             # follow below Pipeline for numerical columns if data has missing values 

            #numeric_transformer = Pipeline(steps=[
            #    ("imputer", SimpleImputer(strategy="median")),  # Impute missing values for numerical columns
            #    ("scaler", StandardScaler())  # Scaling numerical features
            #])

            oh_transformer = OneHotEncoder()      # One-hot encoding for categorical features
        
            # follow below Pipeline for categorical columns if data has missing values

            #oh_transformer = Pipeline(steps=[
            #    ("imputer", SimpleImputer(strategy="most_frequent")),  # Impute missing values for categorical columns
            #    ("one_hot_encoder", OneHotEncoder()),  # One-hot encoding for categorical features
            #    ("scaler", StandardScaler(with_mean=False))  # Scaling categorical features
            #])
           

            ordinal_encoder = OrdinalEncoder()  # Ordinal encoding for specified columns


            logging.info("Initialized StandardScaler, OneHotEncoder, OrdinalEncoder")



            # Get columns from schema configuration
            num_features = self._schema_config['num_features']
            oh_columns = self._schema_config['oh_columns']
            or_columns = self._schema_config['or_columns']
            transform_columns = self._schema_config['transform_columns']


            logging.info("Initialize PowerTransformer")
            transform_pipe = Pipeline(steps=[
                ('transformer', PowerTransformer(method='yeo-johnson'))
            ])

            # Combining all transformations using ColumnTransformer
            preprocessor = ColumnTransformer(
                [
                    ("OneHotEncoder", oh_transformer, oh_columns),
                    ("Ordinal_Encoder", ordinal_encoder, or_columns),
                    ("Transformer", transform_pipe, transform_columns),
                    ("StandardScaler", numeric_transformer, num_features)
                ]
            )
            logging.info("Created preprocessor object from ColumnTransformer")

            logging.info("Exited get_data_transformer_object method of DataTransformation class")

            return preprocessor
        except Exception as e:
            raise Credit_card_Exception(e, sys) from e


    def initiate_data_transformation(self, ) -> DataTransformationArtifact:
        """
        Method Name :   initiate_data_transformation
        Description :   This method initiates the data transformation component for the pipeline 
        
        Output      :   data transformer steps are performed and preprocessor object is created  
        On Failure  :   Write an exception log and then raise an exception
        """

        try:
            if self.data_validation_artifact.validation_status:
                logging.info("Starting data transformation")
                preprocessor = self.get_data_transformer_object()
                logging.info("Got the preprocessor object")

                train_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
                test_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)
                
                #Replace invalid values in specified columns
                target_columns = self._schema_config['replace_invalid_values_in_columns']
                train_df = self.replace_to_zero(train_df, target_columns)
                test_df = self.replace_to_zero(test_df, target_columns)
                
                

                
                


                train_df = self.replace_education_values(train_df)
                test_df = self.replace_education_values(test_df)
                

                train_df = self.replace_marriage_values(train_df)
                test_df = self.replace_marriage_values(test_df)

                train_df = self.remove_duplicates(train_df)
                test_df = self.remove_duplicates(test_df)
                
                input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
                target_feature_train_df = train_df[TARGET_COLUMN]
                
                logging.info("Got train features and test features of Training dataset")

                drop_cols = self._schema_config['drop_columns']

                logging.info("drop the columns in drop_cols of Training dataset")

                input_feature_train_df = drop_columns(df=input_feature_train_df, cols = drop_cols)
                   

                #incase target column categorical, replace with target value mapping with numerical values from estimator.py
                #target_feature_train_df = target_feature_train_df.replace(TargetValueMapping()._asdict())
                target_feature_train_df = target_feature_train_df

                

                input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)

                target_feature_test_df = test_df[TARGET_COLUMN]

                
        

                input_feature_test_df = drop_columns(df=input_feature_test_df, cols = drop_cols)

                logging.info("drop the columns in drop_cols of Test dataset")
                #incase target column categorical, replace with target value mapping with numerical values from estimator.py
                #target_feature_test_df = target_feature_test_df.replace(TargetValueMapping()._asdict() )
                target_feature_test_df = target_feature_test_df 

                logging.info("Got train features and test features of Testing dataset")

                logging.info(
                    "Applying preprocessing object on training dataframe and testing dataframe"
                )
                 
                

                input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)

                logging.info(
                    "Used the preprocessor object to fit transform the train features"
                )

                input_feature_test_arr = preprocessor.transform(input_feature_test_df)

                logging.info("Used the preprocessor object to transform the test features")

                logging.info("Applying SMOTEENN on Training dataset")

                smt = SMOTEENN(sampling_strategy="minority")

                input_feature_train_final, target_feature_train_final = smt.fit_resample(
                    input_feature_train_arr, target_feature_train_df
                )

                logging.info("Applied SMOTEENN on training dataset")

                logging.info("Applying SMOTEENN on testing dataset")

                input_feature_test_final, target_feature_test_final = smt.fit_resample(
                    input_feature_test_arr, target_feature_test_df
                )

                logging.info("Applied SMOTEENN on testing dataset")

                logging.info("Created train array and test array")

                train_arr = np.c_[
                    input_feature_train_final, np.array(target_feature_train_final)
                ]

                test_arr = np.c_[
                    input_feature_test_final, np.array(target_feature_test_final)
                ]

                save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
                save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
                save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)

                logging.info("Saved the preprocessor object")

                logging.info(
                    "Exited initiate_data_transformation method of Data_Transformation class"
                )

                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                    transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                    transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                )
                return data_transformation_artifact
            else:
                raise Exception(self.data_validation_artifact.message)

        except Exception as e:
            raise Credit_card_Exception(e, sys) from e
           