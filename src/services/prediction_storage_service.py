from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
import logging

from models.database import BitcoinPrediction, BitcoinPrice
from models.schemas import (
    BitcoinPredictionResponse,
    PredictionAccuracyResponse,
    PricePredictionResponse,
    TrendPredictionResponse
)
from decimal import Decimal
import math

logger = logging.getLogger(__name__)


class PredictionStorageService:
    """
    Serviço para armazenar e gerenciar previsões de Bitcoin.
    Grava previsões a cada minuto e atualiza com valores reais após 15 minutos.
    """
    
    def store_prediction(
        self,
        db: Session,
        price_prediction: Dict,
        trend_prediction: Dict
    ) -> BitcoinPrediction:
        """
        Armazena uma nova previsão no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            price_prediction: Previsão de preço do modelo XGBoost Regressor (dict)
            trend_prediction: Previsão de tendência do modelo XGBoost Classifier (dict)
            
        Returns:
            BitcoinPrediction: Registro criado no banco
        """
        try:
            # Converter timestamp string para datetime
            timestamp_str = price_prediction['timestamp']
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Criar registro
            prediction = BitcoinPrediction(
                timestamp=timestamp,
                current_price=Decimal(str(price_prediction['current_price'])),
                
                # Previsão de preço
                predicted_price=Decimal(str(price_prediction['predicted_price'])),
                price_change=Decimal(str(price_prediction['price_change'])),
                price_change_percent=Decimal(str(price_prediction['price_change_percent'])),
                price_model_mae=Decimal(str(price_prediction['model_mae'])),
                price_model_mape=Decimal(str(price_prediction['model_mape'])),
                price_run_id=price_prediction['run_id'],
                
                # Previsão de tendência
                predicted_trend=trend_prediction['trend'],
                trend_numeric=trend_prediction['trend_numeric'],
                probability_up=Decimal(str(trend_prediction['probability_up'])),
                probability_down=Decimal(str(trend_prediction['probability_down'])),
                confidence=Decimal(str(trend_prediction['confidence'])),
                trend_model_accuracy=Decimal(str(trend_prediction['model_accuracy'])),
                trend_model_f1=Decimal(str(trend_prediction['model_f1_score'])),
                trend_run_id=trend_prediction['run_id'],
                
                # Valores reais serão preenchidos depois
                actual_price=None,
                actual_trend=None,
                prediction_error=None,
                trend_correct=None
            )
            
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            
            logger.info(f"Stored prediction: price={price_prediction['predicted_price']}, trend={trend_prediction['trend']}")
            
            return prediction
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing prediction: {str(e)}")
            raise
    
    def update_with_actual_values(self, db: Session) -> int:
        """
        Atualiza previsões antigas (15 minutos atrás) com valores reais.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            int: Número de previsões atualizadas
        """
        try:
            # Calcular timestamp de 15 minutos atrás (com margem de 2 minutos)
            now = datetime.now(timezone.utc)
            target_time = now - timedelta(minutes=15)
            min_time = target_time - timedelta(minutes=1)
            max_time = target_time + timedelta(minutes=1)
            
            # Buscar previsões que ainda não foram atualizadas
            predictions = db.query(BitcoinPrediction).filter(
                and_(
                    BitcoinPrediction.timestamp >= min_time,
                    BitcoinPrediction.timestamp <= max_time,
                    BitcoinPrediction.actual_price.is_(None)
                )
            ).all()
            
            if not predictions:
                return 0
            
            updated_count = 0
            
            for prediction in predictions:
                # Buscar o preço real 15 minutos após a previsão
                actual_time_min = prediction.timestamp + timedelta(minutes=14)
                actual_time_max = prediction.timestamp + timedelta(minutes=16)
                
                actual_price_record = db.query(BitcoinPrice).filter(
                    and_(
                        BitcoinPrice.timestamp >= actual_time_min,
                        BitcoinPrice.timestamp <= actual_time_max
                    )
                ).order_by(BitcoinPrice.timestamp).first()
                
                if actual_price_record:
                    actual_price = float(actual_price_record.price)
                    current_price = float(prediction.current_price)
                    predicted_price = float(prediction.predicted_price)
                    
                    # Calcular erro de previsão
                    prediction_error = actual_price - predicted_price
                    
                    # Determinar tendência real
                    actual_trend = "UP" if actual_price > current_price else "DOWN"
                    
                    # Verificar se a tendência foi prevista corretamente
                    trend_correct = 1 if actual_trend == prediction.predicted_trend else 0
                    
                    # Atualizar registro
                    prediction.actual_price = Decimal(str(actual_price))
                    prediction.actual_trend = actual_trend
                    prediction.prediction_error = Decimal(str(prediction_error))
                    prediction.trend_correct = trend_correct
                    
                    updated_count += 1
            
            db.commit()
            
            if updated_count > 0:
                logger.info(f"Updated {updated_count} predictions with actual values")
            
            return updated_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating predictions with actual values: {str(e)}")
            return 0
    
    def get_latest_predictions(self, db: Session, limit: int = 20) -> List[BitcoinPredictionResponse]:
        """
        Retorna as previsões mais recentes.
        
        Args:
            db: Sessão do banco de dados
            limit: Número máximo de previsões a retornar
            
        Returns:
            List[BitcoinPredictionResponse]: Lista de previsões
        """
        predictions = db.query(BitcoinPrediction).order_by(
            BitcoinPrediction.timestamp.desc()
        ).limit(limit).all()
        
        return [self._to_response(p) for p in predictions]
    
    def get_predictions_history(
        self,
        db: Session,
        hours: int = 24,
        limit: int = 1000
    ) -> List[BitcoinPredictionResponse]:
        """
        Retorna histórico de previsões em um período.
        
        Args:
            db: Sessão do banco de dados
            hours: Número de horas de histórico
            limit: Número máximo de previsões a retornar
            
        Returns:
            List[BitcoinPredictionResponse]: Lista de previsões
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        predictions = db.query(BitcoinPrediction).filter(
            BitcoinPrediction.timestamp >= cutoff_time
        ).order_by(BitcoinPrediction.timestamp.desc()).limit(limit).all()
        
        return [self._to_response(p) for p in predictions]
    
    def get_accuracy_metrics(self, db: Session, hours: int = 24) -> Optional[PredictionAccuracyResponse]:
        """
        Calcula métricas de acurácia das previsões.
        
        Args:
            db: Sessão do banco de dados
            hours: Período para calcular métricas
            
        Returns:
            PredictionAccuracyResponse: Métricas de acurácia ou None se não houver dados
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Buscar previsões verificadas (que já têm valor real)
        verified = db.query(BitcoinPrediction).filter(
            and_(
                BitcoinPrediction.timestamp >= cutoff_time,
                BitcoinPrediction.actual_price.isnot(None)
            )
        ).all()
        
        if not verified:
            return None
        
        # Total de previsões
        total = db.query(func.count(BitcoinPrediction.id)).filter(
            BitcoinPrediction.timestamp >= cutoff_time
        ).scalar()
        
        # Calcular métricas de preço
        errors = [abs(float(p.prediction_error)) for p in verified]
        price_mae_avg = sum(errors) / len(errors) if errors else 0.0
        
        squared_errors = [float(p.prediction_error) ** 2 for p in verified]
        price_rmse = math.sqrt(sum(squared_errors) / len(squared_errors)) if squared_errors else 0.0
        
        # Calcular MAPE médio
        mapes = [float(p.price_model_mape) for p in verified if p.price_model_mape]
        price_mape_avg = sum(mapes) / len(mapes) if mapes else 0.0
        
        # Calcular métricas de tendência
        trend_correct_count = sum(1 for p in verified if p.trend_correct == 1)
        trend_accuracy = trend_correct_count / len(verified) if verified else 0.0
        
        # Matriz de confusão
        true_positives = sum(1 for p in verified if p.predicted_trend == "UP" and p.actual_trend == "UP")
        true_negatives = sum(1 for p in verified if p.predicted_trend == "DOWN" and p.actual_trend == "DOWN")
        false_positives = sum(1 for p in verified if p.predicted_trend == "UP" and p.actual_trend == "DOWN")
        false_negatives = sum(1 for p in verified if p.predicted_trend == "DOWN" and p.actual_trend == "UP")
        
        # Precision, Recall, F1
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return PredictionAccuracyResponse(
            total_predictions=total,
            verified_predictions=len(verified),
            price_mae_avg=price_mae_avg,
            price_mape_avg=price_mape_avg,
            price_rmse=price_rmse,
            trend_accuracy=trend_accuracy,
            trend_precision=precision,
            trend_recall=recall,
            trend_f1=f1,
            true_positives=true_positives,
            true_negatives=true_negatives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            time_range_hours=hours
        )
    
    def cleanup_old_predictions(self, db: Session, days: int = 90) -> int:
        """
        Remove previsões antigas (mais de X dias).
        
        Args:
            db: Sessão do banco de dados
            days: Número de dias de retenção
            
        Returns:
            int: Número de registros removidos
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            deleted = db.query(BitcoinPrediction).filter(
                BitcoinPrediction.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} predictions older than {days} days")
            
            return deleted
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up old predictions: {str(e)}")
            return 0
    
    def _to_response(self, prediction: BitcoinPrediction) -> BitcoinPredictionResponse:
        """Converte modelo do banco para response schema"""
        return BitcoinPredictionResponse(
            id=prediction.id,
            timestamp=prediction.timestamp,
            current_price=float(prediction.current_price),
            predicted_price=float(prediction.predicted_price) if prediction.predicted_price else None,
            price_change=float(prediction.price_change) if prediction.price_change else None,
            price_change_percent=float(prediction.price_change_percent) if prediction.price_change_percent else None,
            price_model_mae=float(prediction.price_model_mae) if prediction.price_model_mae else None,
            price_model_mape=float(prediction.price_model_mape) if prediction.price_model_mape else None,
            predicted_trend=prediction.predicted_trend,
            trend_numeric=prediction.trend_numeric,
            probability_up=float(prediction.probability_up) if prediction.probability_up else None,
            probability_down=float(prediction.probability_down) if prediction.probability_down else None,
            confidence=float(prediction.confidence) if prediction.confidence else None,
            trend_model_accuracy=float(prediction.trend_model_accuracy) if prediction.trend_model_accuracy else None,
            trend_model_f1=float(prediction.trend_model_f1) if prediction.trend_model_f1 else None,
            actual_price=float(prediction.actual_price) if prediction.actual_price else None,
            actual_trend=prediction.actual_trend,
            prediction_error=float(prediction.prediction_error) if prediction.prediction_error else None,
            trend_correct=prediction.trend_correct,
            created_at=prediction.created_at
        )


# Singleton instance
prediction_storage_service = PredictionStorageService()
