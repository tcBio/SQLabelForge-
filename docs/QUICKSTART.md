# SQLabelForge Quick Start Guide

This guide will help you get started with SQLabelForge in minutes.

## Prerequisites

- Python 3.9 or higher
- SQL Server with ODBC Driver 17 for SQL Server
- Basic knowledge of SQL and Python

## Installation

### Option 1: Install from source

```bash
git clone https://github.com/yourusername/SQLabelForge.git
cd SQLabelForge
pip install -e .
```

### Option 2: Install with development tools

```bash
pip install -e ".[dev]"
```

### Option 3: Install with GPU support

```bash
pip install -e ".[gpu]"
```

## Initial Configuration

### 1. Set up environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your SQL Server credentials:

```bash
SQL_SERVER=localhost
SQL_DATABASE=YourDatabase
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
SQL_TRUSTED_CONNECTION=false
```

**For Windows Authentication:**

```bash
SQL_SERVER=localhost
SQL_DATABASE=YourDatabase
SQL_TRUSTED_CONNECTION=true
```

### 2. Configure application settings

Copy the configuration templates:

```bash
cp config/config.template.yaml config/config.yaml
cp config/queries.template.yaml config/queries.yaml
```

Edit `config/config.yaml` to customize:
- Database connection settings
- Processing options
- Labeling strategies
- Export preferences

### 3. Define your queries

Edit `config/queries.yaml` to add your SQL queries:

```yaml
queries:
  get_customers: |
    SELECT
        CustomerID,
        CustomerName,
        Country
    FROM Customers
    WHERE Country = :country
```

## Your First Project

### Example 1: Simple Query and Export

```python
from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor

# Connect to database
connector = SQLConnector(
    server="localhost",
    database="Northwind",
    trusted_connection=True
)

# Execute query
query = "SELECT * FROM Customers"
results = connector.execute_query(query)

# Process and export
processor = DataProcessor()
df = processor.process_query_results(results)
processor.export_data(df, "customers.csv")

# Cleanup
connector.close()
```

### Example 2: Parameterized Query

```python
from sqlabelforge.core.sql_connector import SQLConnector

connector = SQLConnector(
    server="localhost",
    database="Northwind",
    trusted_connection=True
)

# Query with parameters (SQL injection safe)
query = """
SELECT * FROM Orders
WHERE CustomerID = :customer_id
  AND OrderDate >= :start_date
"""

results = connector.execute_query(
    query,
    {
        "customer_id": "ALFKI",
        "start_date": "2024-01-01"
    }
)

print(f"Found {len(results)} orders")
connector.close()
```

### Example 3: Rule-Based Labeling

```python
from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor
from sqlabelforge.core.labeling_engine import LabelingEngine, LabelType

# Connect and query
connector = SQLConnector(
    server="localhost",
    database="Northwind",
    trusted_connection=True
)

query = """
SELECT
    ProductID,
    ProductName,
    UnitPrice,
    UnitsInStock
FROM Products
"""

results = connector.execute_query(query)

# Process data
processor = DataProcessor()
df = processor.process_query_results(results)

# Create labeling engine
labeling_engine = LabelingEngine(label_type=LabelType.MULTICLASS)

# Define rules
rules = [
    {"condition": lambda row: row["UnitsInStock"] == 0, "label": "out_of_stock"},
    {"condition": lambda row: 0 < row["UnitsInStock"] < 10, "label": "low_stock"},
    {"condition": lambda row: row["UnitsInStock"] >= 10, "label": "in_stock"}
]

# Apply labels
df = labeling_engine.apply_rule_based_labels(df, rules)

# Export
processor.export_data(df, "labeled_products.csv")

# Cleanup
connector.close()
```

### Example 4: Using the REST API

Start the API server:

```bash
uvicorn sqlabelforge.api.endpoints:app --reload
```

Then use curl or any HTTP client:

```bash
# Health check
curl http://localhost:8000/health

# List available queries
curl http://localhost:8000/queries

# Execute a query
curl -X POST http://localhost:8000/query/execute \
  -H "Content-Type: application/json" \
  -d '{
    "query_name": "get_customers",
    "parameters": {"country": "USA"}
  }'
```

## Running Examples

### Synthetic Data Example (No Database Required)

```bash
python examples/synthetic_data.py
```

This will:
1. Generate synthetic e-commerce data
2. Process and create features
3. Apply various labeling strategies
4. Export to multiple formats

### Northwind Database Example

```bash
python examples/northwind_example.py
```

This requires the Northwind sample database.

## Common Use Cases

### Use Case 1: Extract and Label Customer Data

```python
from sqlabelforge import SQLConnector, DataProcessor, LabelingEngine, LabelType

# Connect
connector = SQLConnector(server="localhost", database="Sales", trusted_connection=True)

# Query
results = connector.execute_query("""
    SELECT CustomerID, TotalRevenue, OrderCount, DaysSinceLastOrder
    FROM CustomerMetrics
""")

# Process
processor = DataProcessor()
df = processor.process_query_results(results)

# Label
engine = LabelingEngine(label_type=LabelType.BINARY)
rules = [
    {"condition": lambda r: r["TotalRevenue"] > 10000 and r["DaysSinceLastOrder"] < 30,
     "label": "active_high_value"},
    {"condition": lambda r: r["TotalRevenue"] <= 10000 or r["DaysSinceLastOrder"] >= 30,
     "label": "other"}
]
df = engine.apply_rule_based_labels(df, rules)

# Export
processor.export_data(df, "customer_segments.parquet", format="parquet")
connector.close()
```

### Use Case 2: Feature Engineering

```python
from sqlabelforge import DataProcessor

processor = DataProcessor()

# Define feature transformations
features = {
    "total_value": {
        "type": "multiply",
        "columns": ["quantity", "unit_price"]
    },
    "discount_amount": {
        "type": "multiply",
        "columns": ["total_value", "discount_rate"]
    },
    "order_year": {
        "type": "extract_year",
        "column": "order_date"
    }
}

df = processor.create_features(df, features)
```

## Next Steps

- Read the [Configuration Guide](CONFIGURATION.md) for advanced settings
- Explore the API documentation
- Check out more examples in the `examples/` directory
- Join our community discussions

## Troubleshooting

### Connection Issues

If you can't connect to SQL Server:

1. Verify ODBC Driver 17 is installed:
   ```bash
   odbcinst -q -d
   ```

2. Test connection with pyodbc:
   ```python
   import pyodbc
   print(pyodbc.drivers())
   ```

3. Check SQL Server authentication mode and firewall settings

### Import Errors

If you get import errors:

```bash
pip install --upgrade -e .
```

### GPU Support Issues

If GPU acceleration isn't working:

```bash
pip install cupy-cuda11x  # Replace 11x with your CUDA version
```

## Getting Help

- Check the [full documentation](../README.md)
- Open an issue on GitHub
- Join our community discussions
