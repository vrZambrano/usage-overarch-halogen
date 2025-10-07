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


class BitcoinPredictionResponse(BaseModel):
    """Response model for stored Bitcoin predictions"""
    id: int
    timestamp: datetime
    current_price: float
    
    # Price prediction
    predicted_price: Optional[float]
    price_change: Optional[float]
    price_change_percent: Optional[float]
    price_model_mae: Optional[float]
    price_model_mape: Optional[float]
    
    # Trend prediction
    predicted_trend: Optional[str]
    trend_numeric: Optional[int]
    probability_up: Optional[float]
    probability_down: Optional[float]
    confidence: Optional[float]
    trend_model_accuracy: Optional[float]
    trend_model_f1: Optional[float]
    
    # Actual values (available after 15 minutes)
    actual_price: Optional[float]
    actual_trend: Optional[str]
    prediction_error: Optional[float]
    trend_correct: Optional[int]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionAccuracyResponse(BaseModel):
    """Response model for prediction accuracy metrics"""
    total_predictions: int
    verified_predictions: int
    
    # Price model metrics
    price_mae_avg: float
    price_mape_avg: float
    price_rmse: float
    
    # Trend model metrics
    trend_accuracy: float
    trend_precision: float
    trend_recall: float
    trend_f1: float
    
    # Confusion matrix
    true_positives: int  # Correctly predicted UP
    true_negatives: int  # Correctly predicted DOWN
    false_positives: int  # Predicted UP, was DOWN
    false_negatives: int  # Predicted DOWN, was UP
    
    time_range_hours: int


class CombinedPredictionResponse(BaseModel):
    """Combined response with both price and trend predictions"""
    timestamp: datetime
    current_price: float
    
    # Price prediction
    price_prediction: PricePredictionResponse
    
    # Trend prediction
    trend_prediction: TrendPredictionResponse
    
    class Config:
        protected_namespaces = ()
