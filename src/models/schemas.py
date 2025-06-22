from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class BitcoinPriceResponse(BaseModel):
    id: int
    price: Decimal
    timestamp: datetime
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BitcoinPriceCreate(BaseModel):
    price: Decimal
    source: str = "binance"

class LatestPriceResponse(BaseModel):
    price: Decimal
    timestamp: datetime
    source: str
    last_updated: datetime
