"""
Example using SQLabelForge with the Northwind sample database.

This example demonstrates:
1. Connecting to SQL Server
2. Executing queries
3. Processing data
4. Applying labels
5. Exporting results
"""

import logging
from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor, AggregationType
from sqlabelforge.core.labeling_engine import LabelingEngine, LabelType, LabelingStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run the Northwind example."""

    # Step 1: Connect to SQL Server
    logger.info("Connecting to SQL Server...")
    connector = SQLConnector(
        server="localhost",
        database="Northwind",
        trusted_connection=True,  # Use Windows authentication
    )

    # Test connection
    if not connector.test_connection():
        logger.error("Failed to connect to database")
        return

    # Step 2: Execute a query
    logger.info("Executing query...")
    query = """
    SELECT
        p.ProductID,
        p.ProductName,
        p.CategoryID,
        c.CategoryName,
        p.UnitPrice,
        p.UnitsInStock,
        p.UnitsOnOrder,
        p.Discontinued
    FROM Products p
    LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
    WHERE p.Discontinued = 0
    ORDER BY p.ProductID
    """

    results = connector.execute_query(query)
    logger.info(f"Retrieved {len(results)} products")

    # Step 3: Process data
    logger.info("Processing data...")
    processor = DataProcessor(use_gpu=False)

    # Convert to DataFrame
    df = processor.process_query_results(results)

    # Create features
    feature_config = {
        "total_value": {
            "type": "multiply",
            "columns": ["UnitPrice", "UnitsInStock"]
        },
        "inventory_status": {
            "type": "custom",
            "function": lambda row: (
                "critical" if row["UnitsInStock"] == 0
                else "low" if row["UnitsInStock"] < 10
                else "normal"
            )
        }
    }

    df = processor.create_features(df, feature_config)

    # Get statistics
    stats = processor.get_statistics(df)
    logger.info(f"Dataset statistics: {stats['row_count']} rows, {stats['column_count']} columns")

    # Step 4: Apply rule-based labels
    logger.info("Applying labels...")
    labeling_engine = LabelingEngine(
        label_type=LabelType.MULTICLASS,
        strategy=LabelingStrategy.RULE_BASED
    )

    # Define labeling rules
    rules = [
        {
            "condition": lambda row: row["UnitsInStock"] == 0,
            "label": "out_of_stock"
        },
        {
            "condition": lambda row: row["UnitsInStock"] < 10 and row["UnitsInStock"] > 0,
            "label": "low_stock"
        },
        {
            "condition": lambda row: row["UnitsInStock"] >= 10 and row["UnitsInStock"] < 50,
            "label": "normal_stock"
        },
        {
            "condition": lambda row: row["UnitsInStock"] >= 50,
            "label": "high_stock"
        }
    ]

    df = labeling_engine.apply_rule_based_labels(df, rules, label_column="stock_label")

    # Validate labels
    validation = labeling_engine.validate_labels(df, label_column="stock_label")
    logger.info(f"Labeling validation: {validation}")

    # Step 5: Export results
    logger.info("Exporting results...")
    processor.export_data(df, "output/northwind_labeled_products.csv", format="csv")
    processor.export_data(df, "output/northwind_labeled_products.parquet", format="parquet")

    # Export labeled data only
    labeling_engine.export_labeled_data(
        df,
        "output/northwind_labeled_only.csv",
        label_column="stock_label",
        include_unlabeled=False
    )

    logger.info("Example completed successfully!")

    # Cleanup
    connector.close()


if __name__ == "__main__":
    main()
