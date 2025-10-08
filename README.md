# Bitcoin Price Pipeline & ML Prediction API

Sistema completo de monitoramento, análise e predição de preços do Bitcoin usando Machine Learning. O projeto coleta preços em tempo real, aplica engenharia de features avançada com indicadores técnicos e disponibiliza modelos de ML através de uma API REST.

## Funcionalidades

### Coleta de Dados
- Coleta automática de preços do Bitcoin a cada minuto
- Coleta automática de previsões a cada 60 segundos
- Armazenamento em PostgreSQL
- Histórico completo para análise temporal
- Atualização automática de previsões com valores reais após 15 minutos

### Feature Engineering
- **50+ features técnicas** criadas automaticamente:
  - Indicadores de Momentum (RSI, Stochastic)
  - Indicadores de Tendência (MACD, Médias Móveis)
  - Indicadores de Volatilidade (Bollinger Bands, ATR)
  - Features temporais (hora do dia, dia da semana)
  - Lag features e Rolling statistics

### Modelos de Machine Learning

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

### Dashboard Interativo (Streamlit)
- **Visualização em tempo real** do preço do Bitcoin e previsões
- **Auto-refresh** configurável (padrão 60 segundos)
- **Gráficos interativos** com Plotly:
  - Preço Real vs Previsões
  - Matriz de Confusão
  - Feature Importance
  - Previsto vs Real (scatter plot)
- **Métricas de performance** dos modelos
- **60 previsões recentes** em tabela
- **Análise de acurácia** em tempo real

### MLflow Integration
- Versionamento de modelos
- Tracking de experimentos
- Armazenamento de artefatos (S3-compatible)
- Métricas e parâmetros logados automaticamente

## Estrutura do Projeto

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

## Instalação e Configuração

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
poetry lock & poetry install

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

## Como Usar

### Usando Poetry (Recomendado)

O projeto inclui scripts Poetry para facilitar a execução:



#### 1. Iniciar a API e Coletar Dados
```bash
poetry run python src/main.py
```

#### 2. Treinar Modelos
```bash
# Treinar modelo de predição de preço (utilizar uma das opções)
poetry run python scripts/train_model.py
poetry run train-price-model

# Treinar modelo de classificação de tendência (utilizar uma das opções)
poetry run python scripts/train_trend_model.py
poetry run train-trend-model
```


### Usando Python Diretamente

#### Passo 1: Coletar Dados
Inicie a API para começar a coletar preços:

```bash
python src/main.py
```

A coleta de preços começará automaticamente em background. Aguarde pelo menos **1-2 horas** para acumular dados suficientes para treinar os modelos.

### Passo 2: Treinar Modelo de Predição de Preço

Utilize uma das opções a seguir:
```bash
python scripts/train_model.py
```

### Passo 3: Treinar Modelo de Classificação de Tendência
Utilize uma das opções a seguir:
```bash
python scripts/train_trend_model.py
```

### Passo 4: Executar o Dashboard Streamlit

Após treinar os modelos e com a API rodando, execute o dashboard:

```bash
# Com Poetry (Recomendado)
poetry run streamlit run dashboard/app.py

# Ou com Streamlit diretamente
streamlit run dashboard/app.py
```

O dashboard estará disponível em: **http://localhost:8501**

**Funcionalidades do Dashboard:**
- **Métricas em Tempo Real**: Preço atual, previsão 15min, tendência e probabilidades
- **Gráfico Previsto vs Real**: Visualização completa com linha de preço real, pontos de previsão e margem de erro (MAE)
- **Análise de Performance**: 
  - Modelo de Preço: MAE, MAPE, RMSE e gráfico de dispersão
  - Modelo de Tendência: Acurácia, Precision, Recall, F1-Score e Matriz de Confusão
- **Feature Importance**: Top 15 features mais importantes para o modelo de tendência
- **Previsões Recentes**: Tabela com 60 últimas previsões comparadas com valores reais
- **Auto-refresh**: Atualização automática a cada 60 segundos (configurável)
- **Timezone Brasília/São Paulo**: Todos os timestamps em UTC-3

**Configurações do Dashboard:**
- Intervalo de atualização: 10-300 segundos (padrão: 60s)
- Período de análise: 1h, 6h, 24h, 7d (padrão: 24h)

## Endpoints da API

### Informações Gerais

Entre em http://localhost:8000/docs para Swagger UI

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
poetry run python scripts/train_model.py
poetry run train-price-model

# Retreinar modelo de tendência
poetry run python scripts/train_trend_model.py
poetry run train-trend-model
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
- **Solução**: Treine os modelos primeiro com `poetry run train-trend-model` e/ou `poetry run train-price-model`

### Erro: "Database connection failed"
- **Solução**: Verifique se o PostgreSQL está rodando (`docker-compose ps`)

### Modelo com baixa acurácia
- **Solução**: Colete mais dados, ajuste hiperparâmetros, verifique qualidade dos dados
