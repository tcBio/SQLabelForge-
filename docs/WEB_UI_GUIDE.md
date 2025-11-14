# SQLabelForge Web UI Guide

This guide provides comprehensive documentation for the SQLabelForge web-based labeling interface.

## Getting Started

### Starting the Server

```bash
# Start the development server
uvicorn sqlabelforge.api.endpoints:app --reload

# Or start with custom host/port
uvicorn sqlabelforge.api.endpoints:app --host 0.0.0.0 --port 8000
```

Open your browser and navigate to http://localhost:8000

### Interface Overview

The web UI is organized into 4 main steps:

1. **Query** - Build and execute SQL queries
2. **Preview** - Review your dataset
3. **Label** - Interactively label your data
4. **Export** - Download your labeled dataset

## Step 1: Query Builder

### Writing Queries

The query builder supports parameterized queries for SQL injection protection:

```sql
SELECT * FROM customers
WHERE country = :country
  AND signup_date >= :start_date
```

**Parameter Syntax:**
- Use `:parameter_name` for parameters
- Click "Parse Parameters" to automatically detect parameters
- Enter values for each parameter in the generated form

### Query Examples

**Simple Query:**
```sql
SELECT id, name, email, status
FROM users
WHERE status = :status
```

**With Aggregation:**
```sql
SELECT
    category,
    COUNT(*) as count,
    AVG(price) as avg_price
FROM products
WHERE created_at >= :start_date
GROUP BY category
ORDER BY count DESC
```

**With Joins:**
```sql
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id) as order_count,
    SUM(o.total) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.country = :country
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) > :min_orders
```

### Executing Queries

1. Write or paste your SQL query
2. Click "Parse Parameters" to detect parameters
3. Fill in parameter values
4. Click "Execute Query"
5. Review the success message showing row/column count

## Step 2: Data Preview

### Reviewing Your Data

The preview step shows:
- Total row count
- First 100 rows of your dataset
- All columns with proper formatting
- NULL values displayed as italicized "null"

**Actions:**
- **Back to Query** - Return to modify your query
- **Proceed to Labeling** - Move to the labeling interface

## Step 3: Labeling Interface

### Label Configuration

**Labeling Strategy:**
- **Manual** - Label each record individually
- **Rule-Based** - Define rules to auto-label (coming soon)
- **Model-Assisted** - Use ML models to suggest labels (coming soon)

**Label Type:**
- **Binary** - Two classes (e.g., positive/negative)
- **Multi-Class** - Multiple classes (e.g., high/medium/low)
- **Text** - Free-form text labels

### Defining Labels

1. Enter label names in the sidebar (e.g., "Positive", "Negative")
2. Assign keyboard shortcuts (e.g., "1", "2")
3. Click "+ Add Label" for additional labels
4. Labels can be removed using the × button

**Example Label Setup:**
```
Label Name: Positive    Shortcut: 1
Label Name: Negative    Shortcut: 2
Label Name: Neutral     Shortcut: 3
```

### Labeling Records

**Current Record Display:**
- Shows all fields from the current record
- Field names and values clearly separated
- Current position indicator (e.g., "Row 5 / 100")

**Applying Labels:**
- Click a label button
- Or use keyboard shortcuts (1-9)
- The interface auto-advances to the next unlabeled record

**Navigation:**
- **Previous** (←) - Go to previous record
- **Skip** (Space) - Jump to next unlabeled record
- **Next** (→) - Go to next record

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` | Previous record |
| `→` | Next record |
| `1-9` | Apply corresponding label |
| `Space` | Skip to next unlabeled record |

**Shortcuts are only active when not typing in input fields**

### Progress Tracking

The sidebar shows real-time statistics:
- **Total Rows** - Total records in dataset
- **Labeled** - Number of labeled records
- **Remaining** - Unlabeled records
- **Progress Bar** - Visual completion indicator

### Labeling Tips

**Efficient Workflow:**
1. Define all labels before starting
2. Use keyboard shortcuts exclusively for speed
3. Let auto-advance take you to the next record
4. Use "Skip" for uncertain records
5. Review progress regularly

**Best Practices:**
- Label in batches for consistency
- Take breaks to maintain accuracy
- Review a sample of your labels periodically
- Use clear, consistent label names

## Step 4: Export

### Export Options

**Format Selection:**
- **CSV** - Comma-separated values (widely compatible)
- **JSON** - JavaScript Object Notation (structured data)
- **Parquet** - Columnar format (efficient, compressed)
- **Excel** - Microsoft Excel format

**Export Settings:**
- **Filename** - Custom name for your export
- **Include Unlabeled** - Include rows without labels

### Dataset Summary

Before exporting, review:
- Total rows in dataset
- Number of labeled rows
- Completion percentage

### Downloading

1. Select your preferred format
2. Enter a filename (or use default)
3. Choose whether to include unlabeled rows
4. Click "Download Dataset"

The file will be saved to your browser's download location with a `label` column containing your labels.

### Export File Format

**CSV Example:**
```csv
id,name,value,label
1,Product A,100,positive
2,Product B,200,negative
3,Product C,150,positive
```

**JSON Example:**
```json
[
  {
    "id": 1,
    "name": "Product A",
    "value": 100,
    "label": "positive"
  },
  {
    "id": 2,
    "name": "Product B",
    "value": 200,
    "label": "negative"
  }
]
```

## Advanced Features

### Health Monitoring

Click the "Health Check" button in the header to:
- Verify database connectivity
- Check system status
- Monitor the status indicator (green = healthy, red = unhealthy)

### Session Management

The UI uses sessions to store your work:
- Sessions are created when you execute a query
- Your labels are stored in the session
- Sessions persist until the server restarts
- Multiple users can work simultaneously with separate sessions

**Note:** For production use, implement persistent session storage (Redis, database)

### Browser Compatibility

Supported browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features requiring modern browser:**
- CSS Grid and Flexbox
- Fetch API
- ES6 JavaScript
- Local Storage

## Troubleshooting

### Query Execution Issues

**Error: "Query cannot be empty"**
- Ensure you've entered a SQL query
- Check that the query text area isn't blank

**Error: "SQL connector not initialized"**
- Check your database configuration in `.env`
- Verify the server started successfully
- Review server logs for connection errors

**Error: "Query execution failed"**
- Check SQL syntax
- Verify table and column names
- Ensure parameters have valid values
- Check database permissions

### Parameter Issues

**Parameters not detected:**
- Ensure you use `:parameter_name` syntax
- Click "Parse Parameters" button
- Parameters must start with a colon

**Parameter value errors:**
- Match data types (numbers, dates, strings)
- Use proper date format: `YYYY-MM-DD`
- Don't include quotes around parameter values

### Labeling Issues

**Keyboard shortcuts not working:**
- Click outside input fields
- Ensure you're on the Label step
- Check that shortcuts are configured
- Try refreshing the page

**Progress not updating:**
- Check browser console for errors
- Ensure labels are being applied (button highlights)
- Try refreshing and re-executing query

**Auto-advance not working:**
- Verify there are unlabeled records remaining
- Check that labels are properly configured
- Try manual navigation to confirm data loading

### Export Issues

**Download not starting:**
- Check browser's popup blocker settings
- Verify you have labeled data
- Try a different export format
- Check browser console for errors

**File format issues:**
- Ensure the format is supported by your target application
- Try CSV for maximum compatibility
- Use JSON for structured data processing

### Performance Issues

**Large datasets (>10,000 rows):**
- Preview only shows first 100 rows (by design)
- Labeling interface loads one record at a time
- Consider batching your queries for very large datasets
- Export may take longer for large datasets

**Slow query execution:**
- Add indexes to frequently queried columns
- Use WHERE clauses to limit result sets
- Avoid SELECT * for tables with many columns
- Check database server performance

## API Integration

The web UI communicates with these API endpoints:

- `GET /api/health` - Health check
- `POST /api/query/execute-raw` - Execute raw SQL query
- `GET /api/stats` - System statistics

For programmatic access, use these endpoints directly with tools like `curl` or Python's `requests` library.

## Security Considerations

**SQL Injection Protection:**
- Always use parameterized queries (`:param` syntax)
- Never concatenate user input into SQL strings
- The UI enforces parameterized queries

**Authentication:**
- Current version has no built-in authentication
- Use reverse proxy (nginx, Apache) for authentication
- Implement OAuth/SAML for enterprise deployments

**Data Privacy:**
- Sessions are stored in server memory (not persistent)
- No data is sent to external services
- Consider HTTPS for production deployments

## Next Steps

- Explore the [Configuration Guide](CONFIGURATION.md) for advanced settings
- Read the [Quick Start Guide](QUICKSTART.md) for Python API usage
- Check out [examples](../examples/) for more use cases
- Review [claude.md](../claude.md) for development guidelines

## Feedback and Support

- Report issues on GitHub
- Suggest features through discussions
- Contribute improvements via pull requests
