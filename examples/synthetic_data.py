"""
Generate synthetic data for testing SQLabelForge without a database.

This example demonstrates:
1. Creating synthetic datasets
2. Processing without SQL connection
3. Different labeling strategies
4. Model-assisted labeling simulation
"""

import logging
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from sqlabelforge.core.data_processor import DataProcessor, AggregationType
from sqlabelforge.core.labeling_engine import LabelingEngine, LabelType, LabelingStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_synthetic_ecommerce_data(n_rows: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic e-commerce data.

    Args:
        n_rows: Number of rows to generate

    Returns:
        DataFrame with synthetic data
    """
    logger.info(f"Generating {n_rows} synthetic e-commerce records...")

    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # Generate data
    data = {
        "order_id": range(1, n_rows + 1),
        "customer_id": [random.randint(1000, 9999) for _ in range(n_rows)],
        "product_name": [
            random.choice([
                "Laptop", "Mouse", "Keyboard", "Monitor", "Headphones",
                "Webcam", "USB Cable", "Hard Drive", "RAM", "Graphics Card"
            ])
            for _ in range(n_rows)
        ],
        "quantity": [random.randint(1, 10) for _ in range(n_rows)],
        "unit_price": [round(random.uniform(10, 500), 2) for _ in range(n_rows)],
        "order_date": [
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            for _ in range(n_rows)
        ],
        "shipping_country": [
            random.choice(["USA", "UK", "Canada", "Germany", "France", "Japan"])
            for _ in range(n_rows)
        ],
        "payment_method": [
            random.choice(["Credit Card", "PayPal", "Debit Card", "Bank Transfer"])
            for _ in range(n_rows)
        ],
    }

    df = pd.DataFrame(data)
    logger.info(f"Generated {len(df)} records")
    return df


def example_data_processing():
    """Demonstrate data processing capabilities."""
    logger.info("\n=== Data Processing Example ===")

    # Generate data
    df = generate_synthetic_ecommerce_data(500)

    # Initialize processor
    processor = DataProcessor(use_gpu=False, chunk_size=100)

    # Create features
    feature_config = {
        "total_value": {
            "type": "multiply",
            "columns": ["quantity", "unit_price"]
        },
        "order_year": {
            "type": "extract_year",
            "column": "order_date"
        },
        "order_month": {
            "type": "extract_month",
            "column": "order_date"
        },
        "high_value_order": {
            "type": "custom",
            "function": lambda row: row["quantity"] * row["unit_price"] > 500
        }
    }

    df = processor.create_features(df, feature_config)

    # Clean data
    df = processor.clean_data(df, drop_duplicates=True, drop_na=False)

    # Get statistics
    stats = processor.get_statistics(df)
    logger.info(f"Processed data: {stats['row_count']} rows, {stats['column_count']} columns")

    return df


def example_rule_based_labeling(df: pd.DataFrame):
    """Demonstrate rule-based labeling."""
    logger.info("\n=== Rule-Based Labeling Example ===")

    # Initialize labeling engine
    labeling_engine = LabelingEngine(
        label_type=LabelType.MULTICLASS,
        strategy=LabelingStrategy.RULE_BASED
    )

    # Define rules for order priority
    rules = [
        {
            "condition": lambda row: row["total_value"] > 1000,
            "label": "high_priority"
        },
        {
            "condition": lambda row: 500 <= row["total_value"] <= 1000,
            "label": "medium_priority"
        },
        {
            "condition": lambda row: row["total_value"] < 500,
            "label": "low_priority"
        }
    ]

    df = labeling_engine.apply_rule_based_labels(df, rules, label_column="priority")

    # Validate labels
    validation = labeling_engine.validate_labels(df, label_column="priority")
    logger.info(f"Labeling validation: {validation}")
    logger.info(f"Label distribution: {validation['label_distribution']}")

    return df


def example_manual_labeling(df: pd.DataFrame):
    """Demonstrate manual labeling."""
    logger.info("\n=== Manual Labeling Example ===")

    # Initialize labeling engine
    labeling_engine = LabelingEngine(
        label_type=LabelType.BINARY,
        strategy=LabelingStrategy.MANUAL
    )

    # Manually label first 20 records as "fraud" or "legitimate"
    manual_labels = {}
    for i in range(20):
        # Simulate manual labeling (in real scenario, this would be user input)
        # Here we use a simple heuristic for demonstration
        row = df.iloc[i]
        if row["total_value"] > 2000 and row["quantity"] > 8:
            manual_labels[i] = "fraud"
        else:
            manual_labels[i] = "legitimate"

    df = labeling_engine.apply_manual_labels(df, manual_labels, label_column="fraud_label")

    # Get labeling statistics
    stats = labeling_engine.get_labeling_statistics()
    logger.info(f"Labeling statistics: {stats}")

    return df


def example_model_assisted_labeling(df: pd.DataFrame):
    """Demonstrate model-assisted labeling with simulated predictions."""
    logger.info("\n=== Model-Assisted Labeling Example ===")

    # Initialize labeling engine
    labeling_engine = LabelingEngine(
        label_type=LabelType.BINARY,
        strategy=LabelingStrategy.MODEL_ASSISTED
    )

    # Simulate model predictions (in real scenario, these would come from a trained model)
    n_samples = len(df)
    simulated_predictions = [
        "fraud" if random.random() > 0.9 else "legitimate"
        for _ in range(n_samples)
    ]

    # Simulate confidence scores
    simulated_confidences = [
        round(random.uniform(0.6, 1.0), 2)
        for _ in range(n_samples)
    ]

    # Apply model-assisted labels
    df = labeling_engine.apply_model_assisted_labels(
        df,
        model_predictions=simulated_predictions,
        confidence_scores=simulated_confidences,
        confidence_threshold=0.8,
        label_column="fraud_prediction",
        confidence_column="prediction_confidence"
    )

    # Validate labels
    validation = labeling_engine.validate_labels(df, label_column="fraud_prediction")
    logger.info(f"Model-assisted labeling: {validation}")

    return df


def example_data_export(df: pd.DataFrame):
    """Demonstrate various export formats."""
    logger.info("\n=== Data Export Example ===")

    processor = DataProcessor()

    # Export to different formats
    processor.export_data(df, "output/synthetic_data.csv", format="csv")
    processor.export_data(df, "output/synthetic_data.parquet", format="parquet")
    processor.export_data(df, "output/synthetic_data.json", format="json")

    logger.info("Data exported to multiple formats")


def main():
    """Run all synthetic data examples."""
    logger.info("Starting synthetic data examples...\n")

    # Create output directory
    import os
    os.makedirs("output", exist_ok=True)

    # Run examples
    df = example_data_processing()
    df = example_rule_based_labeling(df)
    df = example_manual_labeling(df)
    df = example_model_assisted_labeling(df)
    example_data_export(df)

    logger.info("\nAll examples completed successfully!")
    logger.info(f"Final dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
