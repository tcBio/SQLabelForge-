"""Data processing and aggregation engine with GPU acceleration support."""

import logging
from typing import Any, Dict, List, Optional, Union
from enum import Enum

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class AggregationType(Enum):
    """Supported aggregation types."""
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VAR = "var"
    FIRST = "first"
    LAST = "last"


class DataProcessor:
    """
    High-performance data processor with GPU acceleration support.

    Features:
    - Efficient data aggregation
    - GPU-accelerated operations (when available)
    - Memory-efficient chunked processing
    - Multiple export formats
    """

    def __init__(self, use_gpu: bool = False, chunk_size: int = 10000):
        """
        Initialize data processor.

        Args:
            use_gpu: Enable GPU acceleration (requires cupy)
            chunk_size: Number of rows to process at once for large datasets
        """
        self.use_gpu = use_gpu
        self.chunk_size = chunk_size

        if use_gpu:
            try:
                import cupy as cp
                self.cp = cp
                logger.info("GPU acceleration enabled")
            except ImportError:
                logger.warning("cupy not found, falling back to CPU")
                self.use_gpu = False
                self.cp = None
        else:
            self.cp = None

    def process_query_results(
        self,
        data: List[Dict[str, Any]],
        group_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, Union[str, AggregationType]]] = None,
    ) -> pd.DataFrame:
        """
        Process and aggregate query results.

        Args:
            data: List of dictionaries from SQL query
            group_by: Columns to group by
            aggregations: Dictionary mapping column names to aggregation functions
                         Example: {"amount": "sum", "count": "count"}

        Returns:
            Processed DataFrame
        """
        df = pd.DataFrame(data)

        if df.empty:
            logger.warning("Empty dataset provided")
            return df

        # Apply aggregations if specified
        if group_by and aggregations:
            # Convert string aggregations to AggregationType
            agg_dict = {}
            for col, agg in aggregations.items():
                if isinstance(agg, str):
                    agg_dict[col] = agg
                elif isinstance(agg, AggregationType):
                    agg_dict[col] = agg.value
                else:
                    agg_dict[col] = agg

            df = df.groupby(group_by).agg(agg_dict).reset_index()
            logger.info(f"Aggregated data by {group_by}")

        return df

    def clean_data(
        self,
        df: pd.DataFrame,
        drop_duplicates: bool = True,
        fill_na: Optional[Dict[str, Any]] = None,
        drop_na: bool = False,
    ) -> pd.DataFrame:
        """
        Clean and prepare data.

        Args:
            df: Input DataFrame
            drop_duplicates: Remove duplicate rows
            fill_na: Dictionary mapping column names to fill values
            drop_na: Drop rows with any NA values

        Returns:
            Cleaned DataFrame
        """
        df = df.copy()

        if drop_duplicates:
            original_len = len(df)
            df = df.drop_duplicates()
            removed = original_len - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} duplicate rows")

        if fill_na:
            df = df.fillna(fill_na)
            logger.info(f"Filled NA values for columns: {list(fill_na.keys())}")

        if drop_na:
            original_len = len(df)
            df = df.dropna()
            removed = original_len - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} rows with NA values")

        return df

    def create_features(
        self,
        df: pd.DataFrame,
        feature_config: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Create new features based on configuration.

        Args:
            df: Input DataFrame
            feature_config: Dictionary defining feature transformations
                Example: {
                    "total_value": {"type": "multiply", "columns": ["price", "quantity"]},
                    "date_year": {"type": "extract_year", "column": "date"}
                }

        Returns:
            DataFrame with new features
        """
        df = df.copy()

        for feature_name, config in feature_config.items():
            feature_type = config.get("type")

            if feature_type == "multiply":
                cols = config["columns"]
                df[feature_name] = df[cols].prod(axis=1)

            elif feature_type == "divide":
                num_col = config["numerator"]
                denom_col = config["denominator"]
                df[feature_name] = df[num_col] / df[denom_col]

            elif feature_type == "extract_year":
                col = config["column"]
                df[feature_name] = pd.to_datetime(df[col]).dt.year

            elif feature_type == "extract_month":
                col = config["column"]
                df[feature_name] = pd.to_datetime(df[col]).dt.month

            elif feature_type == "custom":
                # Allow custom lambda functions
                func = config["function"]
                df[feature_name] = df.apply(func, axis=1)

            logger.info(f"Created feature: {feature_name}")

        return df

    def export_data(
        self,
        df: pd.DataFrame,
        output_path: str,
        format: str = "csv",
        **kwargs
    ):
        """
        Export data to various formats.

        Args:
            df: DataFrame to export
            output_path: Output file path
            format: Export format (csv, parquet, feather, json, excel)
            **kwargs: Additional arguments for export function
        """
        format = format.lower()

        if format == "csv":
            df.to_csv(output_path, index=False, **kwargs)
        elif format == "parquet":
            df.to_parquet(output_path, index=False, **kwargs)
        elif format == "feather":
            df.to_feather(output_path, **kwargs)
        elif format == "json":
            df.to_json(output_path, **kwargs)
        elif format == "excel":
            df.to_excel(output_path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Exported {len(df)} rows to {output_path} ({format})")

    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the dataset.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with dataset statistics
        """
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df) > 0 else {},
        }

        return stats
