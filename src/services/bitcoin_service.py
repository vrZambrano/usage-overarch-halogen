from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List
import pandas as pd

from models.database import BitcoinPrice


class BitcoinService:
    def get_latest_price(self, db: Session) -> BitcoinPrice:
        """
        Retrieves the latest Bitcoin price from the database.
        """
        return db.query(BitcoinPrice).order_by(desc(BitcoinPrice.created_at)).first()

    def get_price_history(
        self, db: Session, limit: int = 100, hours: int = 24
    ) -> List[BitcoinPrice]:
        """
        Retrieves the price history from the database within a given time frame.
        """
        time_limit = datetime.utcnow() - timedelta(hours=hours)
        return (
            db.query(BitcoinPrice)
            .filter(BitcoinPrice.created_at >= time_limit)
            .order_by(desc(BitcoinPrice.created_at))
            .limit(limit)
            .all()
        )

    def get_price_stats(self, db: Session, hours: int = 24) -> dict:
        """
        Retrieves price statistics from the database within a given time frame.
        """
        time_limit = datetime.utcnow() - timedelta(hours=hours)
        prices = (
            db.query(BitcoinPrice.price)
            .filter(BitcoinPrice.created_at >= time_limit)
            .all()
        )

        if not prices:
            return None

        price_values = [float(p.price) for p in prices]

        return {
            "period_hours": hours,
            "total_records": len(price_values),
            "min_price": min(price_values),
            "max_price": max(price_values),
            "avg_price": sum(price_values) / len(price_values),
            "latest_price": price_values[0] if price_values else None,
        }

    def get_price_history_with_features(
        self, db: Session, limit: int = 100, hours: int = 24, lags: int = 5, window: int = 10
    ) -> List[dict]:
        """
        Retrieves price history and engineers features for time series forecasting.
        """
        # Fetch more data to have enough for lags and moving averages
        extended_limit = limit + lags + window
        time_limit = datetime.utcnow() - timedelta(hours=hours)
        
        prices = (
            db.query(BitcoinPrice)
            .filter(BitcoinPrice.created_at >= time_limit)
            .order_by(desc(BitcoinPrice.created_at))
            .limit(extended_limit)
            .all()
        )

        if not prices:
            return []

        # Convert to pandas DataFrame
        df = pd.DataFrame([p.__dict__ for p in prices])
        df = df.sort_values(by="timestamp").reset_index(drop=True)
        
        # Feature Engineering
        # Target variable (price at t+1)
        df['price_t+1'] = df['price'].shift(-1)

        # Lag features
        for i in range(1, lags + 1):
            df[f'price_t-{i}'] = df['price'].shift(i)

        # Moving average features
        df[f'ma_{window}'] = df['price'].rolling(window=window).mean()

        # Drop rows with NaN values created by shifts and rolling windows
        df = df.dropna().reset_index(drop=True)
        
        # Ensure we return the requested number of records (limit)
        if len(df) > limit:
            df = df.tail(limit)

        return df.to_dict('records')


bitcoin_service = BitcoinService()
