# Guia de Previsão do Modelo de Bitcoin

Este documento explica como funciona o modelo de previsão de preços do Bitcoin e como utilizá-lo.

## Como Funciona o Modelo

### 1. Tipo de Modelo
- **Algoritmo**: Regressão Linear (`sklearn.linear_model.LinearRegression`)
- **Tipo**: Modelo de série temporal supervisionado
- **Objetivo**: Prever o próximo preço do Bitcoin baseado em preços históricos

### 2. Features (Variáveis de Entrada)
O modelo usa 6 features principais:

- **`price_t-1`**: Preço do Bitcoin há 1 período atrás
- **`price_t-2`**: Preço do Bitcoin há 2 períodos atrás  
- **`price_t-3`**: Preço do Bitcoin há 3 períodos atrás
- **`price_t-4`**: Preço do Bitcoin há 4 períodos atrás
- **`price_t-5`**: Preço do Bitcoin há 5 períodos atrás
- **`ma_10`**: Média móvel dos últimos 10 períodos

### 3. Target (Variável Alvo)
- **`price`**: Preço atual do Bitcoin (o que queremos prever)

## Como Fazer Previsões

### 1. Previsão Simples (API)
```bash
# Via API REST
curl http://localhost:8000/price/predict

# Resposta:
# {"predicted_price": 107301.53}
```

### 2. Previsão Programática
```python
from src.services.prediction_service import get_latest_prediction

# Previsão com dados mais recentes
prediction = get_latest_prediction()
print(f"Previsão: ${prediction:.2f}")
```

### 3. Previsão com Dados Customizados
```python
import pandas as pd
import mlflow

# Configura o experimento
mlflow.set_experiment("bitcoin_prediction_s3")

# Carrega o modelo
runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=1)
run_id = runs.iloc[0]["run_id"]
model = mlflow.pyfunc.load_model(f"runs:/{run_id}/linear_regression_model")

# Dados customizados
custom_data = pd.DataFrame([{
    "price_t-1": 106000.0,
    "price_t-2": 105500.0,
    "price_t-3": 105000.0,
    "price_t-4": 104500.0,
    "price_t-5": 104000.0,
    "ma_10": 105200.0,
}])

# Faz a previsão
prediction = model.predict(custom_data)
print(f"Previsão customizada: ${prediction[0]:.2f}")
```

## Interpretação dos Resultados

### 1. Análise de Tendência
- **Alta**: Se a previsão > preço mais recente (price_t-1)
- **Baixa**: Se a previsão < preço mais recente (price_t-1)
- **Estável**: Se a diferença for muito pequena (< $50)

### 2. Confiabilidade
O modelo atual é um **modelo simples** adequado para:
- ✅ Demonstração e prototipagem
- ✅ Identificação de tendências básicas
- ✅ Análise de padrões de curto prazo

**Limitações**:
- ❌ Não considera fatores externos (notícias, eventos)
- ❌ Baseado apenas em preços históricos
- ❌ Regressão linear pode não capturar padrões complexos

### 3. Métricas de Performance
- **R² Score**: Disponível no MLflow para avaliar o ajuste do modelo
- **Visualização**: Acesse http://localhost:5001 para ver experimentos

## Exemplos Práticos

### Cenário 1: Mercado em Alta
```
Features:
  price_t-1: $108000.00
  price_t-2: $107500.00  
  price_t-3: $107000.00
  ...
  
Previsão: $107940.71
Tendência: Leve correção (-$59)
```

### Cenário 2: Mercado em Baixa
```
Features:
  price_t-1: $104000.00
  price_t-2: $104500.00
  price_t-3: $105000.00
  ...
  
Previsão: $103906.39
Tendência: Continuação da queda (-$94)
```

### Cenário 3: Mercado Estável
```
Features:
  price_t-1: $106000.00
  price_t-2: $106100.00
  price_t-3: $105900.00
  ...
  
Previsão: $105978.75
Tendência: Estabilidade (-$21)
```

## Melhorias Future

### Modelos Mais Avançados
1. **Random Forest**: Melhor para padrões não-lineares
2. **LSTM/GRU**: Redes neurais para séries temporais
3. **ARIMA**: Modelos estatísticos específicos para séries temporais

### Features Adicionais
1. **Volume de negociação**
2. **Indicadores técnicos** (RSI, MACD, Bollinger Bands)
3. **Sentimento de mercado**
4. **Dados fundamentais**

### Validação
1. **Cross-validation temporal**
2. **Backtesting** com dados históricos
3. **Métricas específicas** (MAE, RMSE, MAPE)

## Executando os Exemplos

```bash
# Executa exemplos completos
PYTHONPATH=/home/zambra/git/usage-overarch-halogen poetry run python scripts/predict_example.py

# Ou use a API
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/price/predict
```

## Estrutura dos Dados

### Entrada do Modelo
```json
{
  "price_t-1": 107321.55,
  "price_t-2": 107322.18,
  "price_t-3": 107328.21,
  "price_t-4": 107328.22,
  "price_t-5": 107331.10,
  "ma_10": 107327.36
}
```

### Saída do Modelo
```json
{
  "predicted_price": 107301.53
}
```

O modelo funciona analisando padrões nos preços históricos recentes e na média móvel para estimar o próximo valor do Bitcoin.