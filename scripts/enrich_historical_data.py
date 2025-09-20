#!/usr/bin/env python3
"""
Script para enriquecer dados históricos do Bitcoin com features de machine learning.

Este script processa todos os dados históricos da tabela bitcoin_prices,
aplica feature engineering e salva os resultados na tabela modeldb_bitcoin_features.

Uso:
    python scripts/enrich_historical_data.py [--limit N] [--batch-size N]

Argumentos:
    --limit N: Limita o processamento a N registros (padrão: todos)
    --batch-size N: Tamanho do lote para inserção (padrão: 1000)
    --help: Mostra esta ajuda
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.data_enricher import DataEnricher

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('enrich_historical_data.log')
        ]
    )

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(
        description='Enriquece dados históricos do Bitcoin com features de ML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limita o processamento a N registros (padrão: todos)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamanho do lote para inserção no banco (padrão: 1000)'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Apenas mostra estatísticas dos dados existentes'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("INICIANDO ENRIQUECIMENTO DE DADOS HISTÓRICOS")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {datetime.now()}")
    
    if args.limit:
        logger.info(f"Limite de registros: {args.limit}")
    else:
        logger.info("Processando todos os registros disponíveis")
    
    logger.info(f"Tamanho do lote: {args.batch_size}")
    
    try:
        # Criar instância do enriquecedor
        enricher = DataEnricher()
        
        # Se apenas estatísticas
        if args.stats_only:
            logger.info("Obtendo estatísticas dos dados enriquecidos...")
            stats = enricher.get_enriched_data_stats()
            
            print("\n" + "=" * 50)
            print("ESTATÍSTICAS DOS DADOS ENRIQUECIDOS")
            print("=" * 50)
            print(f"Total de registros: {stats.get('total_records', 0)}")
            print(f"Total de features: {stats.get('total_features', 0)}")
            print(f"Registro mais antigo: {stats.get('oldest_record', 'N/A')}")
            print(f"Registro mais recente: {stats.get('newest_record', 'N/A')}")
            print("=" * 50)
            
            return
        
        # Executar enriquecimento
        logger.info("Iniciando processo de enriquecimento...")
        start_time = datetime.now()
        
        success = enricher.enrich_historical_data(
            limit=args.limit,
            batch_size=args.batch_size
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            logger.info("=" * 60)
            logger.info("ENRIQUECIMENTO CONCLUÍDO COM SUCESSO!")
            logger.info("=" * 60)
            logger.info(f"Tempo total: {duration}")
            
            # Mostrar estatísticas finais
            stats = enricher.get_enriched_data_stats()
            logger.info(f"Total de registros processados: {stats.get('total_records', 0)}")
            logger.info(f"Total de features criadas: {stats.get('total_features', 0)}")
            
            print("\n" + "=" * 50)
            print("RESUMO DO PROCESSAMENTO")
            print("=" * 50)
            print(f"✅ Status: SUCESSO")
            print(f"⏱️  Tempo total: {duration}")
            print(f"📊 Registros processados: {stats.get('total_records', 0)}")
            print(f"🔧 Features criadas: {stats.get('total_features', 0)}")
            print(f"📅 Período: {stats.get('oldest_record', 'N/A')} até {stats.get('newest_record', 'N/A')}")
            print("=" * 50)
            
        else:
            logger.error("=" * 60)
            logger.error("ENRIQUECIMENTO FALHOU!")
            logger.error("=" * 60)
            logger.error(f"Tempo decorrido: {duration}")
            
            print("\n" + "=" * 50)
            print("RESUMO DO PROCESSAMENTO")
            print("=" * 50)
            print(f"❌ Status: FALHA")
            print(f"⏱️  Tempo decorrido: {duration}")
            print("Verifique os logs para mais detalhes.")
            print("=" * 50)
            
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("Processamento interrompido pelo usuário")
        print("\n⚠️  Processamento interrompido pelo usuário")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
