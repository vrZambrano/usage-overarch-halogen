import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from core.database import SessionLocal
from services.prediction_service import get_latest_prediction
from services.trend_prediction_service import get_latest_trend_prediction
from services.prediction_storage_service import prediction_storage_service

logger = logging.getLogger(__name__)


class PredictionCollector:
    """
    Coletor de previsões que roda em background.
    Coleta previsões de preço e tendência a cada minuto e armazena no banco.
    Também atualiza previsões antigas com valores reais.
    """
    
    def __init__(self):
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        self.interval_seconds = 60  # Coletar a cada 60 segundos
        
    async def start_collection(self):
        """Inicia a coleta de previsões em background"""
        if self.running:
            logger.warning("Prediction collector is already running")
            return
        
        self.running = True
        logger.info("Starting prediction collector...")
        
        try:
            while self.running:
                await self._collect_and_store_predictions()
                await asyncio.sleep(self.interval_seconds)
        except asyncio.CancelledError:
            logger.info("Prediction collector task cancelled")
        except Exception as e:
            logger.error(f"Error in prediction collector: {str(e)}")
        finally:
            self.running = False
    
    def stop_collection(self):
        """Para a coleta de previsões"""
        if self.running:
            logger.info("Stopping prediction collector...")
            self.running = False
    
    async def _collect_and_store_predictions(self):
        """
        Coleta previsões dos modelos e armazena no banco.
        Também atualiza previsões antigas com valores reais.
        """
        db = SessionLocal()
        
        try:
            # 1. Coletar previsões dos modelos
            try:
                logger.info("Collecting predictions from models...")
                
                # Obter previsão de preço
                price_prediction = get_latest_prediction()
                
                # Obter previsão de tendência
                trend_prediction = get_latest_trend_prediction()
                
                # Armazenar no banco
                prediction_storage_service.store_prediction(
                    db=db,
                    price_prediction=price_prediction,
                    trend_prediction=trend_prediction
                )
                
                logger.info(
                    f"Stored predictions - Price: ${price_prediction['predicted_price']:.2f}, "
                    f"Trend: {trend_prediction['trend']} ({trend_prediction['confidence']:.2%})"
                )
                
            except FileNotFoundError as e:
                logger.warning(f"Model not found: {str(e)}")
            except Exception as e:
                logger.error(f"Error collecting predictions: {str(e)}")
            
            # 2. Atualizar previsões antigas com valores reais
            try:
                updated_count = prediction_storage_service.update_with_actual_values(db)
                if updated_count > 0:
                    logger.info(f"Updated {updated_count} predictions with actual values")
            except Exception as e:
                logger.error(f"Error updating predictions with actual values: {str(e)}")
            
            # 3. Limpeza periódica (a cada hora, verificar se há dados antigos)
            # Executar apenas no minuto 0 de cada hora
            current_minute = datetime.now(timezone.utc).minute
            if current_minute == 0:
                try:
                    deleted_count = prediction_storage_service.cleanup_old_predictions(db, days=90)
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} old predictions")
                except Exception as e:
                    logger.error(f"Error during cleanup: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error in prediction collection cycle: {str(e)}")
        finally:
            db.close()


# Singleton instance
prediction_collector = PredictionCollector()
