"""
SQLabelForge: SQL data labeling and aggregation tool for ML training.

A high-performance, open-source tool for querying SQL Server databases
and creating labeled training datasets with OSS20B integration.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor
from sqlabelforge.core.labeling_engine import LabelingEngine
from sqlabelforge.core.model_interface import ModelInterface

__all__ = [
    "SQLConnector",
    "DataProcessor",
    "LabelingEngine",
    "ModelInterface",
]
