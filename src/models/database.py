from sqlalchemy import Column, Integer, Numeric, DateTime, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BitcoinPrice(Base):
    __tablename__ = "bitcoin_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50), default="binance")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelDBBitcoinFeatures(Base):
    __tablename__ = "modeldb_bitcoin_features"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos base
    price = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50), default="binance")
    
    # Features temporais
    minute_of_hour = Column(Integer)  # 0-59
    hour_of_day = Column(Integer)     # 0-23
    day_of_week = Column(Integer)     # 0-6
    week_of_year = Column(Integer)    # 1-53
    
    # Features de lag (atraso)
    price_lag_1min = Column(Float)
    price_lag_5min = Column(Float)
    price_lag_15min = Column(Float)
    price_lag_30min = Column(Float)
    price_lag_60min = Column(Float)
    
    # Features rolling (janelas deslizantes) - Médias
    rolling_mean_5min = Column(Float)
    rolling_mean_15min = Column(Float)
    rolling_mean_30min = Column(Float)
    rolling_mean_60min = Column(Float)
    
    # Features rolling - Desvio padrão
    rolling_std_5min = Column(Float)
    rolling_std_15min = Column(Float)
    rolling_std_30min = Column(Float)
    rolling_std_60min = Column(Float)
    
    # Features rolling - Min/Max
    rolling_min_30min = Column(Float)
    rolling_max_30min = Column(Float)
    
    # Indicadores técnicos - RSI
    rsi_14 = Column(Float)
    
    # Indicadores técnicos - MACD
    macd_line = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    
    # Indicadores técnicos - Bollinger Bands
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    bb_position = Column(Float)  # Posição do preço nas bandas (0-1)
    
    # Indicadores técnicos - ATR
    atr_14 = Column(Float)
    
    # Indicadores técnicos - Stochastic
    stoch_k = Column(Float)
    stoch_d = Column(Float)
    
    # Features de volatilidade
    price_change_1min = Column(Float)
    price_change_5min = Column(Float)
    price_change_15min = Column(Float)
    price_change_pct_1min = Column(Float)
    price_change_pct_5min = Column(Float)
    price_change_pct_15min = Column(Float)
    volatility_30min = Column(Float)
    
    # Features de momentum
    momentum_5min = Column(Float)
    momentum_15min = Column(Float)
    momentum_30min = Column(Float)
    
    # Features normalizadas (para ML)
    price_normalized = Column(Float)
    volume_normalized = Column(Float)  # Para futuro uso
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BitcoinPrediction(Base):
    """
    Tabela para armazenar previsões de preço e tendência do Bitcoin.
    Mantém histórico de 90 dias para análise de performance dos modelos.
    """
    __tablename__ = "bitcoin_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Dados no momento da previsão
    current_price = Column(Numeric(15, 2), nullable=False)
    
    # Previsão de Preço (XGBoost Regressor)
    predicted_price = Column(Numeric(15, 2))
    price_change = Column(Numeric(15, 2))
    price_change_percent = Column(Numeric(10, 4))
    price_model_mae = Column(Numeric(15, 2))
    price_model_mape = Column(Numeric(10, 4))
    price_run_id = Column(String(100))
    
    # Previsão de Tendência (XGBoost Classifier)
    predicted_trend = Column(String(10))
    trend_numeric = Column(Integer)
    probability_up = Column(Numeric(10, 4))
    probability_down = Column(Numeric(10, 4))
    confidence = Column(Numeric(10, 4))
    trend_model_accuracy = Column(Numeric(10, 4))
    trend_model_f1 = Column(Numeric(10, 4))
    trend_run_id = Column(String(100))
    
    # Valores reais (preenchidos após 15 minutos)
    actual_price = Column(Numeric(15, 2))
    actual_trend = Column(String(10))
    prediction_error = Column(Numeric(15, 2))
    trend_correct = Column(Integer)  # 1 = correto, 0 = incorreto, NULL = ainda não verificado
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
