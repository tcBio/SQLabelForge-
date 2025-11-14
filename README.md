# SQLabelForge

A high-performance, open-source tool for querying SQL Server databases and creating labeled training datasets with OSS20B integration.

## Features

- 🚀 **GPU-accelerated data processing** - Leverage GPU power for faster data transformations
- 🔒 **Secure SQL query management** - Built-in SQL injection protection with parameterized queries
- 🏷️ **Interactive labeling interface** - Multiple labeling strategies (manual, rule-based, model-assisted)
- 🤖 **OSS20B model integration** - Automated labeling with confidence scoring
- 📊 **Advanced data aggregation** - Powerful data processing and feature engineering
- 💾 **Multiple export formats** - Export to CSV, Parquet, JSON, Excel, and Feather

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/SQLabelForge.git
cd SQLabelForge
pip install -e .
```

### Basic Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your SQL connection in `.env`:**
   ```bash
   SQL_SERVER=your_server
   SQL_DATABASE=your_database
   SQL_USERNAME=your_username
   SQL_PASSWORD=your_password
   ```

3. **Create your query configuration:**
   ```bash
   cp config/config.template.yaml config/config.yaml
   cp config/queries.template.yaml config/queries.yaml
   ```

4. **Run the example:**
   ```bash
   python examples/synthetic_data.py
   ```

## Usage

### Python API

```python
from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor
from sqlabelforge.core.labeling_engine import LabelingEngine, LabelType

# Connect to SQL Server
connector = SQLConnector(
    server="localhost",
    database="YourDatabase",
    trusted_connection=True
)

# Execute query
results = connector.execute_query(
    "SELECT * FROM customers WHERE country = :country",
    {"country": "USA"}
)

# Process data
processor = DataProcessor(use_gpu=False)
df = processor.process_query_results(results)

# Apply labels
labeling_engine = LabelingEngine(label_type=LabelType.BINARY)
rules = [
    {"condition": lambda row: row["revenue"] > 10000, "label": "high_value"},
    {"condition": lambda row: row["revenue"] <= 10000, "label": "low_value"}
]
df = labeling_engine.apply_rule_based_labels(df, rules)

# Export
processor.export_data(df, "output/labeled_data.csv")
```

### REST API

Start the API server:

```bash
uvicorn sqlabelforge.api.endpoints:app --reload
```

Access the API at `http://localhost:8000`

API endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `GET /queries` - List available queries
- `POST /query/execute` - Execute a query
- `POST /label/manual` - Apply manual labels
- `POST /label/rules` - Apply rule-based labels

## Configuration

See [CONFIGURATION.md](docs/CONFIGURATION.md) for detailed setup instructions.

## Examples

### Northwind Database Example

```bash
python examples/northwind_example.py
```

This example demonstrates:
- Connecting to SQL Server
- Querying product data
- Creating features
- Applying rule-based labels
- Exporting results

### Synthetic Data Example

```bash
python examples/synthetic_data.py
```

This example demonstrates:
- Generating synthetic e-commerce data
- Data processing and feature engineering
- Multiple labeling strategies
- Model-assisted labeling simulation
- Various export formats

## Project Structure

```
SQLabelForge/
├── sqlabelforge/              # Main package
│   ├── __init__.py
│   ├── core/                  # Core functionality
│   │   ├── sql_connector.py   # SQL Server connector
│   │   ├── data_processor.py  # Data processing engine
│   │   ├── labeling_engine.py # Labeling strategies
│   │   └── model_interface.py # Model integration
│   ├── api/                   # REST API
│   │   └── endpoints.py
│   └── utils/                 # Utilities
│       └── config_loader.py
├── config/                    # Configuration templates
├── examples/                  # Usage examples
├── tests/                     # Test suite
├── docs/                      # Documentation
├── .env.example              # Environment template
├── pyproject.toml            # Package configuration
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Development

### Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Run tests:

```bash
pytest tests/
```

### Code formatting:

```bash
black sqlabelforge/
isort sqlabelforge/
```

### Type checking:

```bash
mypy sqlabelforge/
```

## Requirements

- Python 3.9+
- SQL Server (with ODBC Driver 17+)
- pandas >= 2.0.0
- sqlalchemy >= 2.0.0
- fastapi >= 0.100.0

### Optional:
- cupy >= 12.0.0 (for GPU acceleration)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/SQLabelForge/issues)
- 💬 [Discussions](https://github.com/yourusername/SQLabelForge/discussions)

## Roadmap

- [ ] Web-based labeling interface
- [ ] Support for additional databases (PostgreSQL, MySQL)
- [ ] Active learning integration
- [ ] Label quality metrics and validation
- [ ] Collaborative labeling features
- [ ] Integration with popular ML frameworks

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [pandas](https://pandas.pydata.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [pyodbc](https://github.com/mkleehammer/pyodbc)

---

**Note:** This project is under active development. APIs may change in future versions.
