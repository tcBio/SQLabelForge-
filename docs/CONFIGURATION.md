# SQLabelForge Configuration Guide

This guide covers all configuration options for SQLabelForge.

## Configuration Files

SQLabelForge uses multiple configuration sources:

1. **Environment variables** (`.env`) - Credentials and environment-specific settings
2. **YAML configuration** (`config/config.yaml`) - Application settings
3. **Query definitions** (`config/queries.yaml`) - SQL query templates

## Environment Configuration (.env)

### Database Settings

```bash
# Required: SQL Server connection
SQL_SERVER=localhost
SQL_DATABASE=YourDatabase

# Option 1: SQL Authentication
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
SQL_TRUSTED_CONNECTION=false

# Option 2: Windows Authentication
SQL_TRUSTED_CONNECTION=true
```

### Processing Settings

```bash
# GPU acceleration (requires cupy)
USE_GPU=false

# Chunk size for large datasets
CHUNK_SIZE=10000
```

### Labeling Settings

```bash
# Default labeling strategy: manual, rule_based, model_assisted, hybrid
LABELING_STRATEGY=manual

# Default label type: binary, multiclass, multilabel, regression, text
DEFAULT_LABEL_TYPE=binary
```

### Model Settings

```bash
# Model type: oss20b, custom
MODEL_TYPE=oss20b

# Path to model checkpoint
MODEL_PATH=/path/to/model

# Minimum confidence for auto-labeling
MODEL_CONFIDENCE_THRESHOLD=0.8

# Batch size for predictions
MODEL_BATCH_SIZE=32
```

### Export Settings

```bash
# Default export format: csv, parquet, feather, json, excel
EXPORT_FORMAT=csv

# Output directory
OUTPUT_DIRECTORY=output

# Include unlabeled rows in export
INCLUDE_UNLABELED=false
```

### Logging Settings

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path
LOG_FILE=sqlabelforge.log

# Also log to console
LOG_TO_CONSOLE=true
```

### API Settings

```bash
# API server host
API_HOST=0.0.0.0

# API server port
API_PORT=8000

# Auto-reload on code changes (development only)
API_RELOAD=false
```

## Application Configuration (config.yaml)

### Complete Example

```yaml
# Database connection settings
database:
  server: "localhost"
  database: "YourDatabase"
  username: null  # Use environment variable
  password: null  # Use environment variable
  trusted_connection: false

  # Connection pool settings
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30

# Data processor settings
processor:
  use_gpu: false
  chunk_size: 10000

# Labeling settings
labeling:
  default_strategy: "manual"
  default_label_type: "binary"

  # Model-assisted labeling
  model:
    type: "oss20b"
    model_path: null
    confidence_threshold: 0.8
    batch_size: 32

# Export settings
export:
  default_format: "csv"
  output_directory: "output"
  include_unlabeled: false

# Logging settings
logging:
  level: "INFO"
  log_file: "sqlabelforge.log"
  log_to_console: true

# API settings
api:
  host: "0.0.0.0"
  port: 8000
  reload: false
```

### Database Configuration

#### SQL Authentication

```yaml
database:
  server: "sql.example.com"
  database: "ProductionDB"
  username: "app_user"
  password: "${SQL_PASSWORD}"  # From environment
  trusted_connection: false
```

#### Windows Authentication

```yaml
database:
  server: "localhost"
  database: "ProductionDB"
  trusted_connection: true
```

#### Connection Pool Tuning

```yaml
database:
  # Base pool size
  pool_size: 10

  # Max overflow connections
  max_overflow: 20

  # Timeout for acquiring connection (seconds)
  pool_timeout: 60
```

### Processor Configuration

#### CPU-Only Processing

```yaml
processor:
  use_gpu: false
  chunk_size: 10000
```

#### GPU-Accelerated Processing

```yaml
processor:
  use_gpu: true
  chunk_size: 50000  # Larger chunks for GPU
```

### Labeling Configuration

#### Manual Labeling

```yaml
labeling:
  default_strategy: "manual"
  default_label_type: "binary"
```

#### Rule-Based Labeling

```yaml
labeling:
  default_strategy: "rule_based"
  default_label_type: "multiclass"
```

#### Model-Assisted Labeling

```yaml
labeling:
  default_strategy: "model_assisted"
  default_label_type: "binary"

  model:
    type: "oss20b"
    model_path: "/models/oss20b_checkpoint.bin"
    confidence_threshold: 0.85
    batch_size: 64
```

## Query Configuration (queries.yaml)

### Basic Query Definition

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

### Parameterized Query

```yaml
queries:
  orders_by_date_range: |
    SELECT
        OrderID,
        CustomerID,
        OrderDate,
        TotalAmount
    FROM Orders
    WHERE OrderDate >= :start_date
      AND OrderDate <= :end_date
    ORDER BY OrderDate DESC
```

### Complex Query with Joins

```yaml
queries:
  customer_order_summary: |
    SELECT
        c.CustomerID,
        c.CustomerName,
        COUNT(o.OrderID) as TotalOrders,
        SUM(od.Quantity * od.UnitPrice) as TotalRevenue,
        MAX(o.OrderDate) as LastOrderDate
    FROM Customers c
    LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
    LEFT JOIN OrderDetails od ON o.OrderID = od.OrderID
    WHERE o.OrderDate >= :start_date
    GROUP BY c.CustomerID, c.CustomerName
    HAVING COUNT(o.OrderID) > :min_orders
    ORDER BY TotalRevenue DESC
```

### Query Metadata

```yaml
metadata:
  customer_order_summary:
    description: "Get customer order summaries for date range"
    parameters:
      - name: start_date
        type: date
        required: true
        example: "2024-01-01"
      - name: min_orders
        type: integer
        required: false
        default: 1
```

## Advanced Configuration

### Custom Feature Engineering

Define custom features in your code:

```python
feature_config = {
    "total_value": {
        "type": "multiply",
        "columns": ["quantity", "unit_price"]
    },
    "discount_amount": {
        "type": "custom",
        "function": lambda row: row["total_value"] * row["discount_rate"]
    },
    "is_weekend": {
        "type": "custom",
        "function": lambda row: pd.to_datetime(row["date"]).dayofweek >= 5
    }
}

processor = DataProcessor()
df = processor.create_features(df, feature_config)
```

### Custom Labeling Rules

```python
rules = [
    {
        "condition": lambda row: (
            row["revenue"] > 10000 and
            row["orders"] > 5 and
            row["days_since_last_order"] < 30
        ),
        "label": "active_high_value"
    },
    {
        "condition": lambda row: (
            row["revenue"] > 5000 and
            row["days_since_last_order"] < 60
        ),
        "label": "active_medium_value"
    },
    # ... more rules
]

engine = LabelingEngine(label_type=LabelType.MULTICLASS)
df = engine.apply_rule_based_labels(df, rules)
```

### Multiple Export Formats

```python
processor = DataProcessor()

# Export to different formats
processor.export_data(df, "data.csv", format="csv")
processor.export_data(df, "data.parquet", format="parquet")
processor.export_data(df, "data.json", format="json")
processor.export_data(df, "data.xlsx", format="excel")
```

## Configuration Best Practices

### Security

1. **Never commit credentials:**
   ```bash
   # Add to .gitignore
   .env
   config/queries.yaml  # If it contains sensitive queries
   ```

2. **Use environment variables for secrets:**
   ```yaml
   database:
     password: "${SQL_PASSWORD}"  # Read from environment
   ```

3. **Rotate credentials regularly**

### Performance

1. **Tune connection pool based on workload:**
   - High concurrency: Increase `pool_size`
   - Long-running queries: Increase `pool_timeout`

2. **Adjust chunk size based on available memory:**
   - Low memory: Reduce `chunk_size`
   - High memory + GPU: Increase `chunk_size`

3. **Use appropriate query timeouts:**
   ```python
   results = connector.execute_query(query, params, timeout=600)
   ```

### Maintainability

1. **Document your queries:**
   ```yaml
   metadata:
     query_name:
       description: "Clear description"
       parameters: [...]
   ```

2. **Use meaningful query names:**
   - Good: `customer_revenue_last_year`
   - Bad: `query1`

3. **Version your configuration:**
   ```yaml
   # config.yaml
   version: "1.0"
   ```

## Environment-Specific Configuration

### Development

```yaml
# config.dev.yaml
database:
  server: "localhost"
  database: "TestDB"

logging:
  level: "DEBUG"

api:
  reload: true  # Auto-reload on changes
```

### Production

```yaml
# config.prod.yaml
database:
  server: "prod-sql.example.com"
  pool_size: 20

logging:
  level: "INFO"

api:
  reload: false
```

Load environment-specific config:

```python
from sqlabelforge.utils.config_loader import ConfigLoader

config_loader = ConfigLoader(config_path="config/config.prod.yaml")
config = config_loader.load_config()
```

## Troubleshooting

### Configuration Not Loading

1. Check file paths:
   ```python
   import os
   print(os.getcwd())  # Current directory
   ```

2. Verify YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

### Environment Variables Not Working

1. Check .env file location (should be in project root)

2. Manually load .env:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. Verify variable names match exactly

### Connection Pool Issues

If you get connection timeout errors:

```yaml
database:
  pool_size: 10        # Increase
  max_overflow: 20     # Increase
  pool_timeout: 60     # Increase
```

## Additional Resources

- [Quick Start Guide](QUICKSTART.md)
- [API Documentation](API.md)
- [Examples](../examples/)
