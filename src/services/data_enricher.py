import pandas as pd
import numpy as np
from typing import Optional, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal

from core.database import SessionLocal
from models.database import BitcoinPrice, ModelDBBitcoinFeatures
from services.feature_engineer import BitcoinFeatureEngineer

logger = logging.getLogger(__name__)

class DataEnricher:
    """
    Classe responsável por enriquecer os dados históricos do Bitcoin
    aplicando feature engineering e salvando na tabela modeldb_bitcoin_features.
    """
    
    def __init__(self):
        self.feature_engineer = BitcoinFeatureEngineer()
    
    def load_historical_data(self, db: Session, limit: Optional[int] = None) -> pd.DataFrame:
        """Carrega dados históricos da tabela bitcoin_prices"""
        try:
            query = db.query(BitcoinPrice).order_by(BitcoinPrice.timestamp)
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            
            if not results:
                logger.warning("Nenhum dado histórico encontrado")
                return pd.DataFrame()
            
            # Converter para DataFrame
            data = []
            for record in results:
                data.append({
                    'id': record.id,
                    'price': float(record.price),
                    'timestamp': record.timestamp,
                    'source': record.source,
                    'created_at': record.created_at
                })
            
            df = pd.DataFrame(data)
            logger.info(f"Carregados {len(df)} registros históricos")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados históricos: {e}")
            return pd.DataFrame()
    
    def prepare_enriched_record(self, row: pd.Series) -> dict:
        """Prepara um registro enriquecido para inserção no banco"""
        record = {
            'price': Decimal(str(row['price'])),
            'timestamp': row['timestamp'],
            'source': row.get('source', 'binance'),
            
            # Features temporais
            'minute_of_hour': int(row.get('minute_of_hour', 0)) if pd.notna(row.get('minute_of_hour')) else None,
            'hour_of_day': int(row.get('hour_of_day', 0)) if pd.notna(row.get('hour_of_day')) else None,
            'day_of_week': int(row.get('day_of_week', 0)) if pd.notna(row.get('day_of_week')) else None,
            'week_of_year': int(row.get('week_of_year', 1)) if pd.notna(row.get('week_of_year')) else None,
            
            # Features de lag
            'price_lag_1min': float(row.get('price_lag_1min')) if pd.notna(row.get('price_lag_1min')) else None,
            'price_lag_5min': float(row.get('price_lag_5min')) if pd.notna(row.get('price_lag_5min')) else None,
            'price_lag_15min': float(row.get('price_lag_15min')) if pd.notna(row.get('price_lag_15min')) else None,
            'price_lag_30min': float(row.get('price_lag_30min')) if pd.notna(row.get('price_lag_30min')) else None,
            'price_lag_60min': float(row.get('price_lag_60min')) if pd.notna(row.get('price_lag_60min')) else None,
            
            # Features rolling - médias
            'rolling_mean_5min': float(row.get('rolling_mean_5min')) if pd.notna(row.get('rolling_mean_5min')) else None,
            'rolling_mean_15min': float(row.get('rolling_mean_15min')) if pd.notna(row.get('rolling_mean_15min')) else None,
            'rolling_mean_30min': float(row.get('rolling_mean_30min')) if pd.notna(row.get('rolling_mean_30min')) else None,
            'rolling_mean_60min': float(row.get('rolling_mean_60min')) if pd.notna(row.get('rolling_mean_60min')) else None,
            
            # Features rolling - desvio padrão
            'rolling_std_5min': float(row.get('rolling_std_5min')) if pd.notna(row.get('rolling_std_5min')) else None,
            'rolling_std_15min': float(row.get('rolling_std_15min')) if pd.notna(row.get('rolling_std_15min')) else None,
            'rolling_std_30min': float(row.get('rolling_std_30min')) if pd.notna(row.get('rolling_std_30min')) else None,
            'rolling_std_60min': float(row.get('rolling_std_60min')) if pd.notna(row.get('rolling_std_60min')) else None,
            
            # Features rolling - min/max
            'rolling_min_30min': float(row.get('rolling_min_30min')) if pd.notna(row.get('rolling_min_30min')) else None,
            'rolling_max_30min': float(row.get('rolling_max_30min')) if pd.notna(row.get('rolling_max_30min')) else None,
            
            # Indicadores técnicos - RSI
            'rsi_14': float(row.get('rsi_14')) if pd.notna(row.get('rsi_14')) else None,
            
            # Indicadores técnicos - MACD
            'macd_line': float(row.get('macd_line')) if pd.notna(row.get('macd_line')) else None,
            'macd_signal': float(row.get('macd_signal')) if pd.notna(row.get('macd_signal')) else None,
            'macd_histogram': float(row.get('macd_histogram')) if pd.notna(row.get('macd_histogram')) else None,
            
            # Indicadores técnicos - Bollinger Bands
            'bb_upper': float(row.get('bb_upper')) if pd.notna(row.get('bb_upper')) else None,
            'bb_middle': float(row.get('bb_middle')) if pd.notna(row.get('bb_middle')) else None,
            'bb_lower': float(row.get('bb_lower')) if pd.notna(row.get('bb_lower')) else None,
            'bb_width': float(row.get('bb_width')) if pd.notna(row.get('bb_width')) else None,
            'bb_position': float(row.get('bb_position')) if pd.notna(row.get('bb_position')) else None,
            
            # Indicadores técnicos - ATR
            'atr_14': float(row.get('atr_14')) if pd.notna(row.get('atr_14')) else None,
            
            # Indicadores técnicos - Stochastic
            'stoch_k': float(row.get('stoch_k')) if pd.notna(row.get('stoch_k')) else None,
            'stoch_d': float(row.get('stoch_d')) if pd.notna(row.get('stoch_d')) else None,
            
            # Features de volatilidade
            'price_change_1min': float(row.get('price_change_1min')) if pd.notna(row.get('price_change_1min')) else None,
            'price_change_5min': float(row.get('price_change_5min')) if pd.notna(row.get('price_change_5min')) else None,
            'price_change_15min': float(row.get('price_change_15min')) if pd.notna(row.get('price_change_15min')) else None,
            'price_change_pct_1min': float(row.get('price_change_pct_1min')) if pd.notna(row.get('price_change_pct_1min')) else None,
            'price_change_pct_5min': float(row.get('price_change_pct_5min')) if pd.notna(row.get('price_change_pct_5min')) else None,
            'price_change_pct_15min': float(row.get('price_change_pct_15min')) if pd.notna(row.get('price_change_pct_15min')) else None,
            'volatility_30min': float(row.get('volatility_30min')) if pd.notna(row.get('volatility_30min')) else None,
            
            # Features de momentum
            'momentum_5min': float(row.get('momentum_5min')) if pd.notna(row.get('momentum_5min')) else None,
            'momentum_15min': float(row.get('momentum_15min')) if pd.notna(row.get('momentum_15min')) else None,
            'momentum_30min': float(row.get('momentum_30min')) if pd.notna(row.get('momentum_30min')) else None,
            
            # Features normalizadas
            'price_normalized': float(row.get('price_normalized')) if pd.notna(row.get('price_normalized')) else None,
            'volume_normalized': float(row.get('volume_normalized', 0.0)) if pd.notna(row.get('volume_normalized')) else 0.0,
        }
        
        return record
    
    def save_enriched_data(self, db: Session, enriched_df: pd.DataFrame, batch_size: int = 1000) -> bool:
        """Salva dados enriquecidos na tabela modeldb_bitcoin_features"""
        try:
            total_records = len(enriched_df)
            logger.info(f"Salvando {total_records} registros enriquecidos...")
            
            # Limpar tabela existente (opcional - remover se quiser manter dados)
            db.execute(text("DELETE FROM modeldb_bitcoin_features"))
            db.commit()
            logger.info("Tabela modeldb_bitcoin_features limpa")
            
            # Processar em lotes
            for i in range(0, total_records, batch_size):
                batch_end = min(i + batch_size, total_records)
                batch_df = enriched_df.iloc[i:batch_end]
                
                # Preparar registros do lote
                batch_records = []
                for _, row in batch_df.iterrows():
                    record_data = self.prepare_enriched_record(row)
                    batch_records.append(ModelDBBitcoinFeatures(**record_data))
                
                # Inserir lote
                db.add_all(batch_records)
                db.commit()
                
                logger.info(f"Lote {i//batch_size + 1}: {len(batch_records)} registros salvos ({batch_end}/{total_records})")
            
            logger.info(f"Todos os {total_records} registros foram salvos com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados enriquecidos: {e}")
            db.rollback()
            return False
    
    def enrich_historical_data(self, limit: Optional[int] = None, batch_size: int = 1000) -> bool:
        """
        Pipeline completo para enriquecer dados históricos.
        
        Args:
            limit: Limite de registros a processar (None para todos)
            batch_size: Tamanho do lote para inserção no banco
            
        Returns:
            bool: True se sucesso, False se erro
        """
        db = SessionLocal()
        try:
            logger.info("Iniciando enriquecimento de dados históricos...")
            
            # 1. Carregar dados históricos
            historical_df = self.load_historical_data(db, limit)
            if historical_df.empty:
                logger.warning("Nenhum dado histórico para processar")
                return False
            
            # 2. Aplicar feature engineering
            logger.info("Aplicando feature engineering...")
            enriched_df = self.feature_engineer.engineer_all_features(historical_df)
            
            # 3. Salvar dados enriquecidos
            success = self.save_enriched_data(db, enriched_df, batch_size)
            
            if success:
                logger.info("Enriquecimento de dados históricos concluído com sucesso!")
                
                # Estatísticas finais
                total_features = len(self.feature_engineer.get_feature_columns())
                logger.info(f"Total de features criadas: {total_features}")
                logger.info(f"Shape final dos dados: {enriched_df.shape}")
                
            return success
            
        except Exception as e:
            logger.error(f"Erro no enriquecimento de dados históricos: {e}")
            return False
        finally:
            db.close()
    
    def enrich_single_record(self, price: float, timestamp: datetime, source: str = "binance") -> Optional[dict]:
        """
        Enriquece um único registro de preço (para uso em tempo real).
        
        Args:
            price: Preço do Bitcoin
            timestamp: Timestamp do registro
            source: Fonte dos dados
            
        Returns:
            dict: Registro enriquecido ou None se erro
        """
        db = SessionLocal()
        try:
            # Buscar dados recentes para calcular features que dependem de histórico
            recent_data = db.query(BitcoinPrice)\
                           .order_by(BitcoinPrice.timestamp.desc())\
                           .limit(100)\
                           .all()
            
            if not recent_data:
                logger.warning("Não há dados históricos suficientes para enriquecimento")
                return None
            
            # Converter para DataFrame e adicionar novo registro
            data = []
            for record in reversed(recent_data):  # Reverter para ordem cronológica
                data.append({
                    'price': float(record.price),
                    'timestamp': record.timestamp,
                    'source': record.source
                })
            
            # Adicionar novo registro
            data.append({
                'price': price,
                'timestamp': timestamp,
                'source': source
            })
            
            df = pd.DataFrame(data)
            
            # Aplicar feature engineering
            enriched_df = self.feature_engineer.engineer_all_features(df)
            
            # Retornar apenas o último registro (o novo)
            last_row = enriched_df.iloc[-1]
            return self.prepare_enriched_record(last_row)
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer registro único: {e}")
            return None
        finally:
            db.close()
    
    def get_enriched_data_stats(self) -> dict:
        """Retorna estatísticas dos dados enriquecidos"""
        db = SessionLocal()
        try:
            # Contar registros
            total_records = db.query(ModelDBBitcoinFeatures).count()
            
            # Data mais antiga e mais recente
            oldest = db.query(ModelDBBitcoinFeatures.timestamp)\
                      .order_by(ModelDBBitcoinFeatures.timestamp.asc())\
                      .first()
            
            newest = db.query(ModelDBBitcoinFeatures.timestamp)\
                      .order_by(ModelDBBitcoinFeatures.timestamp.desc())\
                      .first()
            
            stats = {
                'total_records': total_records,
                'oldest_record': oldest[0] if oldest else None,
                'newest_record': newest[0] if newest else None,
                'total_features': len(self.feature_engineer.get_feature_columns())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
        finally:
            db.close()
