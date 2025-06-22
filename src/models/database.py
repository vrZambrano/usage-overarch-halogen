from sqlalchemy import Column, Integer, Numeric, DateTime, String
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