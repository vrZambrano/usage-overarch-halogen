import asyncio
import aiohttp
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.database import BitcoinPrice
from utils.logger import app_logger

logger = app_logger

class BitcoinPriceCollector:
    def __init__(self):
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna uma sessão HTTP reutilizável"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_bitcoin_price(self) -> Optional[float]:
        """Busca o preço atual do Bitcoin da API da Binance"""
        session = await self._get_session()
        try:
            async with session.get(self.api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['price'])
                else:
                    logger.error(f"Erro na API Binance: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error("Timeout ao buscar preço do Bitcoin")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão com API Binance: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar preço: {e}")
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
        if self.running:
            logger.warning("Tentativa de iniciar coleta já em andamento")
            return
            
        self.running = True
        logger.info("Iniciando coleta de preços do Bitcoin...")
        
        while self.running:
            try:
                price = await self.fetch_bitcoin_price()
                if price:
                    self.save_price(price)
                else:
                    logger.warning("Não foi possível obter o preço do Bitcoin")
                
                # Aguarda 1 minuto ou até ser interrompido
                try:
                    await asyncio.wait_for(asyncio.sleep(60), timeout=60)
                except asyncio.CancelledError:
                    logger.info("Coleta interrompida durante sleep")
                    break
                    
            except asyncio.CancelledError:
                logger.info("Tarefa de coleta cancelada")
                break
            except Exception as e:
                logger.error(f"Erro na coleta de preços: {e}")
                # Aguarda antes de tentar novamente
                try:
                    await asyncio.wait_for(asyncio.sleep(10), timeout=10)
                except asyncio.CancelledError:
                    break
    
    async def stop_collection(self):
        """Para a coleta de preços de forma graciosa"""
        if not self.running:
            return
            
        self.running = False
        logger.info("Iniciando encerramento gracioso da coleta de preços...")
        
        # Fecha a sessão HTTP
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Sessão HTTP fechada")
        
        # Aguarda a conclusão da tarefa atual
        if self.collection_task and not self.collection_task.done():
            try:
                await asyncio.wait_for(self.collection_task, timeout=5.0)
                logger.info("Tarefa de coleta concluída com sucesso")
            except asyncio.TimeoutError:
                logger.warning("Timeout ao aguardar conclusão da tarefa de coleta")
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Coleta de preços interrompida com sucesso")

# Instância global do coletor
price_collector = BitcoinPriceCollector()
