from sqlalchemy import create_engine, Column, Integer, Numeric, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://bitcoin_user:bitcoin_password@localhost:5432/bitcoin_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo da tabela
class BitcoinPrice(Base):
    __tablename__ = "bitcoin_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50), default="binance")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Criar as tabelas
Base.metadata.create_all(bind=engine)

# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
