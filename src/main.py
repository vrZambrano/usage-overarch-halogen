from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import asyncio
from datetime import datetime, timedelta

from core.database import get_db
from models.database import BitcoinPrice
from models.schemas import BitcoinPriceResponse, LatestPriceResponse
from services.price_collector import price_collector

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
            "health": "/health"
        }
    }

@app.get("/price/latest", response_model=LatestPriceResponse)
async def get_latest_price(db: Session = Depends(get_db)):
    """Retorna o último preço do Bitcoin registrado"""
    latest_price = db.query(BitcoinPrice).order_by(desc(BitcoinPrice.created_at)).first()
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado")
    
    return LatestPriceResponse(
        price=latest_price.price,
        timestamp=latest_price.timestamp,
        source=latest_price.source,
        last_updated=latest_price.created_at
    )

@app.get("/price/history", response_model=List[BitcoinPriceResponse])
async def get_price_history(
    limit: int = 100, 
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Retorna o histórico de preços do Bitcoin"""
    time_limit = datetime.utcnow() - timedelta(hours=hours)
    
    prices = db.query(BitcoinPrice)\
        .filter(BitcoinPrice.created_at >= time_limit)\
        .order_by(desc(BitcoinPrice.created_at))\
        .limit(limit)\
        .all()
    
    if not prices:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
    
    return prices

@app.get("/price/stats")
async def get_price_stats(hours: int = 24, db: Session = Depends(get_db)):
    """Retorna estatísticas dos preços em um período"""
    time_limit = datetime.utcnow() - timedelta(hours=hours)
    
    prices = db.query(BitcoinPrice.price)\
        .filter(BitcoinPrice.created_at >= time_limit)\
        .all()
    
    if not prices:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
    
    price_values = [float(p.price) for p in prices]
    
    return {
        "period_hours": hours,
        "total_records": len(price_values),
        "min_price": min(price_values),
        "max_price": max(price_values),
        "avg_price": sum(price_values) / len(price_values),
        "latest_price": price_values[0] if price_values else None
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de health check"""
    try:
        # Testa conexão com o banco
        latest_price = db.query(BitcoinPrice).order_by(desc(BitcoinPrice.created_at)).first()
        
        return {
            "status": "healthy",
            "database": "connected",
            "collector": "running" if price_collector.running else "stopped",
            "last_price_update": latest_price.created_at if latest_price else None,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
