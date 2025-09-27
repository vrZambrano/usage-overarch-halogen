import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

class BitcoinFeatureEngineer:
    """
    Classe responsável por gerar features de machine learning a partir dos dados de preço do Bitcoin.
    Implementa indicadores técnicos e features temporais seguindo as técnicas do guia.
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features baseadas no tempo"""
        df = df.copy()
        
        # Garantir que timestamp é datetime e timezone-aware
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Se não tem timezone info, assumir UTC
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        
        # Features temporais
        df['minute_of_hour'] = df['timestamp'].dt.minute
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['week_of_year'] = df['timestamp'].dt.isocalendar().week
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Cria features de lag (atraso)"""
        df = df.copy()
        
        # Features de lag em minutos (assumindo dados de 1 minuto)
        df['price_lag_1min'] = df[price_col].shift(1)
        df['price_lag_5min'] = df[price_col].shift(5)
        df['price_lag_15min'] = df[price_col].shift(15)
        df['price_lag_30min'] = df[price_col].shift(30)
        df['price_lag_60min'] = df[price_col].shift(60)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Cria features de janelas deslizantes (rolling)"""
        df = df.copy()
        
        # Médias móveis
        df['rolling_mean_5min'] = df[price_col].rolling(window=5, min_periods=1).mean()
        df['rolling_mean_15min'] = df[price_col].rolling(window=15, min_periods=1).mean()
        df['rolling_mean_30min'] = df[price_col].rolling(window=30, min_periods=1).mean()
        df['rolling_mean_60min'] = df[price_col].rolling(window=60, min_periods=1).mean()
        
        # Desvios padrão
        df['rolling_std_5min'] = df[price_col].rolling(window=5, min_periods=1).std()
        df['rolling_std_15min'] = df[price_col].rolling(window=15, min_periods=1).std()
        df['rolling_std_30min'] = df[price_col].rolling(window=30, min_periods=1).std()
        df['rolling_std_60min'] = df[price_col].rolling(window=60, min_periods=1).std()
        
        # Min/Max
        df['rolling_min_30min'] = df[price_col].rolling(window=30, min_periods=1).min()
        df['rolling_max_30min'] = df[price_col].rolling(window=30, min_periods=1).max()
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula o Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calcula MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        
        return {
            'macd_line': macd_line,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calcula Bollinger Bands"""
        rolling_mean = prices.rolling(window=period, min_periods=1).mean()
        rolling_std = prices.rolling(window=period, min_periods=1).std()
        
        upper_band = rolling_mean + (rolling_std * std_dev)
        lower_band = rolling_mean - (rolling_std * std_dev)
        
        # Largura das bandas
        bb_width = upper_band - lower_band
        
        # Posição do preço nas bandas (0 = banda inferior, 1 = banda superior)
        bb_position = (prices - lower_band) / (upper_band - lower_band)
        bb_position = bb_position.clip(0, 1)  # Limitar entre 0 e 1
        
        return {
            'bb_upper': upper_band,
            'bb_middle': rolling_mean,
            'bb_lower': lower_band,
            'bb_width': bb_width,
            'bb_position': bb_position
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calcula Average True Range (ATR)"""
        # Para dados de preço único, usamos o preço como high, low e close
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period, min_periods=1).mean()
        
        return atr
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calcula Oscilador Estocástico"""
        lowest_low = low.rolling(window=k_period, min_periods=1).min()
        highest_high = high.rolling(window=k_period, min_periods=1).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period, min_periods=1).mean()
        
        return {
            'stoch_k': k_percent,
            'stoch_d': d_percent
        }
    
    def create_technical_indicators(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Cria todos os indicadores técnicos"""
        df = df.copy()
        prices = df[price_col]
        
        # RSI
        df['rsi_14'] = self.calculate_rsi(prices, 14)
        
        # MACD
        macd_data = self.calculate_macd(prices)
        df['macd_line'] = macd_data['macd_line']
        df['macd_signal'] = macd_data['macd_signal']
        df['macd_histogram'] = macd_data['macd_histogram']
        
        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(prices)
        df['bb_upper'] = bb_data['bb_upper']
        df['bb_middle'] = bb_data['bb_middle']
        df['bb_lower'] = bb_data['bb_lower']
        df['bb_width'] = bb_data['bb_width']
        df['bb_position'] = bb_data['bb_position']
        
        # ATR (usando preço como proxy para high/low/close)
        df['atr_14'] = self.calculate_atr(prices, prices, prices, 14)
        
        # Stochastic (usando preço como proxy para high/low/close)
        stoch_data = self.calculate_stochastic(prices, prices, prices)
        df['stoch_k'] = stoch_data['stoch_k']
        df['stoch_d'] = stoch_data['stoch_d']
        
        return df
    
    def create_volatility_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Cria features de volatilidade e mudança de preço"""
        df = df.copy()
        prices = df[price_col]
        
        # Mudanças absolutas
        df['price_change_1min'] = prices.diff(1)
        df['price_change_5min'] = prices.diff(5)
        df['price_change_15min'] = prices.diff(15)
        
        # Mudanças percentuais
        df['price_change_pct_1min'] = prices.pct_change(1) * 100
        df['price_change_pct_5min'] = prices.pct_change(5) * 100
        df['price_change_pct_15min'] = prices.pct_change(15) * 100
        
        # Volatilidade (desvio padrão rolling)
        df['volatility_30min'] = prices.rolling(window=30, min_periods=1).std()
        
        return df
    
    def create_momentum_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Cria features de momentum"""
        df = df.copy()
        prices = df[price_col]
        
        # Momentum = preço atual - preço N períodos atrás
        df['momentum_5min'] = prices - prices.shift(5)
        df['momentum_15min'] = prices - prices.shift(15)
        df['momentum_30min'] = prices - prices.shift(30)
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """Normaliza features para ML"""
        df = df.copy()
        
        # Normalizar preço (MinMaxScaler)
        price_values = df[price_col].values.reshape(-1, 1)
        df['price_normalized'] = self.scaler.fit_transform(price_values).flatten()
        
        # Placeholder para volume normalizado (para futuro uso)
        df['volume_normalized'] = 0.0
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """
        Pipeline completo de feature engineering.
        Aplica todas as transformações em sequência.
        """
        logger.info("Iniciando feature engineering...")
        
        # Garantir que o DataFrame está ordenado por timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Aplicar todas as transformações
        df = self.create_temporal_features(df)
        logger.info("Features temporais criadas")
        
        df = self.create_lag_features(df, price_col)
        logger.info("Features de lag criadas")
        
        df = self.create_rolling_features(df, price_col)
        logger.info("Features rolling criadas")
        
        df = self.create_technical_indicators(df, price_col)
        logger.info("Indicadores técnicos criados")
        
        df = self.create_volatility_features(df, price_col)
        logger.info("Features de volatilidade criadas")
        
        df = self.create_momentum_features(df, price_col)
        logger.info("Features de momentum criadas")
        
        df = self.normalize_features(df, price_col)
        logger.info("Features normalizadas")
        
        logger.info(f"Feature engineering concluído. Shape final: {df.shape}")
        return df
    
    def get_feature_columns(self) -> List[str]:
        """Retorna lista de todas as colunas de features criadas"""
        return [
            # Features temporais
            'minute_of_hour', 'hour_of_day', 'day_of_week', 'week_of_year',
            
            # Features de lag
            'price_lag_1min', 'price_lag_5min', 'price_lag_15min', 'price_lag_30min', 'price_lag_60min',
            
            # Features rolling - médias
            'rolling_mean_5min', 'rolling_mean_15min', 'rolling_mean_30min', 'rolling_mean_60min',
            
            # Features rolling - desvio padrão
            'rolling_std_5min', 'rolling_std_15min', 'rolling_std_30min', 'rolling_std_60min',
            
            # Features rolling - min/max
            'rolling_min_30min', 'rolling_max_30min',
            
            # Indicadores técnicos
            'rsi_14', 'macd_line', 'macd_signal', 'macd_histogram',
            'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position',
            'atr_14', 'stoch_k', 'stoch_d',
            
            # Features de volatilidade
            'price_change_1min', 'price_change_5min', 'price_change_15min',
            'price_change_pct_1min', 'price_change_pct_5min', 'price_change_pct_15min',
            'volatility_30min',
            
            # Features de momentum
            'momentum_5min', 'momentum_15min', 'momentum_30min',
            
            # Features normalizadas
            'price_normalized', 'volume_normalized'
        ]
