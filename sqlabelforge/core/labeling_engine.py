"""Interactive and automated labeling engine for training data."""

import logging
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class LabelType(Enum):
    """Types of labels that can be applied."""
    BINARY = "binary"
    MULTICLASS = "multiclass"
    MULTILABEL = "multilabel"
    REGRESSION = "regression"
    TEXT = "text"


class LabelingStrategy(Enum):
    """Labeling strategies."""
    MANUAL = "manual"
    RULE_BASED = "rule_based"
    MODEL_ASSISTED = "model_assisted"
    HYBRID = "hybrid"


class LabelingEngine:
    """
    Flexible labeling engine for creating training datasets.

    Features:
    - Multiple labeling strategies
    - Rule-based automatic labeling
    - Model-assisted labeling
    - Label validation and quality checks
    - Audit trail for labels
    """

    def __init__(
        self,
        label_type: LabelType = LabelType.BINARY,
        strategy: LabelingStrategy = LabelingStrategy.MANUAL,
    ):
        """
        Initialize labeling engine.

        Args:
            label_type: Type of labels to create
            strategy: Labeling strategy to use
        """
        self.label_type = label_type
        self.strategy = strategy
        self.label_history: List[Dict[str, Any]] = []
        logger.info(f"Labeling engine initialized: {label_type.value}, {strategy.value}")

    def apply_manual_labels(
        self,
        df: pd.DataFrame,
        labels: Dict[int, Any],
        label_column: str = "label",
    ) -> pd.DataFrame:
        """
        Apply manual labels to dataset.

        Args:
            df: Input DataFrame
            labels: Dictionary mapping row indices to label values
            label_column: Name of the label column to create

        Returns:
            DataFrame with labels applied
        """
        df = df.copy()
        df[label_column] = None

        for idx, label in labels.items():
            if idx < len(df):
                df.loc[idx, label_column] = label

                # Record in history
                self.label_history.append({
                    "timestamp": datetime.now(),
                    "row_index": idx,
                    "label": label,
                    "strategy": "manual",
                })

        labeled_count = df[label_column].notna().sum()
        logger.info(f"Applied {labeled_count} manual labels")

        return df

    def apply_rule_based_labels(
        self,
        df: pd.DataFrame,
        rules: List[Dict[str, Any]],
        label_column: str = "label",
    ) -> pd.DataFrame:
        """
        Apply rule-based labels to dataset.

        Args:
            df: Input DataFrame
            rules: List of rule dictionaries with 'condition' and 'label'
                Example: [
                    {"condition": lambda row: row['amount'] > 1000, "label": "high"},
                    {"condition": lambda row: row['amount'] <= 1000, "label": "low"}
                ]
            label_column: Name of the label column to create

        Returns:
            DataFrame with labels applied
        """
        df = df.copy()
        df[label_column] = None

        for rule in rules:
            condition = rule["condition"]
            label = rule["label"]

            # Apply condition
            mask = df.apply(condition, axis=1)
            df.loc[mask, label_column] = label

            labeled_count = mask.sum()
            logger.info(f"Applied rule-based label '{label}' to {labeled_count} rows")

        return df

    def apply_model_assisted_labels(
        self,
        df: pd.DataFrame,
        model_predictions: List[Any],
        confidence_scores: Optional[List[float]] = None,
        confidence_threshold: float = 0.8,
        label_column: str = "label",
        confidence_column: str = "label_confidence",
    ) -> pd.DataFrame:
        """
        Apply model-assisted labels with confidence scores.

        Args:
            df: Input DataFrame
            model_predictions: List of model predictions
            confidence_scores: Optional confidence scores for predictions
            confidence_threshold: Minimum confidence to auto-apply label
            label_column: Name of the label column
            confidence_column: Name of the confidence column

        Returns:
            DataFrame with model-assisted labels
        """
        df = df.copy()
        df[label_column] = None
        df[confidence_column] = None

        for idx, prediction in enumerate(model_predictions):
            if idx >= len(df):
                break

            confidence = confidence_scores[idx] if confidence_scores else 1.0
            df.loc[idx, confidence_column] = confidence

            # Only apply label if confidence exceeds threshold
            if confidence >= confidence_threshold:
                df.loc[idx, label_column] = prediction

                self.label_history.append({
                    "timestamp": datetime.now(),
                    "row_index": idx,
                    "label": prediction,
                    "confidence": confidence,
                    "strategy": "model_assisted",
                })

        labeled_count = df[label_column].notna().sum()
        logger.info(f"Applied {labeled_count} model-assisted labels")

        return df

    def validate_labels(
        self,
        df: pd.DataFrame,
        label_column: str = "label",
        valid_labels: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate labels and return quality metrics.

        Args:
            df: DataFrame with labels
            label_column: Name of the label column
            valid_labels: Optional list of valid label values

        Returns:
            Dictionary with validation results
        """
        total_rows = len(df)
        labeled_rows = df[label_column].notna().sum()
        unlabeled_rows = total_rows - labeled_rows

        validation = {
            "total_rows": total_rows,
            "labeled_rows": int(labeled_rows),
            "unlabeled_rows": int(unlabeled_rows),
            "labeling_completion": labeled_rows / total_rows if total_rows > 0 else 0,
            "label_distribution": df[label_column].value_counts().to_dict(),
        }

        # Check for invalid labels
        if valid_labels:
            invalid_mask = ~df[label_column].isin(valid_labels + [None])
            invalid_count = invalid_mask.sum()
            validation["invalid_labels"] = int(invalid_count)

            if invalid_count > 0:
                logger.warning(f"Found {invalid_count} invalid labels")

        return validation

    def export_labeled_data(
        self,
        df: pd.DataFrame,
        output_path: str,
        label_column: str = "label",
        include_unlabeled: bool = False,
    ):
        """
        Export labeled dataset.

        Args:
            df: DataFrame with labels
            output_path: Output file path
            label_column: Name of the label column
            include_unlabeled: Include rows without labels
        """
        export_df = df.copy()

        if not include_unlabeled:
            export_df = export_df[export_df[label_column].notna()]

        export_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(export_df)} labeled rows to {output_path}")

    def get_labeling_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the labeling process.

        Returns:
            Dictionary with labeling statistics
        """
        total_labels = len(self.label_history)

        if total_labels == 0:
            return {"total_labels": 0}

        strategy_counts = {}
        for entry in self.label_history:
            strategy = entry.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            "total_labels": total_labels,
            "strategy_distribution": strategy_counts,
            "first_label_time": self.label_history[0]["timestamp"],
            "last_label_time": self.label_history[-1]["timestamp"],
        }

    def clear_history(self):
        """Clear labeling history."""
        self.label_history = []
        logger.info("Labeling history cleared")
