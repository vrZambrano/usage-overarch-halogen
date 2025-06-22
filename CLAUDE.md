# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Start PostgreSQL database
cd docker && docker-compose up -d

# Copy environment template and configure
cp .env.example .env
```

### Running the Application
```bash
# Run with Poetry
poetry run python -m src.main

# Run directly  
python src/main.py

# Run with auto-reload for development
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
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

This is a Bitcoin price tracking application with async FastAPI backend that collects prices from Binance API every minute and stores them in PostgreSQL.

### Application Layers

**API Layer** (`src/api/main.py`):
- FastAPI application with REST endpoints for price data
- Background task management for price collection
- Dependency injection for database sessions

**Core Layer** (`src/core/database.py`):
- Database engine and session management
- SQLAlchemy configuration and connection pooling

**Models Layer**:
- `models/database.py`: SQLAlchemy ORM models (BitcoinPrice table)
- `models/schemas.py`: Pydantic response schemas for API serialization

**Services Layer**:
- `services/price_collector.py`: Async Bitcoin price collection from Binance API
- `services/databricks.py`: Optional Databricks integration for analytics

### Data Flow

1. **Price Collection**: Binance API → BitcoinPriceCollector (async task) → PostgreSQL
2. **API Requests**: HTTP Request → FastAPI Route → Database Query → Pydantic Response
3. **Background Processing**: Automatic startup task collects prices every 60 seconds

### Key Components Integration

- **Startup Sequence**: FastAPI app starts → Database connection established → Background price collection task starts
- **Price Storage**: BitcoinPriceCollector fetches prices and saves via SQLAlchemy session
- **API Queries**: Routes use dependency injection to get database sessions and query via ORM

## Database Schema

The `bitcoin_prices` table stores:
- `id`: Primary key
- `price`: Decimal(15,2) Bitcoin price in USD  
- `timestamp`: Price timestamp from API
- `source`: Data source (default: 'binance')
- `created_at`: Record creation timestamp

## Environment Configuration

Required environment variables in `.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bitcoin_db

# Optional Databricks configuration
DATABRICKS_SERVER_HOSTNAME=your-workspace.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=your-access-token
```

## Important Notes

- Uses Poetry for dependency management (pyproject.toml)
- PostgreSQL runs in Docker container via docker-compose
- Background price collection starts automatically with the FastAPI app
- All imports use relative imports within the package structure
- No tests are currently implemented (test directories exist but are empty)
- Application uses async/await patterns throughout for better performance