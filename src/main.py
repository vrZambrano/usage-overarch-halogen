from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from datetime import datetime

from core.database import get_db
from models.schemas import BitcoinPriceResponse, LatestPriceResponse, BitcoinPriceFeatureResponse
from services.price_collector import price_collector
from services.bitcoin_service import bitcoin_service
from services.prediction_service import get_latest_prediction
from utils.timezone import convert_to_brasilia_timezone

app = FastAPI(title="Bitcoin Price Pipeline", version="1.0.0")

# Variável para controlar a tarefa de background
collection_task = None

@app.on_event("startup")
async def startup_event():
    """Inicia a coleta de preços ao inicializar a aplicação"""
    global collection_task
    collection_task = asyncio.create_task(price_collector.start_collection())

@app.on_event("shutdown")
async def shutdown_event():
    """Para a coleta de preços ao encerrar a aplicação"""
    price_collector.stop_collection()
    if collection_task:
        collection_task.cancel()

@app.get("/")
async def root():
    """Endpoint raiz com informações sobre a API"""
    return {
        "message": "Bitcoin Price Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "latest_price": "/price/latest",
            "price_history": "/price/history",
            "predict": "/price/predict",
            "health": "/health"
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
        timestamp=latest_price.timestamp,
        source=latest_price.source,
        last_updated=latest_price.created_at
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
    """Retorna a previsão do preço do Bitcoin."""
    try:
        prediction = get_latest_prediction()
        return {"predicted_price": prediction}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

@app.get("/price/stats")
async def get_price_stats(hours: int = 24, db: Session = Depends(get_db)):
    """Retorna estatísticas dos preços em um período"""
    stats = bitcoin_service.get_price_stats(db, hours=hours)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
    
    return stats

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
            "last_price_update": convert_to_brasilia_timezone(latest_price.created_at) if latest_price else None,
            "timestamp": convert_to_brasilia_timezone(datetime.utcnow())
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
