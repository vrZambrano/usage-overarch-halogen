import mlflow
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sqlalchemy.orm import Session
import os
import logging

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


def train_and_log_trend_model():
    """
    Trains an XGBoost classification model to predict Bitcoin price trends (Up/Down).
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Set experiment with S3 artifact location
    try:
        mlflow.create_experiment("bitcoin_trend_classification", artifact_location="s3://mlflow/")
    except:
        pass  # Experiment already exists
    mlflow.set_experiment("bitcoin_trend_classification")
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Load historical data
        logger.info("Loading historical data for trend classification...")
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
        
        # 3. Create target variable (trend: 1 = Up, 0 = Down)
        # Compare price 15 minutes ahead with current price
        df_features['future_price'] = df_features['price'].shift(-15)
        df_features['trend'] = (df_features['future_price'] > df_features['price']).astype(int)
        
        # Drop rows with NaN
        df_features = df_features.dropna()
        
        if len(df_features) < 50:
            raise ValueError(f"Insufficient data after feature engineering. Found: {len(df_features)} records")
        
        logger.info(f"Feature engineering complete. Shape: {df_features.shape}")
        
        # Check class balance
        trend_counts = df_features['trend'].value_counts()
        logger.info(f"Class distribution - Down (0): {trend_counts.get(0, 0)}, Up (1): {trend_counts.get(1, 0)}")
        
        # 4. Prepare features and target
        feature_cols = feature_engineer.get_feature_columns()
        
        # Remove features that don't exist or have all NaN values
        available_features = [col for col in feature_cols if col in df_features.columns and not df_features[col].isna().all()]
        
        X = df_features[available_features].values
        y = df_features['trend'].values
        
        # Replace any remaining NaN/inf with 0
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        logger.info(f"Training with {len(available_features)} features and {len(X)} samples")
        
        # 5. Time series split for validation
        tscv = TimeSeriesSplit(n_splits=3)
        
        # 6. Train model with MLflow tracking
        with mlflow.start_run() as run:
            # Model parameters
            params = {
                'n_estimators': 150,
                'max_depth': 7,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'n_jobs': -1,
                'eval_metric': 'logloss'
            }
            
            # Log parameters
            mlflow.log_params(params)
            mlflow.log_param("n_features", len(available_features))
            mlflow.log_param("n_samples", len(X))
            mlflow.log_param("target_horizon_minutes", 15)
            mlflow.log_param("class_0_count", int(trend_counts.get(0, 0)))
            mlflow.log_param("class_1_count", int(trend_counts.get(1, 0)))
            
            # Cross-validation scores
            cv_accuracy = []
            cv_precision = []
            cv_recall = []
            cv_f1 = []
            cv_auc = []
            
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                model = XGBClassifier(**params)
                model.fit(X_train, y_train, verbose=False)
                
                y_pred = model.predict(X_val)
                y_pred_proba = model.predict_proba(X_val)[:, 1]
                
                accuracy = accuracy_score(y_val, y_pred)
                precision = precision_score(y_val, y_pred, zero_division=0)
                recall = recall_score(y_val, y_pred, zero_division=0)
                f1 = f1_score(y_val, y_pred, zero_division=0)
                
                try:
                    auc = roc_auc_score(y_val, y_pred_proba)
                except:
                    auc = 0.0
                
                cv_accuracy.append(accuracy)
                cv_precision.append(precision)
                cv_recall.append(recall)
                cv_f1.append(f1)
                cv_auc.append(auc)
                
                logger.info(f"Fold {fold+1} - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")
            
            # Log cross-validation metrics
            mlflow.log_metric("cv_accuracy_mean", np.mean(cv_accuracy))
            mlflow.log_metric("cv_precision_mean", np.mean(cv_precision))
            mlflow.log_metric("cv_recall_mean", np.mean(cv_recall))
            mlflow.log_metric("cv_f1_mean", np.mean(cv_f1))
            mlflow.log_metric("cv_auc_mean", np.mean(cv_auc))
            
            # Train final model on all data
            logger.info("Training final model on all data...")
            final_model = XGBClassifier(**params)
            final_model.fit(X, y, verbose=False)
            
            # Calculate final metrics on last 20% of data as test set
            split_idx = int(len(X) * 0.8)
            X_test = X[split_idx:]
            y_test = y[split_idx:]
            
            y_pred_test = final_model.predict(X_test)
            y_pred_proba_test = final_model.predict_proba(X_test)[:, 1]
            
            test_accuracy = accuracy_score(y_test, y_pred_test)
            test_precision = precision_score(y_test, y_pred_test, zero_division=0)
            test_recall = recall_score(y_test, y_pred_test, zero_division=0)
            test_f1 = f1_score(y_test, y_pred_test, zero_division=0)
            
            try:
                test_auc = roc_auc_score(y_test, y_pred_proba_test)
            except:
                test_auc = 0.0
            
            # Log final metrics
            mlflow.log_metric("test_accuracy", test_accuracy)
            mlflow.log_metric("test_precision", test_precision)
            mlflow.log_metric("test_recall", test_recall)
            mlflow.log_metric("test_f1", test_f1)
            mlflow.log_metric("test_auc", test_auc)
            
            logger.info(f"Test Accuracy: {test_accuracy:.4f}")
            logger.info(f"Test Precision: {test_precision:.4f}")
            logger.info(f"Test Recall: {test_recall:.4f}")
            logger.info(f"Test F1: {test_f1:.4f}")
            logger.info(f"Test AUC: {test_auc:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred_test)
            logger.info(f"Confusion Matrix:\n{cm}")
            
            # Classification report
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred_test, target_names=['Down', 'Up'])}")
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': available_features,
                'importance': final_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Log top 20 features
            top_features = feature_importance.head(20)
            for idx, row in top_features.iterrows():
                mlflow.log_metric(f"importance_{row['feature']}", row['importance'])
            
            # Save feature importance as artifact
            importance_dict = feature_importance.to_dict('records')
            mlflow.log_dict({"feature_importance": importance_dict}, "feature_importance.json")
            
            # Create input example
            input_example = pd.DataFrame([X[0]], columns=available_features)
            
            # Log model
            mlflow.xgboost.log_model(
                final_model,
                "xgboost_trend_model",
                input_example=input_example
            )
            
            # Log feature names for later use
            mlflow.log_dict({"feature_names": available_features}, "feature_names.json")
            
            logger.info(f"Trend model trained and logged with run_id: {run.info.run_id}")
            return run.info.run_id
            
    except Exception as e:
        logger.error(f"Error during trend model training: {str(e)}")
        raise
    finally:
        db.close()


def get_latest_trend_prediction() -> dict:
    """
    Loads the latest trend model from MLflow and makes a prediction.
    Returns a dictionary with predicted trend and probability.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Get the latest run from the correct experiment
        mlflow.set_experiment("bitcoin_trend_classification")
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        
        if len(runs) == 0:
            raise FileNotFoundError("No MLflow runs found. Please train a trend model first using: python scripts/train_trend_model.py")
        
        latest_run_id = runs.iloc[0]["run_id"]
        
        # 2. Load the model
        logged_model = f"runs:/{latest_run_id}/xgboost_trend_model"
        model = mlflow.xgboost.load_model(logged_model)
        
        # Load feature names
        client = mlflow.tracking.MlflowClient()
        feature_names_path = client.download_artifacts(latest_run_id, "feature_names.json")
        import json
        with open(feature_names_path, 'r') as f:
            feature_names = json.load(f)["feature_names"]
        
        # 3. Get latest data and engineer features
        logger.info("Getting latest data for trend prediction...")
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
        X_latest = []
        for feature_name in feature_names:
            if feature_name in latest_features:
                value = latest_features[feature_name]
                # Handle NaN/inf
                if pd.isna(value) or np.isinf(value):
                    value = 0.0
                X_latest.append(float(value))
            else:
                X_latest.append(0.0)
        
        X_latest = np.array([X_latest])
        
        # 4. Make prediction
        predicted_trend = model.predict(X_latest)[0]
        predicted_proba = model.predict_proba(X_latest)[0]
        
        # Get current price
        current_price = float(latest_features['price'])
        
        # Get model metrics from the run
        test_accuracy = runs.iloc[0]["metrics.test_accuracy"]
        test_f1 = runs.iloc[0]["metrics.test_f1"]
        
        result = {
            "trend": "UP" if predicted_trend == 1 else "DOWN",
            "trend_numeric": int(predicted_trend),
            "probability_down": float(predicted_proba[0]),
            "probability_up": float(predicted_proba[1]),
            "confidence": float(max(predicted_proba)),
            "current_price": float(current_price),
            "horizon_minutes": 15,
            "model_accuracy": float(test_accuracy),
            "model_f1_score": float(test_f1),
            "timestamp": latest_features['timestamp'].isoformat(),
            "run_id": latest_run_id
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error during trend prediction: {str(e)}")
        raise
    finally:
        db.close()


def get_feature_importance() -> list:
    """
    Retrieves the feature importance from the latest trained model.
    Returns a list of features sorted by importance.
    """
    # Setup MLflow configuration
    _setup_mlflow()
    
    try:
        # Get the latest run from the correct experiment
        mlflow.set_experiment("bitcoin_trend_classification")
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        
        if len(runs) == 0:
            raise FileNotFoundError("No MLflow runs found. Please train a trend model first using: python scripts/train_trend_model.py")
        
        latest_run_id = runs.iloc[0]["run_id"]
        
        # Load feature importance
        client = mlflow.tracking.MlflowClient()
        importance_path = client.download_artifacts(latest_run_id, "feature_importance.json")
        import json
        with open(importance_path, 'r') as f:
            feature_importance = json.load(f)["feature_importance"]
        
        return feature_importance
        
    except Exception as e:
        logger.error(f"Error retrieving feature importance: {str(e)}")
        raise
