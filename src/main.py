from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from core.database import get_db
from models.schemas import (
    BitcoinPriceResponse, 
    LatestPriceResponse, 
    BitcoinPriceFeatureResponse,
    PricePredictionResponse,
    TrendPredictionResponse,
    FeatureImportance,
    FeatureImportanceResponse
)
from services.price_collector import price_collector
from services.bitcoin_service import bitcoin_service
from services.prediction_service import get_latest_prediction
from services.trend_prediction_service import get_latest_trend_prediction, get_feature_importance
from services.prediction_collector import prediction_collector
from services.prediction_storage_service import prediction_storage_service
from utils.timezone import convert_to_brasilia_timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Gerenciador de contexto para o ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação FastAPI"""
    # Startup: inicia a coleta de preços e previsões
    price_collection_task = asyncio.create_task(price_collector.start_collection())
    prediction_collection_task = asyncio.create_task(prediction_collector.start_collection())
    
    try:
        # Yield para permitir que a aplicação funcione
        yield
    finally:
        # Shutdown: para as coletas e cancela as tarefas
        price_collector.stop_collection()
        prediction_collector.stop_collection()
        
        for task in [price_collection_task, prediction_collection_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

app = FastAPI(title="Bitcoin Price Pipeline", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    """Endpoint raiz com informações sobre a API"""
    return {
        "message": "Bitcoin Price Pipeline API",
        "version": "2.0.0",
        "description": "API completa para análise e predição de preços do Bitcoin com ML",
        "endpoints": {
            "price": {
                "latest": "/price/latest",
                "history": "/price/history",
                "stats": "/price/stats",
                "predict_legacy": "/price/predict",
                "predict_next": "/price/predict/next"
            },
            "trend": {
                "predict": "/trend/predict",
                "feature_importance": "/trend/feature-importance"
            },
            "system": {
                "health": "/health",
                "docs": "/docs"
            }
        },
        "models": {
            "price_prediction": {
                "type": "XGBoost Regressor",
                "target": "Preço 15 minutos à frente",
                "features": "50+ indicadores técnicos"
            },
            "trend_classification": {
                "type": "XGBoost Classifier",
                "target": "Tendência UP/DOWN 15 minutos à frente",
                "features": "50+ indicadores técnicos"
            }
        }
    }

@app.get("/price/latest", response_model=LatestPriceResponse)
async def get_latest_price(db: Session = Depends(get_db)):
    """Retorna o último preço do Bitcoin registrado"""
    latest_price = bitcoin_service.get_latest_price(db)
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado")
    
    return LatestPriceResponse(
        price=latest_price.price,
        timestamp=convert_to_brasilia_timezone(latest_price.timestamp),
        source=latest_price.source,
        last_updated=convert_to_brasilia_timezone(latest_price.created_at)
    )

@app.get("/price/history", response_model=List[BitcoinPriceFeatureResponse])
async def get_price_history(
    limit: int = 100, 
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Retorna o histórico de preços do Bitcoin com features de engenharia."""
    prices = bitcoin_service.get_price_history_with_features(db, limit=limit, hours=hours)
    
    if not prices:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
    
    return prices

@app.get("/price/predict")
async def predict_price():
    """Retorna a previsão do preço do Bitcoin (endpoint legado - mantido para compatibilidade)."""
    try:
        prediction = get_latest_prediction()
        return {"predicted_price": prediction}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")


@app.get("/price/predict/next", response_model=PricePredictionResponse)
async def predict_next_price():
    """
    Retorna a previsão do preço do Bitcoin 15 minutos à frente usando XGBoost.
    
    Este endpoint usa o modelo XGBoost treinado com todas as features de engenharia
    (indicadores técnicos, lags, rolling statistics, etc.) para prever o preço 15 minutos à frente.
    
    Returns:
        PricePredictionResponse: Previsão detalhada incluindo preço previsto, mudança esperada,
                                métricas de confiança do modelo e timestamp
    """
    try:
        prediction = get_latest_prediction()
        return prediction
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, 
            detail="Modelo não encontrado. Execute 'python scripts/train_model.py' para treinar o modelo primeiro."
        )
    except Exception as e:
        logger.error(f"Error during price prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer predição de preço: {str(e)}")


@app.get("/trend/predict", response_model=TrendPredictionResponse)
async def predict_trend():
    """
    Prediz a tendência do Bitcoin (UP/DOWN) para os próximos 15 minutos.
    
    Este endpoint usa um modelo XGBoost Classifier treinado com indicadores técnicos
    completos para classificar se o preço subirá ou cairá nos próximos 15 minutos.
    
    Returns:
        TrendPredictionResponse: Tendência prevista (UP/DOWN), probabilidades,
                                confiança e métricas do modelo
    """
    try:
        prediction = get_latest_trend_prediction()
        return prediction
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Modelo de tendência não encontrado. Execute 'python scripts/train_trend_model.py' para treinar o modelo primeiro."
        )
    except Exception as e:
        logger.error(f"Error during trend prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer predição de tendência: {str(e)}")


@app.get("/trend/feature-importance", response_model=FeatureImportanceResponse)
async def get_trend_feature_importance():
    """
    Retorna a importância das features usadas no modelo de classificação de tendências.
    
    Este endpoint fornece insights sobre quais indicadores técnicos e features
    são mais importantes para o modelo na hora de fazer predições de tendência.
    
    Returns:
        FeatureImportanceResponse: Lista de features ordenadas por importância
    """
    try:
        importance_list = get_feature_importance()
        return FeatureImportanceResponse(
            features=[FeatureImportance(**item) for item in importance_list],
            total_features=len(importance_list)
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Modelo de tendência não encontrado. Execute 'python scripts/train_trend_model.py' para treinar o modelo primeiro."
        )
    except Exception as e:
        logger.error(f"Error retrieving feature importance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar importância das features: {str(e)}")

@app.get("/price/stats")
async def get_price_stats(hours: int = 24, db: Session = Depends(get_db)):
    """Retorna estatísticas dos preços em um período"""
    stats = bitcoin_service.get_price_stats(db, hours=hours)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
    
    return stats

@app.get("/predictions/latest")
async def get_latest_predictions(limit: int = 20, db: Session = Depends(get_db)):
    """
    Retorna as previsões mais recentes armazenadas no banco.
    
    Args:
        limit: Número de previsões a retornar (padrão: 20)
        
    Returns:
        Lista de previsões com valores previstos e reais (quando disponível)
    """
    try:
        predictions = prediction_storage_service.get_latest_predictions(db, limit=limit)
        return predictions
    except Exception as e:
        logger.error(f"Error retrieving latest predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar previsões: {str(e)}")


@app.get("/predictions/history")
async def get_predictions_history(hours: int = 24, limit: int = 1000, db: Session = Depends(get_db)):
    """
    Retorna histórico de previsões em um período específico.
    
    Args:
        hours: Número de horas de histórico (padrão: 24)
        limit: Número máximo de previsões (padrão: 1000)
        
    Returns:
        Lista de previsões históricas
    """
    try:
        predictions = prediction_storage_service.get_predictions_history(db, hours=hours, limit=limit)
        return predictions
    except Exception as e:
        logger.error(f"Error retrieving predictions history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")


@app.get("/predictions/accuracy")
async def get_predictions_accuracy(hours: int = 24, db: Session = Depends(get_db)):
    """
    Retorna métricas de acurácia das previsões.
    
    Calcula métricas de performance dos modelos comparando previsões
    com valores reais observados.
    
    Args:
        hours: Período para calcular métricas (padrão: 24 horas)
        
    Returns:
        Métricas detalhadas de acurácia incluindo MAE, MAPE, accuracy, precision, etc.
    """
    try:
        metrics = prediction_storage_service.get_accuracy_metrics(db, hours=hours)
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"Sem dados de previsões verificadas nas últimas {hours} horas"
            )
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating accuracy metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular métricas: {str(e)}")


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de health check"""
    try:
        # Testa conexão com o banco
        latest_price = bitcoin_service.get_latest_price(db)
        
        return {
            "status": "healthy",
            "database": "connected",
            "collector": "running" if price_collector.running else "stopped",
            "prediction_collector": "running" if prediction_collector.running else "stopped",
            "last_price_update": convert_to_brasilia_timezone(latest_price.created_at) if latest_price else None,
            "timestamp": convert_to_brasilia_timezone(datetime.now(timezone.utc))
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
