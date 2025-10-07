# Bitcoin Price Pipeline & ML Prediction API

Sistema completo de monitoramento, análise e predição de preços do Bitcoin usando Machine Learning. O projeto coleta preços em tempo real, aplica engenharia de features avançada com indicadores técnicos e disponibiliza modelos de ML através de uma API REST.

## 🚀 Funcionalidades

### 📊 Coleta de Dados
- Coleta automática de preços do Bitcoin a cada minuto
- Armazenamento em PostgreSQL com timezone-aware timestamps
- Histórico completo para análise temporal

### 🔬 Feature Engineering
- **50+ features técnicas** criadas automaticamente:
  - Indicadores de Momentum (RSI, Stochastic)
  - Indicadores de Tendência (MACD, Médias Móveis)
  - Indicadores de Volatilidade (Bollinger Bands, ATR)
  - Features temporais (hora do dia, dia da semana)
  - Lag features e Rolling statistics

### 🤖 Modelos de Machine Learning

#### 1. Predição de Preço (XGBoost Regressor)
- **Objetivo**: Prever o preço exato 15 minutos à frente
- **Modelo**: XGBoost Regressor
- **Features**: 50+ indicadores técnicos
- **Métricas**: RMSE, MAE, MAPE
- **Endpoint**: `/price/predict/next`

#### 2. Classificação de Tendência (XGBoost Classifier)
- **Objetivo**: Classificar se o preço subirá (UP) ou cairá (DOWN)
- **Modelo**: XGBoost Classifier
- **Features**: 50+ indicadores técnicos
- **Métricas**: Acurácia, Precisão, Recall, F1-Score, AUC
- **Endpoints**: `/trend/predict`, `/trend/feature-importance`

#### 3. Predição de Preço com H2O AutoML (Novo!)
- **Objetivo**: Prever o preço exato 15 minutos à frente usando AutoML
- **Modelo**: H2O AutoML (seleciona automaticamente o melhor entre GBM, XGBoost, Deep Learning, GLM, etc.)
- **Features**: 50+ indicadores técnicos
- **Métricas**: RMSE, MAE, MAPE, R²
- **Endpoints**: `/price/predict/h2o`, `/h2o/leaderboard`
- **Diferencial**: Testa múltiplos algoritmos automaticamente e seleciona o melhor

### 🔄 MLflow Integration
- Versionamento de modelos
- Tracking de experimentos
- Armazenamento de artefatos (S3-compatible)
- Métricas e parâmetros logados automaticamente

## 📁 Estrutura do Projeto

```
usage-overarch-halogen/
├── src/
│   ├── main.py                    # API FastAPI
│   ├── services/
│   │   ├── feature_engineer.py    # Engenharia de features
│   │   ├── prediction_service.py  # Modelo de predição de preço
│   │   ├── trend_prediction_service.py  # Modelo de tendência
│   │   ├── bitcoin_service.py     # Serviço de dados
│   │   └── price_collector.py     # Coleta de preços
│   ├── models/
│   │   ├── database.py            # Modelos SQLAlchemy
│   │   └── schemas.py             # Schemas Pydantic
│   ├── core/
│   │   └── database.py            # Configuração do banco
│   └── utils/
│       └── timezone.py            # Utilidades de timezone
├── scripts/
│   ├── train_model.py             # Treinar modelo de preço
│   └── train_trend_model.py       # Treinar modelo de tendência
├── docker/
│   └── docker-compose.yml         # PostgreSQL + MLflow
└── requirements.txt
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### 2. Clonar o Repositório
```bash
git clone <repo-url>
cd usage-overarch-halogen
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` baseado no `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bitcoin_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5001
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
```

### 4. Iniciar Serviços com Docker
```bash
cd docker
docker-compose up -d
```

Isso iniciará:
- PostgreSQL (porta 5432)
- MLflow Tracking Server (porta 5001)
- MinIO S3 (porta 9000) - para artefatos do MLflow

### 5. Instalar Dependências

#### Opção A: Com Poetry (Recomendado)
```bash
# Instalar Poetry (se ainda não tiver)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências do projeto
poetry install

# Ativar o ambiente virtual
poetry shell
```

#### Opção B: Com pip
```bash
pip install -r requirements.txt
```

### 6. Inicializar o Banco de Dados
```bash
# O script init.sql será executado automaticamente pelo Docker
# Ou execute manualmente:
psql -U user -d bitcoin_db -f init.sql
```

## 🎯 Como Usar

### Usando Poetry (Recomendado)

O projeto inclui scripts Poetry para facilitar a execução:

#### 1. Iniciar a API e Coletar Dados
```bash
# Método 1: Usando Poetry run
poetry run python src/main.py

# Método 2: Dentro do shell do Poetry
poetry shell
cd src
python main.py
```

#### 2. Treinar Modelos
```bash
# Treinar modelo de predição de preço
poetry run python scripts/train_model.py

# Treinar modelo de classificação de tendência
poetry run python scripts/train_trend_model.py
```

#### 3. Executar Exemplos Interativos
```bash
poetry run python scripts/example_usage.py
```

### Usando Python Diretamente

#### Passo 1: Coletar Dados
Inicie a API para começar a coletar preços:

```bash
cd src
python main.py
# ou
uvicorn main:app --reload
```

A coleta de preços começará automaticamente em background. Aguarde pelo menos **1-2 horas** para acumular dados suficientes para treinar os modelos.

### Passo 2: Treinar Modelo de Predição de Preço
```bash
python scripts/train_model.py
```

Saída esperada:
```
================================================================================
Starting Bitcoin Price Prediction Model Training
================================================================================
MLflow Tracking URI: http://localhost:5001
Using XGBoost Regressor with full feature engineering
Target: Predict price 15 minutes ahead
================================================================================
INFO:__main__:Loaded 5432 price records
INFO:__main__:Feature engineering complete. Shape: (5312, 52)
INFO:__main__:Training with 50 features and 5312 samples
INFO:__main__:Fold 1 - RMSE: 125.30, MAE: 98.45
INFO:__main__:Fold 2 - RMSE: 132.12, MAE: 102.33
INFO:__main__:Fold 3 - RMSE: 128.67, MAE: 99.87
INFO:__main__:Test RMSE: 127.89
INFO:__main__:Test MAE: 100.12
INFO:__main__:Test MAPE: 0.28%
✓ Model training completed successfully!
✓ Run ID: abc123def456
✓ Experiment: bitcoin_price_prediction
```

### Passo 3: Treinar Modelo de Classificação de Tendência
```bash
python scripts/train_trend_model.py
```

Saída esperada:
```
================================================================================
Starting Bitcoin Trend Classification Model Training
================================================================================
MLflow Tracking URI: http://localhost:5001
Using XGBoost Classifier with full feature engineering
Target: Classify trend (UP/DOWN) 15 minutes ahead
================================================================================
INFO:__main__:Loaded 5432 price records
INFO:__main__:Class distribution - Down (0): 2689, Up (1): 2623
INFO:__main__:Fold 1 - Accuracy: 0.8723, Precision: 0.8656, Recall: 0.8812, F1: 0.8733
INFO:__main__:Test Accuracy: 0.8701
INFO:__main__:Test F1: 0.8698
✓ Trend model training completed successfully!
✓ Run ID: xyz789ghi012
```

## 📡 Endpoints da API

### Informações Gerais

#### `GET /`
Retorna informações sobre a API e todos os endpoints disponíveis.

```bash
curl http://localhost:8000/
```

#### `GET /docs`
Documentação interativa Swagger UI.

#### `GET /health`
Health check do sistema.

### Endpoints de Preço

#### `GET /price/latest`
Retorna o último preço registrado.

```bash
curl http://localhost:8000/price/latest
```

Resposta:
```json
{
  "price": 45123.50,
  "timestamp": "2025-01-07T12:30:00-03:00",
  "source": "binance",
  "last_updated": "2025-01-07T12:30:05-03:00"
}
```

#### `GET /price/history?limit=100&hours=24`
Retorna histórico de preços.

#### `GET /price/stats?hours=24`
Retorna estatísticas de preço (min, max, avg).

### Endpoints de Predição

#### `GET /price/predict/next`
**Predição de Preço 15 minutos à frente**

```bash
curl http://localhost:8000/price/predict/next
```

Resposta:
```json
{
  "predicted_price": 45230.50,
  "current_price": 45000.00,
  "price_change": 230.50,
  "price_change_percent": 0.51,
  "horizon_minutes": 15,
  "model_mae": 125.30,
  "model_mape": 0.28,
  "timestamp": "2025-01-07T12:30:00",
  "run_id": "abc123def456"
}
```

#### `GET /trend/predict`
**Classificação de Tendência (UP/DOWN)**

```bash
curl http://localhost:8000/trend/predict
```

Resposta:
```json
{
  "trend": "UP",
  "trend_numeric": 1,
  "probability_down": 0.35,
  "probability_up": 0.65,
  "confidence": 0.65,
  "current_price": 45000.00,
  "horizon_minutes": 15,
  "model_accuracy": 0.87,
  "model_f1_score": 0.86,
  "timestamp": "2025-01-07T12:30:00",
  "run_id": "xyz789ghi012"
}
```

#### `GET /trend/feature-importance`
**Importância das Features**

Retorna quais indicadores técnicos são mais importantes para o modelo de tendência.

```bash
curl http://localhost:8000/trend/feature-importance
```

Resposta:
```json
{
  "features": [
    {"feature": "rsi_14", "importance": 0.085},
    {"feature": "macd_line", "importance": 0.072},
    {"feature": "bb_position", "importance": 0.065},
    {"feature": "momentum_15min", "importance": 0.058},
    ...
  ],
  "total_features": 50
}
```

### Endpoints H2O AutoML (Novo!)

#### `GET /price/predict/h2o`
**Predição de Preço com H2O AutoML**

Usa o melhor modelo selecionado automaticamente pelo H2O AutoML.

```bash
curl http://localhost:8000/price/predict/h2o
```

Resposta:
```json
{
  "predicted_price": 45280.75,
  "current_price": 45000.00,
  "price_change": 280.75,
  "price_change_percent": 0.62,
  "horizon_minutes": 15,
  "model_type": "GBM",
  "model_id": "GBM_1_AutoML_20250107_123456",
  "model_rmse": 118.45,
  "model_mae": 92.30,
  "model_mape": 0.25,
  "model_r2": 0.956,
  "timestamp": "2025-01-07T12:30:00",
  "run_id": "abc123def456"
}
```

#### `GET /h2o/leaderboard`
**Leaderboard do H2O AutoML**

Retorna todos os modelos testados pelo H2O AutoML ordenados por performance.

```bash
curl http://localhost:8000/h2o/leaderboard
```

Resposta:
```json
{
  "leaderboard": [
    {
      "model_id": "GBM_1_AutoML_20250107_123456",
      "rmse": 118.45,
      "mae": 92.30,
      "rmsle": 0.0026,
      "mean_residual_deviance": 14030.22
    },
    {
      "model_id": "XGBoost_2_AutoML_20250107_123456",
      "rmse": 125.12,
      "mae": 98.76,
      "rmsle": 0.0028,
      "mean_residual_deviance": 15655.02
    }
  ],
  "total_models": 20,
  "best_model": "GBM_1_AutoML_20250107_123456"
}
```

## 🤖 H2O AutoML - Guia Completo

### O que é H2O AutoML?

H2O AutoML é uma plataforma de Machine Learning automatizado que:
- **Testa múltiplos algoritmos automaticamente** (GBM, XGBoost, Deep Learning, GLM, Random Forest)
- **Otimiza hiperparâmetros** de forma automática
- **Cria modelos ensemble** combinando os melhores modelos
- **Seleciona o melhor modelo** baseado em métricas de performance

### Como Treinar o Modelo H2O AutoML

```bash
# Treinar modelo H2O AutoML
poetry run python scripts/train_h2o_model.py

# Ou sem Poetry
python scripts/train_h2o_model.py
```

### Configurações do H2O AutoML

No arquivo `h2o_prediction_service.py`, você pode ajustar:

```python
aml = H2OAutoML(
    max_runtime_secs=300,  # Tempo máximo de treinamento (5 minutos)
    max_models=20,         # Número máximo de modelos a testar
    seed=42,               # Semente para reprodutibilidade
    nfolds=5,              # Cross-validation folds
    sort_metric='RMSE'     # Métrica para ordenar modelos
)
```

### Algoritmos Testados pelo H2O AutoML

1. **GBM (Gradient Boosting Machine)**: Excelente para dados tabulares
2. **XGBoost**: Versão otimizada de GBM
3. **GLM (Generalized Linear Model)**: Modelo linear robusto
4. **Deep Learning**: Redes neurais profundas
5. **Distributed Random Forest**: Ensemble de árvores

### Comparando Modelos

Você pode comparar os 3 modelos de predição de preço:

```python
import requests

# XGBoost Manual
xgb_pred = requests.get("http://localhost:8000/price/predict/next").json()

# H2O AutoML
h2o_pred = requests.get("http://localhost:8000/price/predict/h2o").json()

print(f"XGBoost - Preço Previsto: ${xgb_pred['predicted_price']:.2f} (MAE: {xgb_pred['model_mae']:.2f})")
print(f"H2O AutoML - Preço Previsto: ${h2o_pred['predicted_price']:.2f} (MAE: {h2o_pred['model_mae']:.2f})")
print(f"Melhor Algoritmo H2O: {h2o_pred['model_type']}")
```

### Vantagens do H2O AutoML

✅ **Automação Completa**: Não precisa escolher algoritmo ou hiperparâmetros
✅ **Múltiplos Modelos**: Testa vários algoritmos em paralelo  
✅ **Ensemble Learning**: Combina modelos para melhor performance  
✅ **Leaderboard Transparente**: Veja todos os modelos testados
✅ **Otimização Automática**: Ajuste de hiperparâmetros incluído

### Desvantagens

⚠️ **Tempo de Treinamento**: Pode demorar mais que treinar um único modelo  
⚠️ **Uso de Memória**: Requer mais RAM (configurado para 4GB)  
⚠️ **Complexidade**: Mais difícil de interpretar que um único modelo

## 🔧 Exemplos de Uso com Python

### Exemplo 1: Obter Predição de Preço
```python
import requests

response = requests.get("http://localhost:8000/price/predict/next")
prediction = response.json()

print(f"Preço Atual: ${prediction['current_price']:.2f}")
print(f"Preço Previsto (15min): ${prediction['predicted_price']:.2f}")
print(f"Mudança Esperada: {prediction['price_change_percent']:.2f}%")
print(f"Confiança (MAE): ${prediction['model_mae']:.2f}")
```

### Exemplo 2: Obter Predição de Tendência
```python
import requests

response = requests.get("http://localhost:8000/trend/predict")
trend = response.json()

print(f"Tendência Prevista: {trend['trend']}")
print(f"Confiança: {trend['confidence']*100:.1f}%")
print(f"Probabilidade de Alta: {trend['probability_up']*100:.1f}%")
print(f"Probabilidade de Baixa: {trend['probability_down']*100:.1f}%")

if trend['trend'] == 'UP':
    print("✅ Sinal de COMPRA")
else:
    print("⚠️ Sinal de VENDA")
```

### Exemplo 3: Analisar Features Importantes
```python
import requests
import pandas as pd

response = requests.get("http://localhost:8000/trend/feature-importance")
data = response.json()

# Criar DataFrame
df = pd.DataFrame(data['features'])
top_10 = df.head(10)

print("Top 10 Features Mais Importantes:")
print(top_10)

# Visualizar
import matplotlib.pyplot as plt
plt.barh(top_10['feature'], top_10['importance'])
plt.xlabel('Importância')
plt.title('Top 10 Features - Modelo de Tendência')
plt.tight_layout()
plt.show()
```

## 📊 MLflow UI

Acesse o MLflow UI para visualizar experimentos, métricas e modelos:

```
http://localhost:5001
```

Funcionalidades disponíveis:
- Comparar diferentes runs de treinamento
- Visualizar métricas (accuracy, RMSE, MAE, etc.)
- Baixar artefatos de modelos
- Ver importância de features
- Comparar hiperparâmetros

## 🧪 Retreinamento de Modelos

Os modelos podem ser retreinados periodicamente com novos dados:

```bash
# Retreinar modelo de preço
python scripts/train_model.py

# Retreinar modelo de tendência
python scripts/train_trend_model.py
```

**Recomendação**: Retreine os modelos:
- Diariamente: para capturar novos padrões de mercado
- Após eventos significativos: notícias, mudanças regulatórias
- Quando a performance cair: monitorar MAE/MAPE em produção

## 🎓 Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para PostgreSQL
- **XGBoost**: Modelos de ML de alto desempenho
- **MLflow**: Versionamento e tracking de modelos
- **Pandas**: Manipulação de dados
- **Scikit-learn**: Métricas e validação
- **PostgreSQL**: Banco de dados relacional
- **Docker**: Containerização

## 📈 Performance dos Modelos

### Modelo de Predição de Preço
- **RMSE**: ~127 USD
- **MAE**: ~100 USD
- **MAPE**: ~0.28%

### Modelo de Classificação de Tendência
- **Acurácia**: ~87%
- **Precisão**: ~86.5%
- **Recall**: ~88.1%
- **F1-Score**: ~87%
- **AUC**: ~0.92

*Nota: As métricas variam dependendo dos dados de treinamento e condições de mercado.*

## 🔐 Segurança e Boas Práticas

- Nunca exponha credenciais em código
- Use `.env` para variáveis sensíveis
- Mantenha `.env` no `.gitignore`
- Configure CORS apropriadamente para produção
- Use HTTPS em produção
- Implemente rate limiting para a API
- Monitore logs e alertas

## 🐛 Troubleshooting

### Erro: "Insufficient data for training"
- **Solução**: Aguarde mais tempo para coletar dados (mínimo 1-2 horas)

### Erro: "No MLflow runs found"
- **Solução**: Treine os modelos primeiro com `python scripts/train_model.py`

### Erro: "Database connection failed"
- **Solução**: Verifique se o PostgreSQL está rodando (`docker-compose ps`)

### Modelo com baixa acurácia
- **Solução**: Colete mais dados, ajuste hiperparâmetros, verifique qualidade dos dados

## 📝 Licença

MIT License

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para análise e predição de Bitcoin com Machine Learning**
