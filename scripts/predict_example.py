#!/usr/bin/env python3
"""
Exemplo de como fazer previsões com o modelo de Bitcoin

Este script demonstra diferentes formas de usar o modelo de previsão:
1. Previsão simples usando o modelo mais recente
2. Previsão com dados customizados
3. Análise das features usadas no modelo
"""

import pandas as pd
import mlflow
from sqlalchemy.orm import Session

# Imports do projeto
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_db
from src.services.bitcoin_service import bitcoin_service
from src.services.prediction_service import get_latest_prediction


def predict_with_latest_model():
    """
    Faz previsão usando o modelo mais recente e os dados mais atuais.
    """
    print("=== Previsão com modelo mais recente ===")
    
    try:
        prediction = get_latest_prediction()
        print(f"Previsão do preço do Bitcoin: ${prediction:.2f}")
        return prediction
    except Exception as e:
        print(f"Erro: {e}")
        return None


def analyze_model_features():
    """
    Analisa as features que o modelo usa para fazer previsões.
    """
    print("\n=== Análise das Features do Modelo ===")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Pega os dados mais recentes com features
        data = bitcoin_service.get_price_history_with_features(db, limit=5)
        if not data:
            print("Nenhum dado disponível")
            return
        
        df = pd.DataFrame(data)
        
        # Identifica as features usadas pelo modelo
        feature_cols = [col for col in df.columns if col.startswith("price_t-") or col.startswith("ma_")]
        
        print(f"Features usadas pelo modelo: {feature_cols}")
        print(f"Dados mais recentes para previsão:")
        
        # Mostra os valores das features
        latest_features = df[feature_cols].iloc[0]
        for feature, value in latest_features.items():
            print(f"  {feature}: ${float(value):.2f}")
        
        # Mostra o preço atual (target)
        current_price = df["price"].iloc[0]
        print(f"\nPreço atual: ${float(current_price):.2f}")
        
        return df[feature_cols].iloc[0]
        
    finally:
        db.close()


def predict_with_custom_features(custom_features=None):
    """
    Faz previsão com features customizadas.
    
    Args:
        custom_features: Dict com valores customizados para as features
    """
    print("\n=== Previsão com Features Customizadas ===")
    
    if custom_features is None:
        # Exemplo de features customizadas
        custom_features = {
            "price_t-1": 106000.0,  # Preço há 1 período
            "price_t-2": 105500.0,  # Preço há 2 períodos
            "price_t-3": 105000.0,  # Preço há 3 períodos
            "price_t-4": 104500.0,  # Preço há 4 períodos
            "price_t-5": 104000.0,  # Preço há 5 períodos
            "ma_10": 105200.0,      # Média móvel de 10 períodos
        }
    
    try:
        # Configura o experimento
        mlflow.set_experiment("bitcoin_prediction_s3")
        
        # Pega o modelo mais recente
        runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
        if len(runs) == 0:
            print("Nenhum modelo encontrado. Treine um modelo primeiro.")
            return None
        
        latest_run_id = runs.iloc[0]["run_id"]
        logged_model = f"runs:/{latest_run_id}/linear_regression_model"
        model = mlflow.pyfunc.load_model(logged_model)
        
        # Prepara os dados de entrada
        X_custom = pd.DataFrame([custom_features])
        
        print("Features customizadas:")
        for feature, value in custom_features.items():
            print(f"  {feature}: ${value:.2f}")
        
        # Faz a previsão
        prediction = model.predict(X_custom)
        
        print(f"\nPrevisão com dados customizados: ${prediction[0]:.2f}")
        return prediction[0]
        
    except Exception as e:
        print(f"Erro na previsão customizada: {e}")
        return None


def compare_predictions():
    """
    Compara diferentes cenários de previsão.
    """
    print("\n=== Comparação de Cenários ===")
    
    # Cenário 1: Tendência de alta
    alta_scenario = {
        "price_t-1": 108000.0,
        "price_t-2": 107500.0,
        "price_t-3": 107000.0,
        "price_t-4": 106500.0,
        "price_t-5": 106000.0,
        "ma_10": 106800.0,
    }
    
    # Cenário 2: Tendência de baixa
    baixa_scenario = {
        "price_t-1": 104000.0,
        "price_t-2": 104500.0,
        "price_t-3": 105000.0,
        "price_t-4": 105500.0,
        "price_t-5": 106000.0,
        "ma_10": 105000.0,
    }
    
    # Cenário 3: Estabilidade
    estavel_scenario = {
        "price_t-1": 106000.0,
        "price_t-2": 106100.0,
        "price_t-3": 105900.0,
        "price_t-4": 106050.0,
        "price_t-5": 105950.0,
        "ma_10": 106000.0,
    }
    
    scenarios = [
        ("Tendência de Alta", alta_scenario),
        ("Tendência de Baixa", baixa_scenario),
        ("Mercado Estável", estavel_scenario),
    ]
    
    for name, scenario in scenarios:
        print(f"\n{name}:")
        prediction = predict_with_custom_features(scenario)
        if prediction:
            trend = "Alta" if prediction > scenario["price_t-1"] else "Baixa"
            change = abs(prediction - scenario["price_t-1"])
            print(f"  Tendência prevista: {trend} (${change:.2f})")


def main():
    """
    Função principal que executa todos os exemplos.
    """
    print("🚀 Exemplos de Previsão do Preço do Bitcoin\n")
    
    # 1. Previsão básica
    predict_with_latest_model()
    
    # 2. Análise das features
    analyze_model_features()
    
    # 3. Previsão customizada
    predict_with_custom_features()
    
    # 4. Comparação de cenários
    compare_predictions()
    
    print("\n✅ Exemplos concluídos!")


if __name__ == "__main__":
    main()