"""
Exemplos de uso da API de Predição de Bitcoin

Este script demonstra como consumir os endpoints da API para:
1. Obter predições de preço
2. Obter predições de tendência
3. Analisar importância das features
4. Monitorar continuamente as predições
"""

import requests
import time
from datetime import datetime
from typing import Dict, Any
import json

# Base URL da API
BASE_URL = "http://localhost:8000"


class BitcoinPredictionClient:
    """Cliente para consumir a API de predição de Bitcoin"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_latest_price(self) -> Dict[str, Any]:
        """Obtém o último preço registrado"""
        response = requests.get(f"{self.base_url}/price/latest")
        response.raise_for_status()
        return response.json()
    
    def predict_price(self) -> Dict[str, Any]:
        """Obtém predição de preço para 15 minutos à frente"""
        response = requests.get(f"{self.base_url}/price/predict/next")
        response.raise_for_status()
        return response.json()
    
    def predict_trend(self) -> Dict[str, Any]:
        """Obtém predição de tendência (UP/DOWN)"""
        response = requests.get(f"{self.base_url}/trend/predict")
        response.raise_for_status()
        return response.json()
    
    def get_feature_importance(self) -> Dict[str, Any]:
        """Obtém importância das features do modelo de tendência"""
        response = requests.get(f"{self.base_url}/trend/feature-importance")
        response.raise_for_status()
        return response.json()
    
    def get_price_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas de preço"""
        response = requests.get(f"{self.base_url}/price/stats?hours={hours}")
        response.raise_for_status()
        return response.json()


def example_1_price_prediction():
    """Exemplo 1: Predição de Preço"""
    print("\n" + "="*80)
    print("EXEMPLO 1: Predição de Preço 15 Minutos à Frente")
    print("="*80)
    
    client = BitcoinPredictionClient()
    
    try:
        # Obter predição
        prediction = client.predict_price()
        
        print(f"\n📊 Preço Atual: ${prediction['current_price']:,.2f}")
        print(f"🔮 Preço Previsto (15min): ${prediction['predicted_price']:,.2f}")
        print(f"📈 Mudança Esperada: ${prediction['price_change']:,.2f} ({prediction['price_change_percent']:.2f}%)")
        print(f"⏰ Timestamp: {prediction['timestamp']}")
        print(f"\n🎯 Métricas do Modelo:")
        print(f"   MAE (Erro Médio Absoluto): ${prediction['model_mae']:.2f}")
        print(f"   MAPE (Erro Percentual): {prediction['model_mape']:.2f}%")
        print(f"   Run ID: {prediction['run_id']}")
        
        # Interpretar resultado
        if prediction['price_change_percent'] > 0.5:
            print(f"\n✅ INTERPRETAÇÃO: Expectativa de ALTA significativa (+{prediction['price_change_percent']:.2f}%)")
        elif prediction['price_change_percent'] < -0.5:
            print(f"\n⚠️ INTERPRETAÇÃO: Expectativa de BAIXA significativa ({prediction['price_change_percent']:.2f}%)")
        else:
            print(f"\n➡️ INTERPRETAÇÃO: Expectativa de ESTABILIDADE ({prediction['price_change_percent']:.2f}%)")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("\n❌ Modelo não encontrado. Execute: python scripts/train_model.py")
        else:
            print(f"\n❌ Erro: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_2_trend_prediction():
    """Exemplo 2: Predição de Tendência"""
    print("\n" + "="*80)
    print("EXEMPLO 2: Classificação de Tendência (UP/DOWN)")
    print("="*80)
    
    client = BitcoinPredictionClient()
    
    try:
        # Obter predição de tendência
        trend = client.predict_trend()
        
        print(f"\n📊 Preço Atual: ${trend['current_price']:,.2f}")
        print(f"🔮 Tendência Prevista: {trend['trend']}")
        print(f"💯 Confiança: {trend['confidence']*100:.1f}%")
        print(f"\n📊 Probabilidades:")
        print(f"   ⬆️ Alta (UP): {trend['probability_up']*100:.1f}%")
        print(f"   ⬇️ Baixa (DOWN): {trend['probability_down']*100:.1f}%")
        print(f"\n🎯 Métricas do Modelo:")
        print(f"   Acurácia: {trend['model_accuracy']*100:.1f}%")
        print(f"   F1-Score: {trend['model_f1_score']*100:.1f}%")
        print(f"   Run ID: {trend['run_id']}")
        
        # Sinal de trading
        print(f"\n{'='*80}")
        if trend['trend'] == 'UP' and trend['confidence'] > 0.7:
            print("✅ SINAL DE TRADING: COMPRA FORTE")
            print(f"   Confiança Alta ({trend['confidence']*100:.1f}%) para tendência de ALTA")
        elif trend['trend'] == 'UP':
            print("🟢 SINAL DE TRADING: COMPRA MODERADA")
            print(f"   Confiança Moderada ({trend['confidence']*100:.1f}%) para tendência de ALTA")
        elif trend['trend'] == 'DOWN' and trend['confidence'] > 0.7:
            print("⛔ SINAL DE TRADING: VENDA FORTE")
            print(f"   Confiança Alta ({trend['confidence']*100:.1f}%) para tendência de BAIXA")
        else:
            print("🟡 SINAL DE TRADING: VENDA MODERADA")
            print(f"   Confiança Moderada ({trend['confidence']*100:.1f}%) para tendência de BAIXA")
        print("="*80)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("\n❌ Modelo não encontrado. Execute: python scripts/train_trend_model.py")
        else:
            print(f"\n❌ Erro: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_3_feature_importance():
    """Exemplo 3: Análise de Importância das Features"""
    print("\n" + "="*80)
    print("EXEMPLO 3: Análise de Importância das Features")
    print("="*80)
    
    client = BitcoinPredictionClient()
    
    try:
        # Obter importância das features
        importance_data = client.get_feature_importance()
        
        print(f"\n📊 Total de Features: {importance_data['total_features']}")
        print(f"\n🏆 Top 10 Features Mais Importantes:\n")
        
        for i, feature in enumerate(importance_data['features'][:10], 1):
            bar_length = int(feature['importance'] * 100)
            bar = "█" * bar_length
            print(f"{i:2d}. {feature['feature']:25s} {bar} {feature['importance']:.4f}")
        
        # Análise por categoria
        print(f"\n📈 Análise por Categoria de Indicadores:")
        
        categories = {
            'Momentum': ['rsi', 'momentum', 'stoch'],
            'Tendência': ['macd', 'rolling_mean', 'ma_'],
            'Volatilidade': ['bb_', 'atr', 'volatility', 'rolling_std'],
            'Temporal': ['hour', 'day', 'minute', 'week'],
            'Lag': ['lag']
        }
        
        for category, keywords in categories.items():
            category_features = [
                f for f in importance_data['features'] 
                if any(kw in f['feature'].lower() for kw in keywords)
            ]
            if category_features:
                total_importance = sum(f['importance'] for f in category_features)
                print(f"\n   {category}: {len(category_features)} features, importância total: {total_importance:.4f}")
                for f in category_features[:3]:
                    print(f"      - {f['feature']}: {f['importance']:.4f}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("\n❌ Modelo não encontrado. Execute: python scripts/train_trend_model.py")
        else:
            print(f"\n❌ Erro: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_4_combined_analysis():
    """Exemplo 4: Análise Combinada"""
    print("\n" + "="*80)
    print("EXEMPLO 4: Análise Combinada de Preço e Tendência")
    print("="*80)
    
    client = BitcoinPredictionClient()
    
    try:
        # Obter ambas as predições
        price_pred = client.predict_price()
        trend_pred = client.predict_trend()
        stats = client.get_price_stats(hours=24)
        
        print(f"\n📊 SITUAÇÃO ATUAL")
        print(f"{'='*80}")
        print(f"Preço Atual: ${price_pred['current_price']:,.2f}")
        print(f"Min (24h): ${stats['min_price']:,.2f}")
        print(f"Max (24h): ${stats['max_price']:,.2f}")
        print(f"Média (24h): ${stats['avg_price']:,.2f}")
        
        print(f"\n🔮 PREDIÇÕES PARA 15 MINUTOS")
        print(f"{'='*80}")
        print(f"Preço Previsto: ${price_pred['predicted_price']:,.2f} ({price_pred['price_change_percent']:+.2f}%)")
        print(f"Tendência: {trend_pred['trend']} (Confiança: {trend_pred['confidence']*100:.1f}%)")
        
        # Análise combinada
        print(f"\n💡 ANÁLISE COMBINADA")
        print(f"{'='*80}")
        
        price_bullish = price_pred['price_change_percent'] > 0
        trend_bullish = trend_pred['trend'] == 'UP'
        high_confidence = trend_pred['confidence'] > 0.7
        
        if price_bullish and trend_bullish and high_confidence:
            signal = "🟢 COMPRA FORTE"
            reason = "Ambos os modelos concordam em tendência de ALTA com alta confiança"
        elif price_bullish and trend_bullish:
            signal = "🟢 COMPRA MODERADA"
            reason = "Ambos os modelos indicam tendência de ALTA"
        elif not price_bullish and not trend_bullish and high_confidence:
            signal = "🔴 VENDA FORTE"
            reason = "Ambos os modelos concordam em tendência de BAIXA com alta confiança"
        elif not price_bullish and not trend_bullish:
            signal = "🔴 VENDA MODERADA"
            reason = "Ambos os modelos indicam tendência de BAIXA"
        else:
            signal = "🟡 AGUARDAR"
            reason = "Modelos divergem ou baixa confiança"
        
        print(f"Sinal: {signal}")
        print(f"Razão: {reason}")
        
        print(f"\n📋 DETALHES:")
        print(f"   - Modelo de Preço: {'+' if price_bullish else '-'}{abs(price_pred['price_change_percent']):.2f}%")
        print(f"   - Modelo de Tendência: {trend_pred['trend']} ({trend_pred['confidence']*100:.1f}%)")
        print(f"   - Concordância: {'Sim ✓' if price_bullish == trend_bullish else 'Não ✗'}")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_5_monitor_continuous():
    """Exemplo 5: Monitoramento Contínuo"""
    print("\n" + "="*80)
    print("EXEMPLO 5: Monitoramento Contínuo de Predições")
    print("="*80)
    print("\nMonitorando predições a cada 60 segundos... (Ctrl+C para parar)\n")
    
    client = BitcoinPredictionClient()
    
    try:
        while True:
            try:
                # Obter predições
                price_pred = client.predict_price()
                trend_pred = client.predict_trend()
                
                # Exibir resumo
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Preço: ${price_pred['current_price']:,.2f} | "
                      f"Prev: ${price_pred['predicted_price']:,.2f} ({price_pred['price_change_percent']:+.2f}%) | "
                      f"Tendência: {trend_pred['trend']} ({trend_pred['confidence']*100:.0f}%)")
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro: {e}")
            
            # Aguardar 60 segundos
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\nMonitoramento interrompido pelo usuário.")


def main():
    """Função principal - executa todos os exemplos"""
    print("\n" + "="*80)
    print(" Bitcoin ML Prediction API - Exemplos de Uso")
    print("="*80)
    
    # Verificar se a API está disponível
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        print("\n✅ API está disponível e funcionando!")
    except:
        print("\n❌ API não está disponível. Inicie a API primeiro:")
        print("   cd src && python main.py")
        return
    
    # Menu de exemplos
    while True:
        print("\n" + "="*80)
        print("Escolha um exemplo:")
        print("  1. Predição de Preço")
        print("  2. Classificação de Tendência")
        print("  3. Análise de Importância das Features")
        print("  4. Análise Combinada")
        print("  5. Monitoramento Contínuo")
        print("  0. Sair")
        print("="*80)
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            example_1_price_prediction()
        elif choice == "2":
            example_2_trend_prediction()
        elif choice == "3":
            example_3_feature_importance()
        elif choice == "4":
            example_4_combined_analysis()
        elif choice == "5":
            example_5_monitor_continuous()
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
        
        if choice != "5":
            input("\nPressione ENTER para continuar...")


def example_h2o_automl():
    """Exemplos de uso do H2O AutoML"""
    print("\n" + "=" * 80)
    print("EXEMPLO 4: H2O AutoML - Predição Automatizada")
    print("=" * 80)
    
    try:
        # Predição com H2O AutoML
        response = requests.get(f"{BASE_URL}/price/predict/h2o")
        
        if response.status_code == 200:
            h2o_pred = response.json()
            
            print(f"\n🤖 Predição H2O AutoML:")
            print(f"   Algoritmo Selecionado: {h2o_pred['model_type']}")
            print(f"   Preço Atual: ${h2o_pred['current_price']:,.2f}")
            print(f"   Preço Previsto (15min): ${h2o_pred['predicted_price']:,.2f}")
            print(f"   Mudança Esperada: {h2o_pred['price_change_percent']:+.2f}%")
            print(f"\n📊 Métricas do Modelo:")
            print(f"   RMSE: ${h2o_pred['model_rmse']:.2f}")
            print(f"   MAE: ${h2o_pred['model_mae']:.2f}")
            print(f"   MAPE: {h2o_pred['model_mape']:.2f}%")
            print(f"   R²: {h2o_pred['model_r2']:.4f}")
            
            # Obter leaderboard
            lb_response = requests.get(f"{BASE_URL}/h2o/leaderboard")
            if lb_response.status_code == 200:
                leaderboard = lb_response.json()
                print(f"\n🏆 H2O AutoML Leaderboard (Top 5):")
                print(f"   Total de Modelos Testados: {leaderboard['total_models']}")
                print(f"   Melhor Modelo: {leaderboard['best_model']}")
                print("\n   Ranking:")
                
                for i, model in enumerate(leaderboard['leaderboard'][:5], 1):
                    print(f"   {i}. {model['model_id']}")
                    print(f"      RMSE: {model['rmse']:.2f} | MAE: {model['mae']:.2f}")
        
        elif response.status_code == 404:
            print("\n⚠️  Modelo H2O AutoML não encontrado.")
            print("   Execute: poetry run python scripts/train_h2o_model.py")
        else:
            print(f"\n❌ Erro ao buscar predição H2O: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão: {e}")


def compare_all_models():
    """Compara os três modelos de predição de preço"""
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Comparação de Todos os Modelos")
    print("=" * 80)
    
    try:
        # XGBoost Manual
        xgb_response = requests.get(f"{BASE_URL}/price/predict/next")
        
        # H2O AutoML
        h2o_response = requests.get(f"{BASE_URL}/price/predict/h2o")
        
        # Trend
        trend_response = requests.get(f"{BASE_URL}/trend/predict")
        
        print("\n📊 Comparação de Modelos de Predição de Preço:\n")
        print(f"{'Modelo':<20} {'Preço Previsto':<15} {'Mudança %':<12} {'MAE':<10} {'Métrica Extra'}")
        print("-" * 80)
        
        if xgb_response.status_code == 200:
            xgb = xgb_response.json()
            print(f"{'XGBoost Manual':<20} ${xgb['predicted_price']:>12,.2f} {xgb['price_change_percent']:>10.2f}% ${xgb['model_mae']:>8.2f} MAPE: {xgb['model_mape']:.2f}%")
        else:
            print(f"{'XGBoost Manual':<20} {'Não disponível'}")
        
        if h2o_response.status_code == 200:
            h2o = h2o_response.json()
            print(f"{'H2O AutoML':<20} ${h2o['predicted_price']:>12,.2f} {h2o['price_change_percent']:>10.2f}% ${h2o['model_mae']:>8.2f} R²: {h2o['model_r2']:.4f}")
            print(f"{'  └─ ' + h2o['model_type']:<18}")
        else:
            print(f"{'H2O AutoML':<20} {'Não disponível'}")
        
        print("\n📈 Modelo de Classificação de Tendência:\n")
        
        if trend_response.status_code == 200:
            trend = trend_response.json()
            print(f"   Tendência Prevista: {trend['trend']}")
            print(f"   Confiança: {trend['confidence']*100:.1f}%")
            print(f"   Prob. Alta: {trend['probability_up']*100:.1f}% | Prob. Baixa: {trend['probability_down']*100:.1f}%")
            
            if trend['trend'] == 'UP':
                print(f"   Sinal: ✅ COMPRA")
            else:
                print(f"   Sinal: ⚠️ VENDA")
        else:
            print(f"   Modelo de tendência não disponível")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão: {e}")


if __name__ == "__main__":
    main()
    example_h2o_automl()
    compare_all_models()
