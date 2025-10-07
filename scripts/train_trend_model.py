import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set MLflow tracking URI from environment
import mlflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

from services.trend_prediction_service import train_and_log_trend_model

def main():
    """Main function for training the trend classification model"""
    print("=" * 80)
    print("Starting Bitcoin Trend Classification Model Training")
    print("=" * 80)
    print(f"MLflow Tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    print(f"Using XGBoost Classifier with full feature engineering")
    print(f"Target: Classify trend (UP/DOWN) 15 minutes ahead")
    print("=" * 80)
    
    try:
        run_id = train_and_log_trend_model()
        print("\n" + "=" * 80)
        print("✓ Trend model training completed successfully!")
        print(f"✓ Run ID: {run_id}")
        print(f"✓ Experiment: bitcoin_trend_classification")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Check MLflow UI to view training metrics and feature importance")
        print("  2. Test prediction via API endpoint: /trend/predict")
        print("  3. View feature importance via: /trend/feature-importance")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ Error during trend model training:")
        print(f"  {str(e)}")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
