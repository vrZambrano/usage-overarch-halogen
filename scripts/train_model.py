
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set MLflow tracking URI from environment
import mlflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

from src.services.prediction_service import train_and_log_model

if __name__ == "__main__":
    print("Starting model training...")
    train_and_log_model()
    print("Model training finished.")
