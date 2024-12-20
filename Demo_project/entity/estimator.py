import sys

from pandas import DataFrame
from sklearn.pipeline import Pipeline

from Demo_project.exception import Credit_card_Exception
from Demo_project.logger import logging

#class TargetValueMapping:
#   def __init__(self):
#       self.Non_defaulter:int = 0
#       self.defaulter:int = 1
#   def _asdict(self):
#       return self.__dict__
#   def reverse_mapping(self):
#       mapping_response = self._asdict()
#      return dict(zip(mapping_response.values(),mapping_response.keys()))
