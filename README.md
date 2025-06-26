# Bitcoin Price Tracking Application

This project is a Bitcoin price pipeline application. It utilizes FastAPI to create an API that serves Bitcoin price data. The application collects Bitcoin prices in the background and stores them in a PostgreSQL database. The API exposes endpoints to retrieve the latest price, price history, and price statistics.

## Project Structure

```
/home/zambra/git/usage-overarch-halogen/
├───.env.example
├───.gitignore
├───CLAUDE.md
├───init.sql
├───poetry.lock
├───pyproject.toml
├───README.md
├───requirements.txt
├───.git/...
├───docker/
│   └───docker-compose.yml
├───docs/
├───scripts/
│   └───install-mcp-servers.sh
├───src/
│   ├───__init__.py
│   ├───main.py
│   ├───api/
│   │   ├───__init__.py
│   │   └───routes/
│   ├───core/
│   │   ├───__init__.py
│   │   ├───database.py
│   │   └───__pycache__/
│   ├───models/
│   │   ├───__init__.py
│   │   ├───database.py
│   │   ├───schemas.py
│   │   └───__pycache__/
│   ├───services/
│   │   ├───__init__.py
│   │   ├───databricks.py
│   │   ├───price_collector.py
│   │   └───__pycache__/
│   └───utils/
│       └───__init__.py
└───tests/
    ├───__init__.py
    ├───test_api/
    └───test_services/
```

## Code Explanations

*   **`src/main.py`**: The entry point of the FastAPI application. It defines the API endpoints and manages the background price collection task.
*   **`src/services/price_collector.py`**: This service is responsible for collecting Bitcoin prices from an external source.
*   **`src/core/database.py`**: Manages the database connection and sessions.
*   **`src/models/database.py`**: Defines the SQLAlchemy database model for storing Bitcoin prices.
*   **`src/models/schemas.py`**: Defines the Pydantic schemas for API request and response data validation.
*   **`docker/docker-compose.yml`**: Defines the PostgreSQL service for the database.
*   **`pyproject.toml`**: Defines the project dependencies and metadata.

## How to Run

1.  **Set up the environment:**
    *   Create a `.env` file from the `.env.example` and populate it with your database credentials.
2.  **Start the services:**
    *   Run `docker-compose up -d` to start the PostgreSQL database.
3.  **Install dependencies:**
    *   Run `poetry install` to install the project dependencies.
4.  **Run the application:**
    *   Run `poetry run uvicorn src.main:app --reload` to start the FastAPI application.
