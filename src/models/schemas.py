from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional

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

class BitcoinPriceFeatureResponse(BaseModel):
    id: int
    price: Decimal
    timestamp: datetime
    source: str
    created_at: datetime
    price_t_plus_1: Optional[Decimal] = Field(alias="price_t+1")
    price_t_minus_1: Optional[Decimal] = Field(alias="price_t-1")
    price_t_minus_2: Optional[Decimal] = Field(alias="price_t-2")
    price_t_minus_3: Optional[Decimal] = Field(alias="price_t-3")
    price_t_minus_4: Optional[Decimal] = Field(alias="price_t-4")
    price_t_minus_5: Optional[Decimal] = Field(alias="price_t-5")
    ma_10: Optional[Decimal] = Field(alias="ma_10")

    class Config:
        from_attributes = True
        populate_by_name = True
