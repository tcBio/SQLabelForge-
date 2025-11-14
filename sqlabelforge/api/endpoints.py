"""FastAPI endpoints for SQLabelForge."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from sqlabelforge.core.sql_connector import SQLConnector
from sqlabelforge.core.data_processor import DataProcessor
from sqlabelforge.core.labeling_engine import LabelingEngine, LabelType, LabelingStrategy
from sqlabelforge.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SQLabelForge API",
    description="SQL data labeling and aggregation API",
    version="0.1.0",
)

# Global instances (will be initialized on startup)
config_loader: Optional[ConfigLoader] = None
sql_connector: Optional[SQLConnector] = None
data_processor: Optional[DataProcessor] = None


# Pydantic models for request/response
class QueryRequest(BaseModel):
    """Request model for executing SQL queries."""
    query_name: str = Field(..., description="Name of the query from config")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")
    timeout: int = Field(default=300, description="Query timeout in seconds")


class LabelRequest(BaseModel):
    """Request model for applying labels."""
    data_id: str = Field(..., description="Identifier for the dataset")
    labels: Dict[int, Any] = Field(..., description="Dictionary of row index to label")
    label_column: str = Field(default="label", description="Name of label column")


class RuleLabelRequest(BaseModel):
    """Request model for rule-based labeling."""
    data_id: str = Field(..., description="Identifier for the dataset")
    rules: List[Dict[str, Any]] = Field(..., description="List of labeling rules")
    label_column: str = Field(default="label", description="Name of label column")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global config_loader, sql_connector, data_processor

    try:
        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_config()

        # Initialize SQL connector
        db_config = config.get("database", {})
        sql_connector = SQLConnector(
            server=db_config.get("server"),
            database=db_config.get("database"),
            username=db_config.get("username"),
            password=db_config.get("password"),
            trusted_connection=db_config.get("trusted_connection", False),
        )

        # Initialize data processor
        processor_config = config.get("processor", {})
        data_processor = DataProcessor(
            use_gpu=processor_config.get("use_gpu", False),
            chunk_size=processor_config.get("chunk_size", 10000),
        )

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    if sql_connector:
        sql_connector.close()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SQLabelForge API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "queries": "/queries",
            "execute": "/query/execute",
            "label": "/label/manual",
            "rule_label": "/label/rules",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if sql_connector and sql_connector.test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/queries")
async def list_queries():
    """List available queries from configuration."""
    try:
        if not config_loader:
            raise HTTPException(status_code=500, detail="Config loader not initialized")

        queries = config_loader.get_queries()
        return {
            "queries": list(queries.keys()),
            "count": len(queries),
        }
    except Exception as e:
        logger.error(f"Failed to list queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/execute")
async def execute_query(request: QueryRequest):
    """Execute a SQL query and return results."""
    try:
        if not sql_connector:
            raise HTTPException(status_code=500, detail="SQL connector not initialized")

        if not config_loader:
            raise HTTPException(status_code=500, detail="Config loader not initialized")

        # Get query from config
        queries = config_loader.get_queries()
        query = queries.get(request.query_name)

        if not query:
            raise HTTPException(status_code=404, detail=f"Query '{request.query_name}' not found")

        # Execute query
        results = sql_connector.execute_query(
            query=query,
            params=request.parameters,
            timeout=request.timeout,
        )

        return {
            "query_name": request.query_name,
            "row_count": len(results),
            "data": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/label/manual")
async def apply_manual_labels(request: LabelRequest):
    """Apply manual labels to dataset."""
    try:
        # In a real implementation, this would retrieve the dataset
        # from a session store or database based on data_id
        raise HTTPException(
            status_code=501,
            detail="Manual labeling endpoint not fully implemented yet"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual labeling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/label/rules")
async def apply_rule_labels(request: RuleLabelRequest):
    """Apply rule-based labels to dataset."""
    try:
        # In a real implementation, this would retrieve the dataset
        # and apply the rules
        raise HTTPException(
            status_code=501,
            detail="Rule-based labeling endpoint not fully implemented yet"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rule-based labeling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get system statistics."""
    try:
        return {
            "sql_connector": "initialized" if sql_connector else "not initialized",
            "data_processor": "initialized" if data_processor else "not initialized",
            "gpu_enabled": data_processor.use_gpu if data_processor else False,
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
