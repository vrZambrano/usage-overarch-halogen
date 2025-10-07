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

from services.prediction_service import train_and_log_model

def main():
    """Main function for training the price prediction model"""
    print("=" * 80)
    print("Starting Bitcoin Price Prediction Model Training")
    print("=" * 80)
    print(f"MLflow Tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    print(f"Using XGBoost Regressor with full feature engineering")
    print(f"Target: Predict price 15 minutes ahead")
    print("=" * 80)
    
    try:
        run_id = train_and_log_model()
        print("\n" + "=" * 80)
        print("✓ Model training completed successfully!")
        print(f"✓ Run ID: {run_id}")
        print(f"✓ Experiment: bitcoin_price_prediction")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Check MLflow UI to view training metrics")
        print("  2. Test prediction with: python scripts/predict_example.py")
        print("  3. Start API server to expose predictions")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ Error during model training:")
        print(f"  {str(e)}")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
