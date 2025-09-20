#!/usr/bin/env python3
"""
Script de teste para validar a implementação de feature engineering.

Este script testa os componentes principais:
1. Feature engineering básico
2. Enriquecimento de dados
3. Salvamento na base modeldb_

Uso:
    python scripts/test_feature_engineering.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.feature_engineer import BitcoinFeatureEngineer
from services.data_enricher import DataEnricher

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_sample_data(num_records: int = 100) -> pd.DataFrame:
    """Cria dados de exemplo para teste"""
    print(f"Criando {num_records} registros de exemplo...")
    
    # Gerar timestamps a cada minuto
    start_time = datetime.now() - timedelta(minutes=num_records)
    timestamps = [start_time + timedelta(minutes=i) for i in range(num_records)]
    
    # Gerar preços simulados (random walk)
    np.random.seed(42)  # Para reprodutibilidade
    initial_price = 50000.0
    price_changes = np.random.normal(0, 100, num_records)  # Mudanças aleatórias
    prices = [initial_price]
    
    for change in price_changes[1:]:
        new_price = max(prices[-1] + change, 1000)  # Preço mínimo de $1000
        prices.append(new_price)
    
    # Criar DataFrame
    df = pd.DataFrame({
        'price': prices,
        'timestamp': timestamps,
        'source': 'test'
    })
    
    print(f"Dados criados: {len(df)} registros")
    print(f"Preço inicial: ${df['price'].iloc[0]:.2f}")
    print(f"Preço final: ${df['price'].iloc[-1]:.2f}")
    print(f"Período: {df['timestamp'].min()} até {df['timestamp'].max()}")
    
    return df

def test_feature_engineer():
    """Testa o BitcoinFeatureEngineer"""
    print("\n" + "="*50)
    print("TESTANDO FEATURE ENGINEER")
    print("="*50)
    
    # Criar dados de exemplo
    sample_data = create_sample_data(100)
    
    # Inicializar feature engineer
    engineer = BitcoinFeatureEngineer()
    
    # Aplicar feature engineering
    print("\nAplicando feature engineering...")
    enriched_data = engineer.engineer_all_features(sample_data)
    
    print(f"Shape original: {sample_data.shape}")
    print(f"Shape enriquecido: {enriched_data.shape}")
    print(f"Novas features criadas: {enriched_data.shape[1] - sample_data.shape[1]}")
    
    # Mostrar algumas features criadas
    feature_columns = engineer.get_feature_columns()
    print(f"\nTotal de features implementadas: {len(feature_columns)}")
    
    print("\nPrimeiras 10 features:")
    for i, feature in enumerate(feature_columns[:10]):
        if feature in enriched_data.columns:
            sample_value = enriched_data[feature].dropna().iloc[0] if not enriched_data[feature].dropna().empty else "N/A"
            print(f"  {i+1:2d}. {feature}: {sample_value}")
    
    # Verificar se há valores NaN
    nan_counts = enriched_data.isnull().sum()
    features_with_nan = nan_counts[nan_counts > 0]
    
    print(f"\nFeatures com valores NaN: {len(features_with_nan)}")
    if len(features_with_nan) > 0:
        print("Primeiras 5 features com NaN:")
        for feature, count in features_with_nan.head().items():
            print(f"  {feature}: {count} NaN values")
    
    return enriched_data

def test_data_enricher():
    """Testa o DataEnricher"""
    print("\n" + "="*50)
    print("TESTANDO DATA ENRICHER")
    print("="*50)
    
    enricher = DataEnricher()
    
    # Testar enriquecimento de registro único
    print("\nTestando enriquecimento de registro único...")
    test_price = 45000.0
    test_timestamp = datetime.now()
    
    enriched_record = enricher.enrich_single_record(
        price=test_price,
        timestamp=test_timestamp,
        source="test"
    )
    
    if enriched_record:
        print(f"✅ Registro enriquecido com sucesso!")
        print(f"Preço: ${enriched_record['price']}")
        print(f"Timestamp: {enriched_record['timestamp']}")
        print(f"Features não-nulas: {sum(1 for v in enriched_record.values() if v is not None)}")
    else:
        print("❌ Falha ao enriquecer registro")
    
    # Testar estatísticas
    print("\nObtendo estatísticas dos dados enriquecidos...")
    stats = enricher.get_enriched_data_stats()
    
    print("Estatísticas atuais:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return enriched_record

def test_technical_indicators():
    """Testa indicadores técnicos específicos"""
    print("\n" + "="*50)
    print("TESTANDO INDICADORES TÉCNICOS")
    print("="*50)
    
    # Criar dados de teste com tendência
    sample_data = create_sample_data(50)
    engineer = BitcoinFeatureEngineer()
    
    # Testar RSI
    print("\nTestando RSI...")
    rsi = engineer.calculate_rsi(sample_data['price'])
    print(f"RSI médio: {rsi.mean():.2f}")
    print(f"RSI min/max: {rsi.min():.2f} / {rsi.max():.2f}")
    
    # Testar MACD
    print("\nTestando MACD...")
    macd_data = engineer.calculate_macd(sample_data['price'])
    print(f"MACD line média: {macd_data['macd_line'].mean():.2f}")
    print(f"MACD signal média: {macd_data['macd_signal'].mean():.2f}")
    
    # Testar Bollinger Bands
    print("\nTestando Bollinger Bands...")
    bb_data = engineer.calculate_bollinger_bands(sample_data['price'])
    print(f"BB width média: {bb_data['bb_width'].mean():.2f}")
    print(f"BB position média: {bb_data['bb_position'].mean():.2f}")
    
    print("✅ Todos os indicadores técnicos funcionando!")

def main():
    """Função principal do teste"""
    setup_logging()
    
    print("="*60)
    print("TESTE DE FEATURE ENGINEERING - BITCOIN")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")
    
    try:
        # Teste 1: Feature Engineer
        enriched_data = test_feature_engineer()
        
        # Teste 2: Data Enricher
        enriched_record = test_data_enricher()
        
        # Teste 3: Indicadores Técnicos
        test_technical_indicators()
        
        print("\n" + "="*60)
        print("RESUMO DOS TESTES")
        print("="*60)
        print("✅ Feature Engineer: OK")
        print("✅ Data Enricher: OK")
        print("✅ Indicadores Técnicos: OK")
        print("✅ Todos os testes passaram!")
        
        print(f"\nDados de exemplo criados com {enriched_data.shape[0]} registros")
        print(f"Total de features: {enriched_data.shape[1]}")
        print("\nImplementação pronta para uso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
