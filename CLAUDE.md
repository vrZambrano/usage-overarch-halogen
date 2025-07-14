# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Start services (PostgreSQL, MLflow, MinIO)
cd docker && docker compose up -d

# Copy environment template and configure
cp .env.example .env

# Create MLflow S3 bucket in MinIO (run after services are up)
docker exec bitcoin_minio mc alias set local http://localhost:9000 minio minio123
docker exec bitcoin_minio mc mb local/mlflow
```

### Running the Application
```bash
# Run with Poetry
poetry run python -m src.main

# Run directly  
python src/main.py

# Run with auto-reload for development
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Machine Learning
```bash
# Train and log model to MLflow
poetry run python scripts/train_model.py

# View MLflow UI
# MLflow is accessible at: http://localhost:5001
```

### Package Management
```bash
# Add new dependency
poetry add package_name

# Remove dependency
poetry remove package_name

# Update dependencies
poetry update
```

## Architecture Overview

This is a Bitcoin price tracking and prediction application with async FastAPI backend that collects prices from Binance API, stores them in PostgreSQL, and provides ML-powered price predictions using MLflow for model management.

### Application Layers

**API Layer** (`src/main.py`):
- FastAPI application with REST endpoints for price data and predictions
- Background task management for price collection
- Dependency injection for database sessions
- Health check and monitoring endpoints

**Core Layer** (`src/core/database.py`):
- Database engine and session management
- SQLAlchemy configuration and connection pooling

**Models Layer**:
- `models/database.py`: SQLAlchemy ORM models (BitcoinPrice table)
- `models/schemas.py`: Pydantic schemas for API serialization and feature engineering

**Services Layer**:
- `services/price_collector.py`: Async Bitcoin price collection from Binance API
- `services/bitcoin_service.py`: Business logic for price data and feature engineering
- `services/prediction_service.py`: ML model training and prediction using MLflow
- `services/databricks.py`: Optional Databricks integration for analytics

**Scripts Layer**:
- `scripts/train_model.py`: Standalone script for training ML models

### Data Flow

1. **Price Collection**: Binance API → BitcoinPriceCollector (async task) → PostgreSQL
2. **API Requests**: HTTP Request → FastAPI Route → BitcoinService → Database Query → Pydantic Response
3. **Feature Engineering**: Raw price data → Lag features, Moving averages → ML-ready dataset
4. **ML Pipeline**: Historical data → Feature engineering → Model training → MLflow → Predictions
5. **Background Processing**: Automatic startup task collects prices every 60 seconds

### Key Components Integration

- **Startup Sequence**: FastAPI app starts → Database connection established → Background price collection task starts
- **Price Storage**: BitcoinPriceCollector fetches prices and saves via SQLAlchemy session
- **API Queries**: Routes use dependency injection to get database sessions and query via BitcoinService
- **Feature Engineering**: BitcoinService creates lag features and moving averages for time series forecasting
- **ML Integration**: MLflow manages model lifecycle, MinIO stores artifacts, predictions served via API

## API Endpoints

- `GET /`: API information and available endpoints
- `GET /price/latest`: Latest recorded Bitcoin price
- `GET /price/history`: Price history with engineered features for ML
- `GET /price/stats`: Price statistics for specified period
- `GET /price/predict`: ML-powered price prediction
- `GET /health`: Health check for application, database, and collector status

## Database Schema

The `bitcoin_prices` table stores:
- `id`: Primary key
- `price`: Decimal(15,2) Bitcoin price in USD  
- `timestamp`: Price timestamp from API
- `source`: Data source (default: 'binance')
- `created_at`: Record creation timestamp

## MLflow Integration

- **Model Training**: Linear regression model trained on engineered features
- **Feature Engineering**: Lag features (price_t-1 to price_t-5) and moving averages (ma_10)
- **Model Storage**: Models stored in MLflow with S3-compatible MinIO backend (experiment: `bitcoin_prediction_s3`)
- **Artifact Storage**: Uses MinIO S3 bucket (`s3://mlflow/`) instead of local filesystem
- **Input Examples**: Models logged with input examples to enable automatic signature inference
- **Prediction**: Latest trained model used for price predictions via API

## Environment Configuration

Required environment variables in `.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bitcoin_db

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5001
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123

# Optional Databricks configuration
DATABRICKS_SERVER_HOSTNAME=your-workspace.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=your-access-token
```

## Docker Services

The application uses docker-compose with three services:
- **PostgreSQL**: Database for price storage
- **MLflow**: Model tracking and registry
- **MinIO**: S3-compatible object storage for MLflow artifacts

## Important Notes

- Uses Poetry for dependency management (pyproject.toml)
- PostgreSQL, MLflow, and MinIO run in Docker containers via docker compose
- Background price collection runs automatically with the FastAPI app
- All imports use relative imports within the package structure
- MLflow provides experiment tracking and model management with S3 artifact storage
- Feature engineering includes lag features and moving averages for time series forecasting
- Models use the `bitcoin_prediction_s3` experiment with MinIO S3 backend
- Decimal types are automatically converted to float for ML model compatibility
- No tests are currently implemented (test directories exist but are empty)
- Application uses async/await patterns throughout for better performance

## Troubleshooting

### MLflow Issues
- If model training fails with permission errors, ensure MinIO bucket is created: `docker exec bitcoin_minio mc mb local/mlflow`
- Models are stored in the `bitcoin_prediction_s3` experiment, not the original `bitcoin_prediction`
- MLflow server is configured to use MinIO S3 storage at `s3://mlflow/` for artifacts