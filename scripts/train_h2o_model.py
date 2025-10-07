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

from services.h2o_prediction_service import train_and_log_h2o_model

if __name__ == "__main__":
    print("=" * 80)
    print("Starting H2O AutoML Training for Bitcoin Price Prediction")
    print("=" * 80)
    print(f"MLflow Tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    print(f"Using H2O AutoML (tests multiple algorithms automatically)")
    print(f"Target: Predict price 15 minutes ahead")
    print(f"Max Runtime: 5 minutes")
    print(f"Max Models: 20")
    print("=" * 80)
    print("\nH2O AutoML will test the following algorithms:")
    print("  - GBM (Gradient Boosting Machine)")
    print("  - XGBoost")
    print("  - GLM (Generalized Linear Model)")
    print("  - Deep Learning (Neural Networks)")
    print("  - Distributed Random Forest")
    print("  - And automatically select the best model!")
    print("=" * 80)
    
    try:
        run_id, model_type = train_and_log_h2o_model()
        print("\n" + "=" * 80)
        print("✓ H2O AutoML training completed successfully!")
        print(f"✓ Run ID: {run_id}")
        print(f"✓ Best Model Type: {model_type}")
        print(f"✓ Experiment: bitcoin_h2o_automl")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Check MLflow UI to view the leaderboard and model comparison")
        print("  2. Test prediction via API endpoint: /price/predict/h2o")
        print("  3. Compare with XGBoost model: /price/predict/next")
        print("  4. View leaderboard via: /h2o/leaderboard")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ Error during H2O AutoML training:")
        print(f"  {str(e)}")
        print("=" * 80)
        sys.exit(1)
