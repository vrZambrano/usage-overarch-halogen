from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional

class BitcoinPriceResponse(BaseModel):
    id: int
    price: Decimal
    timestamp: datetime
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BitcoinPriceCreate(BaseModel):
    price: Decimal
    source: str = "binance"

class LatestPriceResponse(BaseModel):
    price: Decimal
    timestamp: datetime
    source: str
    last_updated: datetime

class BitcoinPriceFeatureResponse(BaseModel):
    id: int
    price: Decimal
    timestamp: datetime
    source: str
    created_at: datetime
    price_t_plus_1: Optional[Decimal] = Field(alias="price_t+1")
    price_t_minus_1: Optional[Decimal] = Field(alias="price_t-1")
    price_t_minus_2: Optional[Decimal] = Field(alias="price_t-2")
    price_t_minus_3: Optional[Decimal] = Field(alias="price_t-3")
    price_t_minus_4: Optional[Decimal] = Field(alias="price_t-4")
    price_t_minus_5: Optional[Decimal] = Field(alias="price_t-5")
    ma_10: Optional[Decimal] = Field(alias="ma_10")

    class Config:
        from_attributes = True
        populate_by_name = True


class PricePredictionResponse(BaseModel):
    """Response model for Bitcoin price predictions"""
    predicted_price: float = Field(..., description="Predicted price 15 minutes ahead")
    current_price: float = Field(..., description="Current Bitcoin price")
    price_change: float = Field(..., description="Absolute price change prediction")
    price_change_percent: float = Field(..., description="Percentage price change prediction")
    horizon_minutes: int = Field(..., description="Prediction time horizon in minutes")
    model_mae: float = Field(..., description="Model Mean Absolute Error")
    model_mape: float = Field(..., description="Model Mean Absolute Percentage Error")
    timestamp: str = Field(..., description="Timestamp of the prediction")
    run_id: str = Field(..., description="MLflow run ID of the model")

    class Config:
        protected_namespaces = ()
        json_schema_extra = {
            "example": {
                "predicted_price": 45230.50,
                "current_price": 45000.00,
                "price_change": 230.50,
                "price_change_percent": 0.51,
                "horizon_minutes": 15,
                "model_mae": 125.30,
                "model_mape": 0.28,
                "timestamp": "2025-01-07T12:30:00",
                "run_id": "abc123def456"
            }
        }


class TrendPredictionResponse(BaseModel):
    """Response model for Bitcoin trend predictions"""
    trend: str = Field(..., description="Predicted trend direction: UP or DOWN")
    trend_numeric: int = Field(..., description="Numeric trend: 1 for UP, 0 for DOWN")
    probability_down: float = Field(..., description="Probability of downward trend")
    probability_up: float = Field(..., description="Probability of upward trend")
    confidence: float = Field(..., description="Model confidence (max probability)")
    current_price: float = Field(..., description="Current Bitcoin price")
    horizon_minutes: int = Field(..., description="Prediction time horizon in minutes")
    model_accuracy: float = Field(..., description="Model test accuracy")
    model_f1_score: float = Field(..., description="Model F1 score")
    timestamp: str = Field(..., description="Timestamp of the prediction")
    run_id: str = Field(..., description="MLflow run ID of the model")

    class Config:
        protected_namespaces = ()
        json_schema_extra = {
            "example": {
                "trend": "UP",
                "trend_numeric": 1,
                "probability_down": 0.35,
                "probability_up": 0.65,
                "confidence": 0.65,
                "current_price": 45000.00,
                "horizon_minutes": 15,
                "model_accuracy": 0.87,
                "model_f1_score": 0.86,
                "timestamp": "2025-01-07T12:30:00",
                "run_id": "abc123def456"
            }
        }


class FeatureImportance(BaseModel):
    """Model for a single feature importance entry"""
    feature: str = Field(..., description="Feature name")
    importance: float = Field(..., description="Feature importance score")


class FeatureImportanceResponse(BaseModel):
    """Response model for feature importance"""
    features: list[FeatureImportance] = Field(..., description="List of features with their importance scores")
    total_features: int = Field(..., description="Total number of features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [
                    {"feature": "rsi_14", "importance": 0.085},
                    {"feature": "macd_line", "importance": 0.072},
                    {"feature": "bb_position", "importance": 0.065}
                ],
                "total_features": 50
            }
        }


class H2OPricePredictionResponse(BaseModel):
    """Response model for H2O AutoML Bitcoin price predictions"""
    predicted_price: float = Field(..., description="Predicted price 15 minutes ahead")
    current_price: float = Field(..., description="Current Bitcoin price")
    price_change: float = Field(..., description="Absolute price change prediction")
    price_change_percent: float = Field(..., description="Percentage price change prediction")
    horizon_minutes: int = Field(..., description="Prediction time horizon in minutes")
    model_type: str = Field(..., description="Type of best model selected by H2O AutoML")
    model_id: str = Field(..., description="H2O model ID")
    model_rmse: float = Field(..., description="Model Root Mean Squared Error")
    model_mae: float = Field(..., description="Model Mean Absolute Error")
    model_mape: float = Field(..., description="Model Mean Absolute Percentage Error")
    model_r2: float = Field(..., description="Model R-squared score")
    timestamp: str = Field(..., description="Timestamp of the prediction")
    run_id: str = Field(..., description="MLflow run ID")

    class Config:
        protected_namespaces = ()
        json_schema_extra = {
            "example": {
                "predicted_price": 45280.75,
                "current_price": 45000.00,
                "price_change": 280.75,
                "price_change_percent": 0.62,
                "horizon_minutes": 15,
                "model_type": "GBM",
                "model_id": "GBM_1_AutoML_20250107_123456",
                "model_rmse": 118.45,
                "model_mae": 92.30,
                "model_mape": 0.25,
                "model_r2": 0.956,
                "timestamp": "2025-01-07T12:30:00",
                "run_id": "abc123def456"
            }
        }


class H2OLeaderboardEntry(BaseModel):
    """Model for a single H2O AutoML leaderboard entry"""
    model_id: str = Field(..., description="Model identifier")
    rmse: float = Field(..., description="Root Mean Squared Error")
    mae: float = Field(..., description="Mean Absolute Error")
    rmsle: float = Field(..., description="Root Mean Squared Logarithmic Error")
    mean_residual_deviance: float = Field(..., description="Mean residual deviance")


class H2OLeaderboardResponse(BaseModel):
    """Response model for H2O AutoML leaderboard"""
    leaderboard: list[dict] = Field(..., description="List of all models tested with their metrics")
    total_models: int = Field(..., description="Total number of models in leaderboard")
    best_model: str = Field(..., description="ID of the best performing model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "leaderboard": [
                    {
                        "model_id": "GBM_1_AutoML_20250107_123456",
                        "rmse": 118.45,
                        "mae": 92.30,
                        "rmsle": 0.0026,
                        "mean_residual_deviance": 14030.22
                    },
                    {
                        "model_id": "XGBoost_2_AutoML_20250107_123456",
                        "rmse": 125.12,
                        "mae": 98.76,
                        "rmsle": 0.0028,
                        "mean_residual_deviance": 15655.02
                    }
                ],
                "total_models": 20,
                "best_model": "GBM_1_AutoML_20250107_123456"
            }
        }
