"""
Script para limpar previsões antigas do banco de dados.
Mantém apenas os últimos 90 dias de previsões conforme especificado.

Uso:
    python scripts/cleanup_old_predictions.py [--days 90]
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))

from core.database import SessionLocal
from services.prediction_storage_service import prediction_storage_service
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_predictions(days: int = 90):
    """
    Remove previsões mais antigas que o número especificado de dias.
    
    Args:
        days: Número de dias de retenção (padrão: 90)
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Iniciando limpeza de previsões com mais de {days} dias...")
        
        deleted_count = prediction_storage_service.cleanup_old_predictions(db, days=days)
        
        if deleted_count > 0:
            logger.info(f"✅ Limpeza concluída com sucesso! {deleted_count} registros removidos.")
        else:
            logger.info("ℹ️ Nenhum registro antigo encontrado para remoção.")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Erro durante a limpeza: {str(e)}")
        raise
    finally:
        db.close()


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Limpar previsões antigas do banco de dados"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Número de dias de retenção (padrão: 90)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("SCRIPT DE LIMPEZA DE PREVISÕES ANTIGAS")
    logger.info("=" * 60)
    
    deleted_count = cleanup_predictions(days=args.days)
    
    logger.info("=" * 60)
    logger.info("RESUMO")
    logger.info(f"Registros removidos: {deleted_count}")
    logger.info(f"Retenção configurada: {args.days} dias")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
