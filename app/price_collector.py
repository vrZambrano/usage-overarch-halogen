import asyncio
import aiohttp
import logging
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, BitcoinPrice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitcoinPriceCollector:
    def __init__(self):
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        self.running = False
    
    async def fetch_bitcoin_price(self) -> float:
        """Busca o preço atual do Bitcoin da API da Binance"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
                    else:
                        logger.error(f"Erro na API: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Erro ao buscar preço: {e}")
            return None
    
    def save_price(self, price: float) -> bool:
        """Salva o preço no banco de dados"""
        try:
            db = SessionLocal()
            bitcoin_price = BitcoinPrice(
                price=Decimal(str(price)),
                source="binance"
            )
            db.add(bitcoin_price)
            db.commit()
            db.refresh(bitcoin_price)
            db.close()
            logger.info(f"Preço salvo: ${price:.2f}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar preço: {e}")
            return False
    
    async def start_collection(self):
        """Inicia a coleta de preços a cada minuto"""
        self.running = True
        logger.info("Iniciando coleta de preços do Bitcoin...")
        
        while self.running:
            try:
                price = await self.fetch_bitcoin_price()
                if price:
                    self.save_price(price)
                else:
                    logger.warning("Não foi possível obter o preço")
                
                # Aguarda 1 minuto
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erro na coleta: {e}")
                await asyncio.sleep(60)
    
    def stop_collection(self):
        """Para a coleta de preços"""
        self.running = False
        logger.info("Coleta de preços interrompida")

# Instância global do coletor
price_collector = BitcoinPriceCollector()
