# Project Documentation for Bitcoin Price Tracking Application

## Project Overview

This is a FastAPI-based application for tracking Bitcoin prices. The system collects Bitcoin price data from external APIs (specifically Binance) on a regular basis, stores it in a PostgreSQL database, and exposes endpoints to retrieve the latest price, price history, statistics, and predictions.

## Project Structure

```
/home/zambra/git/usage-overarch-halogen/
├───.env.example              # Environment variables template
├───.gitignore                # Git ignore patterns
├───init.sql                  # Database initialization script
├───poetry.lock               # Poetry dependency lock file
├───pyproject.toml            # Project dependencies and configuration
├───README.md                 # Main project documentation
├───requirements.txt          # Python dependencies
├───docker/                   # Docker configuration
│   └───docker-compose.yml    # Docker Compose file for services
├───docs/                     # Documentation files
├───scripts/                  # Utility scripts
│   └───install-mcp-servers.sh # MCP server installation script
├───src/                      # Source code
│   ├───__init__.py
│   ├───main.py               # Entry point for FastAPI application
│   ├───api/                  # API-related code
│   │   ├───__init__.py
│   │   └───routes/           # API routes
│   ├───core/                 # Core application components
│   │   ├───__init__.py
│   │   ├───database.py       # Database connection and session management
│   │   └───__pycache__/      # Python cache
│   ├───models/               # Data models
│   │   ├───__init__.py
│   │   ├───database.py       # SQLAlchemy database models
│   │   ├───schemas.py        # Pydantic validation schemas
│   │   └───__pycache__/      # Python cache
│   ├───services/             # Business logic services
│   │   ├───__init__.py
│   │   ├───databricks.py     # Databricks integration (possibly unused)
│   │   ├───price_collector.py # Bitcoin price collection service
│   │   └───__pycache__/      # Python cache
│   └───utils/                # Utility functions
│       └───__init__.py
└───tests/                    # Test files
    ├───__init__.py
    ├───test_api/             # API tests
    └───test_services/        # Service tests
```

## Key Components

### Main Application (`src/main.py`)
- Entry point for the FastAPI application
- Defines API endpoints for:
  - `/price/latest` - Get the latest Bitcoin price
  - `/price/history` - Get price history with features
  - `/price/predict` - Get price prediction
  - `/price/stats` - Get price statistics
  - `/health` - Health check endpoint
- Manages background price collection using lifespan context manager

### Price Collection Service (`src/services/price_collector.py`)
- Collects Bitcoin price data from Binance API
- Stores collected data in PostgreSQL database
- Runs continuously in the background, collecting data every minute

### Database Layer (`src/core/database.py`, `src/models/database.py`)
- Uses SQLAlchemy with PostgreSQL
- Models Bitcoin price data with fields for price, timestamp, source, and creation time
- Includes database initialization script in `init.sql`

### API Endpoints
1. **`GET /`** - Root endpoint with API information and available endpoints
2. **`GET /price/latest`** - Retrieves the most recent Bitcoin price
3. **`GET /price/history`** - Gets historical price data with engineered features
4. **`GET /price/predict`** - Returns predicted Bitcoin price
5. **`GET /price/stats`** - Provides statistics on price data for a specified time period
6. **`GET /health`** - Checks application health and database connectivity

## Infrastructure

The application uses Docker Compose for deployment with:
1. **PostgreSQL** - Database for storing Bitcoin price data
2. **MLflow** - Machine learning experiment tracking
3. **MinIO** - S3-compatible storage for MLflow artifacts

## Setup Instructions

1. **Environment Configuration:**
   - Copy `.env.example` to `.env`
   - Fill in database credentials and other configuration values

2. **Start Services:**
   - Run `docker-compose up -d` to start PostgreSQL, MLflow, and MinIO services

3. **Install Dependencies:**
   - Run `poetry install` to install Python dependencies

4. **Run Application:**
   - Execute `poetry run uvicorn src.main:app --reload` to start the FastAPI application

## Technologies Used

- **FastAPI** - Framework for building API endpoints
- **PostgreSQL** - Database for storing price data
- **SQLAlchemy** - ORM for database operations
- **AIOHTTP** - Async HTTP client for fetching price data
- **Poetry** - Dependency management
- **Docker** - Containerization of services
- **MLflow** - Machine learning workflow management
- **MinIO** - S3-compatible storage for ML experiments
- **Asyncio** - For asynchronous background processing

## Testing

Test files are organized in the `tests/` directory with:
- API tests in `test_api/`
- Service tests in `test_services/`

## Development Conventions

- Follows Python PEP8 coding standards
- Uses type hints throughout the codebase
- Implements proper error handling and logging
- Utilizes async/await for I/O operations
- Separation of concerns with clear layers (API, services, models, database)