import h2o
from h2o.automl import H2OAutoML
import mlflow
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import os
import logging
from datetime import datetime

from services.bitcoin_service import bitcoin_service
from services.feature_engineer import BitcoinFeatureEngineer
from core.database import get_db

logger = logging.getLogger(__name__)


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


def train_and_log_h2o_model():
    """
    Trains multiple models using H2O AutoML and logs the best one to MLflow.
    H2O AutoML automatically tests various algorithms and selects the best.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Set experiment
    try:
        mlflow.create_experiment("bitcoin_h2o_automl", artifact_location="s3://mlflow/")
    except:
        pass  # Experiment already exists
    mlflow.set_experiment("bitcoin_h2o_automl")
    
    # Initialize H2O in standalone mode
    logger.info("Initializing H2O in standalone mode...")
    h2o.init(
        max_mem_size="4G",
        nthreads=-1,
        strict_version_check=False,
        ip="127.0.0.1",
        port=54321,
        start_h2o=True,
        enable_assertions=False
    )
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Load historical data
        logger.info("Loading historical data...")
        time_limit_hours = 24 * 7  # 1 week of data
        prices = bitcoin_service.get_price_history(db, limit=10000, hours=time_limit_hours)
        
        if not prices or len(prices) < 100:
            raise ValueError(f"Insufficient data available for training. Found: {len(prices) if prices else 0} records")

        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': p.timestamp,
            'price': float(p.price)
        } for p in prices])
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"Loaded {len(df)} price records")
        
        # 2. Apply feature engineering
        logger.info("Applying feature engineering...")
        feature_engineer = BitcoinFeatureEngineer()
        df_features = feature_engineer.engineer_all_features(df, price_col='price')
        
        # 3. Create target variable (price 15 minutes ahead)
        df_features['target_price'] = df_features['price'].shift(-15)
        
        # Drop rows with NaN
        df_features = df_features.dropna()
        
        if len(df_features) < 50:
            raise ValueError(f"Insufficient data after feature engineering. Found: {len(df_features)} records")
        
        logger.info(f"Feature engineering complete. Shape: {df_features.shape}")
        
        # 4. Prepare features and target
        feature_cols = feature_engineer.get_feature_columns()
        available_features = [col for col in feature_cols if col in df_features.columns and not df_features[col].isna().all()]
        
        # Add timestamp for splitting
        df_model = df_features[available_features + ['target_price', 'timestamp']].copy()
        
        # Replace NaN/inf with 0
        df_model = df_model.replace([np.inf, -np.inf], np.nan)
        df_model = df_model.fillna(0)
        
        logger.info(f"Training with {len(available_features)} features and {len(df_model)} samples")
        
        # 5. Time-based split (80% train, 20% test)
        split_idx = int(len(df_model) * 0.8)
        train_df = df_model.iloc[:split_idx].copy()
        test_df = df_model.iloc[split_idx:].copy()
        
        # Remove timestamp from training data
        train_df = train_df.drop('timestamp', axis=1)
        test_df = test_df.drop('timestamp', axis=1)
        
        logger.info(f"Train set: {len(train_df)}, Test set: {len(test_df)}")
        
        # 6. Convert to H2O frames
        train_h2o = h2o.H2OFrame(train_df)
        test_h2o = h2o.H2OFrame(test_df)
        
        # Identify target and features
        target = 'target_price'
        features = [col for col in train_h2o.columns if col != target]
        
        # 7. Train with H2O AutoML
        with mlflow.start_run() as run:
            logger.info("Starting H2O AutoML training...")
            
            # Configure AutoML
            aml = H2OAutoML(
                max_runtime_secs=300,  # 5 minutes max
                max_models=20,
                seed=42,
                nfolds=5,
                sort_metric='RMSE',
                exclude_algos=['StackedEnsemble'],  # Exclude for faster training
                verbosity='info'
            )
            
            # Log parameters
            mlflow.log_param("max_runtime_secs", 300)
            mlflow.log_param("max_models", 20)
            mlflow.log_param("n_features", len(features))
            mlflow.log_param("n_samples", len(train_df))
            mlflow.log_param("target_horizon_minutes", 15)
            mlflow.log_param("nfolds", 5)
            
            # Train AutoML
            aml.train(x=features, y=target, training_frame=train_h2o)
            
            # Get leaderboard
            leaderboard = aml.leaderboard
            logger.info(f"\nH2O AutoML Leaderboard:\n{leaderboard.head()}")
            
            # Get best model
            best_model = aml.leader
            model_id = best_model.model_id
            
            logger.info(f"Best model: {model_id}")
            
            # 8. Evaluate on test set
            perf = best_model.model_performance(test_h2o)
            
            test_rmse = perf.rmse()
            test_mae = perf.mae()
            test_r2 = perf.r2()
            
            # Calculate MAPE manually
            predictions = best_model.predict(test_h2o).as_data_frame()
            y_true = test_df['target_price'].values
            y_pred = predictions['predict'].values
            test_mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Log metrics
            mlflow.log_metric("test_rmse", test_rmse)
            mlflow.log_metric("test_mae", test_mae)
            mlflow.log_metric("test_mape", test_mape)
            mlflow.log_metric("test_r2", test_r2)
            
            logger.info(f"Test RMSE: {test_rmse:.2f}")
            logger.info(f"Test MAE: {test_mae:.2f}")
            logger.info(f"Test MAPE: {test_mape:.2f}%")
            logger.info(f"Test R²: {test_r2:.4f}")
            
            # Log model type
            model_type = best_model.algo
            mlflow.log_param("best_model_type", model_type)
            mlflow.log_param("best_model_id", model_id)
            
            # Get variable importance
            try:
                var_imp = best_model.varimp(use_pandas=True)
                if var_imp is not None:
                    # Log top 10 features
                    for idx, row in var_imp.head(10).iterrows():
                        mlflow.log_metric(f"importance_{row['variable']}", row['relative_importance'])
                    
                    # Save variable importance as artifact
                    var_imp_dict = var_imp.to_dict('records')
                    mlflow.log_dict({"variable_importance": var_imp_dict}, "variable_importance.json")
            except Exception as e:
                logger.warning(f"Could not get variable importance: {e}")
            
            # 9. Save model
            model_path = f"/tmp/h2o_model_{run.info.run_id}"
            h2o.save_model(best_model, path=model_path, force=True)
            
            # Log model to MLflow
            mlflow.log_artifacts(model_path, "h2o_model")
            
            # Save feature names and model metadata
            mlflow.log_dict({
                "feature_names": features,
                "model_type": model_type,
                "model_id": model_id
            }, "model_metadata.json")
            
            # Log leaderboard
            leaderboard_df = leaderboard.as_data_frame()
            mlflow.log_dict({
                "leaderboard": leaderboard_df.to_dict('records')
            }, "leaderboard.json")
            
            logger.info(f"H2O AutoML model trained and logged with run_id: {run.info.run_id}")
            logger.info(f"Best model type: {model_type}")
            
            return run.info.run_id, model_type
            
    except Exception as e:
        logger.error(f"Error during H2O AutoML training: {str(e)}")
        raise
    finally:
        db.close()
        # Don't shutdown H2O here - might be needed for predictions


def get_latest_h2o_prediction() -> dict:
    """
    Loads the latest H2O AutoML model from MLflow and makes a prediction.
    Returns a dictionary with predicted price and model information.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Initialize H2O if not already initialized
    try:
        h2o.init(
            max_mem_size="2G",
            nthreads=-1,
            strict_version_check=False,
            ip="127.0.0.1",
            port=54321,
            start_h2o=True,
            enable_assertions=False
        )
    except:
        pass  # Already initialized
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Get the latest run from the experiment
        mlflow.set_experiment("bitcoin_h2o_automl")
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        
        if len(runs) == 0:
            raise FileNotFoundError("No H2O AutoML runs found. Please train a model first using: python scripts/train_h2o_model.py")
        
        latest_run_id = runs.iloc[0]["run_id"]
        
        # 2. Load model metadata
        client = mlflow.tracking.MlflowClient()
        metadata_path = client.download_artifacts(latest_run_id, "model_metadata.json")
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        feature_names = metadata["feature_names"]
        model_type = metadata["model_type"]
        model_id = metadata["model_id"]
        
        # 3. Load H2O model
        model_artifact_path = client.download_artifacts(latest_run_id, "h2o_model")
        model = h2o.load_model(model_artifact_path + "/" + model_id)
        
        # 4. Get latest data and engineer features
        logger.info("Getting latest data for H2O prediction...")
        prices = bitcoin_service.get_price_history(db, limit=100, hours=2)
        
        if not prices or len(prices) < 60:
            raise ValueError("Insufficient recent data for prediction")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': p.timestamp,
            'price': float(p.price)
        } for p in prices])
        
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Apply feature engineering
        feature_engineer = BitcoinFeatureEngineer()
        df_features = feature_engineer.engineer_all_features(df, price_col='price')
        
        # Get the latest row
        latest_features = df_features.iloc[-1]
        
        # Prepare features in the same order as training
        feature_dict = {}
        for feature_name in feature_names:
            if feature_name in latest_features:
                value = latest_features[feature_name]
                # Handle NaN/inf
                if pd.isna(value) or np.isinf(value):
                    value = 0.0
                feature_dict[feature_name] = float(value)
            else:
                feature_dict[feature_name] = 0.0
        
        # Convert to H2O frame
        pred_df = pd.DataFrame([feature_dict])
        pred_h2o = h2o.H2OFrame(pred_df)
        
        # 5. Make prediction
        prediction_h2o = model.predict(pred_h2o)
        predicted_price = prediction_h2o.as_data_frame()['predict'].values[0]
        
        # Get current price
        current_price = float(latest_features['price'])
        
        # Calculate prediction change
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Get model metrics from the run
        test_mae = runs.iloc[0]["metrics.test_mae"]
        test_mape = runs.iloc[0]["metrics.test_mape"]
        test_rmse = runs.iloc[0]["metrics.test_rmse"]
        test_r2 = runs.iloc[0]["metrics.test_r2"]
        
        result = {
            "predicted_price": float(predicted_price),
            "current_price": float(current_price),
            "price_change": float(price_change),
            "price_change_percent": float(price_change_pct),
            "horizon_minutes": 15,
            "model_type": model_type,
            "model_id": model_id,
            "model_rmse": float(test_rmse),
            "model_mae": float(test_mae),
            "model_mape": float(test_mape),
            "model_r2": float(test_r2),
            "timestamp": latest_features['timestamp'].isoformat(),
            "run_id": latest_run_id
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error during H2O prediction: {str(e)}")
        raise
    finally:
        db.close()


def get_h2o_leaderboard() -> list:
    """
    Retrieves the H2O AutoML leaderboard from the latest training run.
    Returns a list of all models tested with their performance metrics.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    try:
        # Get the latest run
        mlflow.set_experiment("bitcoin_h2o_automl")
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        
        if len(runs) == 0:
            raise FileNotFoundError("No H2O AutoML runs found. Please train a model first.")
        
        latest_run_id = runs.iloc[0]["run_id"]
        
        # Load leaderboard
        client = mlflow.tracking.MlflowClient()
        leaderboard_path = client.download_artifacts(latest_run_id, "leaderboard.json")
        import json
        with open(leaderboard_path, 'r') as f:
            leaderboard = json.load(f)["leaderboard"]
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error retrieving H2O leaderboard: {str(e)}")
        raise
