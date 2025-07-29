from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
import sys
import fastapi
from datetime import datetime
from contextlib import asynccontextmanager

from core.database import get_db
from models.schemas import BitcoinPriceResponse, LatestPriceResponse, BitcoinPriceFeatureResponse
from services.price_collector import price_collector
from services.bitcoin_service import bitcoin_service
from services.prediction_service import get_latest_prediction
from utils.logger import app_logger, log_operation

# Variável para controlar a tarefa de background
collection_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação FastAPI"""
    # Startup: código executado ao iniciar a aplicação
    global collection_task
    collection_task = None
    
    try:
        collection_task = asyncio.create_task(price_collector.start_collection())
        log_operation(
            operation="startup",
            status="success",
            details={
                "message": "Coleta de preços iniciada com sucesso",
                "task_id": id(collection_task) if collection_task else None
            }
        )
    except asyncio.CancelledError:
        log_operation(
            operation="startup",
            status="error",
            details={"error": "Task was cancelled during startup", "message": "Tarefa cancelada durante inicialização"}
        )
        raise
    except ConnectionError as e:
        log_operation(
            operation="startup",
            status="error",
            details={"error": str(e), "message": "Erro de conexão ao iniciar coleta de preços"}
        )
        raise
    except TimeoutError as e:
        log_operation(
            operation="startup",
            status="error",
            details={"error": str(e), "message": "Tempo limite excedido ao iniciar coleta de preços"}
        )
        raise
    except Exception as e:
        log_operation(
            operation="startup",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro inesperado ao iniciar coleta de preços"
            }
        )
        raise
    
    yield  # Ponto onde a aplicação está ativa
    
    # Shutdown: código executado ao encerrar a aplicação
    try:
        # Primeiro para o coletor
        if hasattr(price_collector, 'stop_collection'):
            await price_collector.stop_collection()
        
        # Depois cancela a tarefa de background
        if collection_task:
            collection_task.cancel()
            # Aguarda o cancelamento da tarefa com timeout
            try:
                await asyncio.wait_for(collection_task, timeout=5.0)
            except asyncio.TimeoutError:
                log_operation(
                    operation="shutdown",
                    status="warning",
                    details={"message": "Tarefa de coleta não foi cancelada dentro do timeout"}
                )
            except asyncio.CancelledError:
                pass
        
        log_operation(
            operation="shutdown",
            status="success",
            details={"message": "Coleta de preços interrompida com sucesso"}
        )
    except asyncio.CancelledError:
        log_operation(
            operation="shutdown",
            status="error",
            details={"error": "Task was cancelled during shutdown", "message": "Tarefa cancelada durante encerramento"}
        )
        raise
    except Exception as e:
        log_operation(
            operation="shutdown",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro inesperado ao encerrar coleta de preços"
            }
        )

app = FastAPI(
    title="Bitcoin Price Pipeline",
    version="1.0.0",
    lifespan=lifespan
)

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
    try:
        log_operation(
            operation="get_latest_price",
            status="start",
            details={"message": "Buscando preço mais recente"}
        )
        
        latest_price = bitcoin_service.get_latest_price(db)
        
        if not latest_price:
            log_operation(
                operation="get_latest_price",
                status="error",
                details={"message": "Nenhum preço encontrado no banco de dados"}
            )
            raise HTTPException(status_code=404, detail="Nenhum preço encontrado")
        
        response = LatestPriceResponse(
            price=latest_price.price,
            timestamp=latest_price.timestamp,
            source=latest_price.source,
            last_updated=latest_price.created_at
        )
        
        log_operation(
            operation="get_latest_price",
            status="success",
            details={
                "message": "Preço mais recente encontrado",
                "price": float(latest_price.price),
                "timestamp": latest_price.timestamp.isoformat()
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation(
            operation="get_latest_price",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro inesperado ao buscar preço mais recente"
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao buscar preço: {str(e)}")

@app.get("/price/history", response_model=List[BitcoinPriceFeatureResponse])
async def get_price_history(
    limit: int = 100,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Retorna o histórico de preços do Bitcoin com features de engenharia."""
    try:
        # Validação dos parâmetros
        if limit <= 0:
            raise HTTPException(status_code=400, detail="O parâmetro 'limit' deve ser maior que zero")
        
        if hours <= 0:
            raise HTTPException(status_code=400, detail="O parâmetro 'hours' deve ser maior que zero")
        
        if limit > 1000:
            raise HTTPException(status_code=400, detail="O parâmetro 'limit' não pode exceder 1000 registros")
        
        if hours > 720:  # 30 dias
            raise HTTPException(status_code=400, detail="O parâmetro 'hours' não pode exceder 720 horas (30 dias)")
        
        log_operation(
            operation="get_price_history",
            status="start",
            details={"limit": limit, "hours": hours, "message": "Buscando histórico de preços"}
        )
        
        prices = bitcoin_service.get_price_history_with_features(db, limit=limit, hours=hours)
        
        if not prices:
            log_operation(
                operation="get_price_history",
                status="warning",
                details={"limit": limit, "hours": hours, "message": "Nenhum preço encontrado no período especificado"}
            )
            raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
        
        log_operation(
            operation="get_price_history",
            status="success",
            details={
                "limit": limit,
                "hours": hours,
                "count": len(prices),
                "message": f"Histórico de preços encontrado com {len(prices)} registros"
            }
        )
        
        return prices
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation(
            operation="get_price_history",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "limit": limit,
                "hours": hours,
                "message": "Erro inesperado ao buscar histórico de preços"
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico de preços: {str(e)}")

@app.get("/price/predict")
async def predict_price():
    """Retorna a previsão do preço do Bitcoin."""
    try:
        log_operation(
            operation="predict_price",
            status="start",
            details={"message": "Gerando previsão de preço"}
        )
        
        prediction = get_latest_prediction()
        
        log_operation(
            operation="predict_price",
            status="success",
            details={
                "predicted_price": prediction,
                "message": "Previsão de preço gerada com sucesso"
            }
        )
        
        return {"predicted_price": prediction}
        
    except FileNotFoundError as e:
        log_operation(
            operation="predict_price",
            status="error",
            details={
                "error": str(e),
                "message": "Modelo de previsão não encontrado"
            }
        )
        raise HTTPException(status_code=404, detail=f"Modelo não encontrado: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        user_friendly_msg = error_msg
        
        # Mensagens de erro amigáveis
        if "No data available for prediction" in error_msg:
            user_friendly_msg = "Não há dados suficientes para gerar uma previsão. Por favor, aguarde até que mais dados sejam coletados."
        elif "Modelo não encontrado" in error_msg or "FileNotFoundError" in str(type(e)):
            user_friendly_msg = "O modelo de previsão não está disponível. Por favor, execute o treinamento do modelo primeiro."
            
        log_operation(
            operation="predict_price",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro ao gerar previsão de preço",
                "user_friendly_msg": user_friendly_msg
            }
        )
        raise HTTPException(status_code=500, detail=user_friendly_msg)

@app.get("/price/stats")
async def get_price_stats(hours: int = 24, db: Session = Depends(get_db)):
    """Retorna estatísticas dos preços em um período"""
    try:
        # Validação do parâmetro
        if hours <= 0:
            raise HTTPException(status_code=400, detail="O parâmetro 'hours' deve ser maior que zero")
        
        if hours > 720:  # 30 dias
            raise HTTPException(status_code=400, detail="O parâmetro 'hours' não pode exceder 720 horas (30 dias)")
        
        log_operation(
            operation="get_price_stats",
            status="start",
            details={"hours": hours, "message": "Calculando estatísticas de preço"}
        )
        
        stats = bitcoin_service.get_price_stats(db, hours=hours)
        
        if not stats:
            log_operation(
                operation="get_price_stats",
                status="warning",
                details={"hours": hours, "message": "Nenhum preço encontrado para calcular estatísticas"}
            )
            raise HTTPException(status_code=404, detail="Nenhum preço encontrado no período")
        
        log_operation(
            operation="get_price_stats",
            status="success",
            details={
                "hours": hours,
                "total_records": stats.get("total_records", 0),
                "avg_price": stats.get("avg_price"),
                "message": "Estatísticas de preço calculadas com sucesso"
            }
        )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation(
            operation="get_price_stats",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "hours": hours,
                "message": "Erro inesperado ao calcular estatísticas de preço"
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas: {str(e)}")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de health check com detalhes de status do sistema"""
    try:
        log_operation(
            operation="health_check",
            status="start",
            details={"message": "Executando verificação de saúde do sistema"}
        )
        
        # Testa conexão com o banco
        latest_price = bitcoin_service.get_latest_price(db)
        
        # Verifica status do coletor
        collector_status = "running" if price_collector.running else "stopped"
        
        # Calcula tempo desde a última atualização
        last_update_ago = None
        if latest_price and latest_price.created_at:
            time_diff = datetime.utcnow() - latest_price.created_at
            last_update_ago = time_diff.total_seconds()
        
        # Verifica se o coletor está atualizando regularmente
        collector_health = "healthy"
        if price_collector.running and last_update_ago and last_update_ago > 300:  # 5 minutos
            collector_health = "degraded"
            log_operation(
                operation="health_check",
                status="warning",
                details={
                    "message": "Coletor está rodando mas sem atualizações recentes",
                    "last_update_seconds_ago": last_update_ago
                }
            )
        
        response = {
            "status": "healthy",
            "database": "connected",
            "collector": "running" if price_collector.running else "stopped",
            "last_price_update": latest_price.created_at if latest_price else None,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        log_operation(
            operation="health_check",
            status="error",
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro ao executar verificação de saúde"
            }
        )
        # Mesmo com erro no banco, ainda podemos retornar informações parciais
        return {
            "status": "unhealthy",
            "timestamp": convert_to_brasilia_timezone(datetime.utcnow()),
            "services": {
                "database": {
                    "status": "disconnected",
                    "error": str(e)
                },
                "collector": {
                    "status": "unknown",
                    "running": price_collector.running,
                    "health": "unknown"
                },
                "api": {
                    "status": "operational"
                }
            },
            "system": {
                "python_version": sys.version,
                "fastapi_version": fastapi.__version__
            },
            "error": f"Service unhealthy: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
