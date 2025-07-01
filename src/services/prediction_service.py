
import mlflow
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session
import os

from services.bitcoin_service import bitcoin_service
from core.database import get_db

def _setup_mlflow():
    """Setup MLflow configuration from environment variables."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
    mlflow.set_tracking_uri(tracking_uri)
    
    s3_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL")
    if s3_endpoint:
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = s3_endpoint
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if aws_access_key and aws_secret_key:
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key


def train_and_log_model():
    """
    Trains a simple linear regression model and logs it to MLflow.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Set experiment with S3 artifact location
    try:
        mlflow.create_experiment("bitcoin_prediction_s3", artifact_location="s3://mlflow/")
    except:
        pass  # Experiment already exists
    mlflow.set_experiment("bitcoin_prediction_s3")
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Load data and prepare features
        data = bitcoin_service.get_price_history_with_features(db, limit=1000, hours=24*7)  # 1 week of data
        
        if not data:
            raise ValueError("No data available to train the model.")

        # Convert to DataFrame
        df = pd.DataFrame(data)
        # Convert Decimal columns to float
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass
        df = df.dropna()

        if df.empty:
            raise ValueError("No valid data available after feature engineering.")

        # 2. Define features (X) and target (y)
        features = [col for col in df.columns if col.startswith("price_t-") or col.startswith("ma_")]
        X = df[features]
        y = df["price"]

        if X.empty or len(X) < 10:
            raise ValueError("Insufficient data for training. Need at least 10 samples.")

        # 3. Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

        # 4. Train model
        with mlflow.start_run() as run:
            model = LinearRegression()
            model.fit(X_train, y_train)

            # 5. Create input example
            input_example = X_train.iloc[:1]

            # 6. Log model and metrics
            mlflow.sklearn.log_model(
                model, 
                "linear_regression_model",
                input_example=input_example
            )
            mlflow.log_metric("r2_score", model.score(X_test, y_test))

            print(f"Model trained and logged with run_id: {run.info.run_id}")
            return run.info.run_id
    finally:
        db.close()


def get_latest_prediction() -> float:
    """
    Loads the latest model from MLflow and makes a prediction.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Get the latest run from the correct experiment
        mlflow.set_experiment("bitcoin_prediction_s3")
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        if len(runs) == 0:
            raise FileNotFoundError("No MLflow runs found. Please train a model first.")
        latest_run_id = runs.iloc[0]["run_id"]

        # 2. Load the model
        logged_model = f"runs:/{latest_run_id}/linear_regression_model"
        model = mlflow.pyfunc.load_model(logged_model)

        # 3. Get the latest features
        data = bitcoin_service.get_price_history_with_features(db, limit=1)
        if not data:
            raise ValueError("No data available for prediction.")

        df = pd.DataFrame(data)
        features = [col for col in df.columns if col.startswith("price_t-") or col.startswith("ma_")]
        X_latest = df[features]

        # 4. Predict
        prediction = model.predict(X_latest)
        return prediction[0]
    finally:
        db.close()
