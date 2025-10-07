# 🚀 Guia de Início Rápido - Dashboard de Previsões Bitcoin

Este guia mostra como colocar todo o sistema de previsões funcionando do zero.

## 📋 Pré-requisitos

- Python 3.9+
- PostgreSQL instalado e rodando
- Docker (opcional, para PostgreSQL)

## ⚙️ Configuração Inicial

### 1. Configurar Banco de Dados

```bash
# Opção 1: Usar Docker Compose (recomendado)
cd usage-overarch-halogen/docker
docker-compose up -d

# Opção 2: PostgreSQL local
# Criar banco de dados manualmente
createdb bitcoin_db
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env
```

Configurações mínimas no `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bitcoin_db
MLFLOW_TRACKING_URI=http://localhost:5001
```

### 3. Instalar Dependências

```bash
# Instalar dependências com Poetry
poetry install

# Ou atualizar dependências
poetry update
```

## 🎯 Fluxo de Execução Completo

### Passo 1: Treinar os Modelos

**IMPORTANTE**: Os modelos precisam ser treinados ANTES de iniciar a API.

```bash
# Opção 1: Usando Poetry (recomendado)
poetry run train-price-model
poetry run train-trend-model

# Opção 2: Usando Python diretamente
poetry run python scripts/train_model.py
poetry run python scripts/train_trend_model.py
```

**Aguarde**: Esses scripts podem levar alguns minutos. Eles vão:
- Buscar dados históricos do banco
- Aplicar engenharia de features
- Treinar modelos XGBoost
- Salvar modelos no MLflow

### Passo 2: Iniciar a API

```bash
# Opção 1: Usando Poetry (recomendado)
poetry run start-api

# Opção 2: Usando uvicorn diretamente com Poetry
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Opção 3: Ativando ambiente virtual primeiro
poetry shell
python src/main.py
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

**Verificar Status**:
```bash
curl http://localhost:8000/health
```

### Passo 3: Aguardar Coleta de Dados

Após iniciar a API, dois coletores começam automaticamente:

1. **Price Collector**: Coleta preços a cada minuto
2. **Prediction Collector**: Gera previsões a cada minuto

**Aguarde pelo menos 20 minutos** para:
- ✅ Coletar dados suficientes para previsões
- ✅ Ter previsões verificadas (após 15 min)
- ✅ Calcular métricas de acurácia

### Passo 4: Iniciar o Dashboard

```bash
# Opção 1: Usando Poetry (recomendado)
poetry run streamlit run dashboard/app.py

# Opção 2: Dentro do ambiente virtual Poetry
poetry shell
streamlit run dashboard/app.py
```

O dashboard estará disponível em: http://localhost:8501

## 📊 O Que Esperar

### Primeiros 5 minutos
- ✅ Preços sendo coletados
- ✅ Previsões sendo geradas
- ⏳ Gráficos com poucos dados
- ⏳ Métricas ainda não disponíveis

### Após 15-20 minutos
- ✅ Gráfico de preço vs previsto populado
- ✅ Primeiras previsões verificadas
- ✅ Métricas de acurácia disponíveis
- ✅ Todos os gráficos funcionando

### Após 1 hora
- ✅ Dados suficientes para análise robusta
- ✅ Gráficos de tendência claros
- ✅ Métricas estáveis

## 🔍 Endpoints Principais da API

### Preços
```bash
# Último preço
curl http://localhost:8000/price/latest

# Histórico (últimas 24h)
curl http://localhost:8000/price/history?hours=24
```

### Previsões em Tempo Real
```bash
# Previsão de preço
curl http://localhost:8000/price/predict/next

# Previsão de tendência
curl http://localhost:8000/trend/predict

# Feature importance
curl http://localhost:8000/trend/feature-importance
```

### Previsões Armazenadas
```bash
# Histórico de previsões
curl http://localhost:8000/predictions/history?hours=24

# Métricas de acurácia
curl http://localhost:8000/predictions/accuracy?hours=24

# Últimas previsões
curl http://localhost:8000/predictions/latest?limit=20
```

## 🛠️ Manutenção

### Limpeza de Dados Antigos

```bash
# Opção 1: Usando Poetry (recomendado)
poetry run cleanup-predictions

# Opção 2: Com argumentos customizados
poetry run python scripts/cleanup_old_predictions.py --days 60

# Opção 3: Dentro do ambiente virtual
poetry shell
python scripts/cleanup_old_predictions.py --days 60
```

### Retreinar Modelos

Recomenda-se retreinar os modelos periodicamente:

```bash
# Parar a API
# Ctrl+C no terminal da API

# Retreinar modelos com Poetry
poetry run train-price-model
poetry run train-trend-model

# Reiniciar a API
poetry run start-api
```

## 🐛 Troubleshooting

### Erro: "No MLflow runs found"

**Problema**: Modelos não foram treinados.

**Solução**:
```bash
poetry run train-price-model
poetry run train-trend-model
```

### Erro: "Insufficient data available for training"

**Problema**: Não há dados suficientes no banco.

**Solução**: Aguarde alguns minutos para o price_collector coletar dados.

### Dashboard não mostra dados

**Problema**: API não está rodando ou modelos não treinados.

**Verificações**:
1. API rodando: `curl http://localhost:8000/health`
2. Modelos treinados: Verificar logs do treinamento
3. Dados no banco: `curl http://localhost:8000/price/latest`

### Previsões não são verificadas

**Problema**: Previsões recentes ainda não têm valores reais.

**Solução**: Aguarde 15 minutos após as previsões serem feitas.

## 📈 Configurações do Dashboard

### No Sidebar (barra lateral):

- **Intervalo de atualização**: 10-300 segundos (padrão: 60s)
- **Período de análise**: 1h, 6h, 24h, 7d (padrão: 24h)

### Recomendações:

- **Testes/Debug**: Intervalo de 10s, período de 1h
- **Produção**: Intervalo de 60s, período de 24h
- **Análise Longa**: Período de 7d

## 🔄 Fluxo de Dados Completo

```
1. Binance API
   ↓ (a cada minuto)
2. Price Collector → PostgreSQL (bitcoin_prices)
   ↓
3. Feature Engineering
   ↓
4. Modelos ML (XGBoost)
   ↓ (previsões)
5. Prediction Collector → PostgreSQL (bitcoin_predictions)
   ↓ (após 15 min)
6. Atualização com valores reais
   ↓
7. Dashboard Streamlit (visualização)
```

## 📊 Estrutura do Banco de Dados

### Tabelas Criadas Automaticamente:

1. **bitcoin_prices**: Preços coletados a cada minuto
2. **bitcoin_predictions**: Previsões e comparações com valores reais
3. **modeldb_bitcoin_features**: Features de engenharia (opcional)

### Verificar Dados:

```sql
-- Contagem de preços
SELECT COUNT(*) FROM bitcoin_prices;

-- Contagem de previsões
SELECT COUNT(*) FROM bitcoin_predictions;

-- Últimas previsões verificadas
SELECT * FROM bitcoin_predictions 
WHERE actual_price IS NOT NULL 
ORDER BY timestamp DESC 
LIMIT 10;
```

## 🎓 Próximos Passos

1. **Explorar API**: http://localhost:8000/docs
2. **Analisar Dashboard**: http://localhost:8501
3. **Monitorar Logs**: Ver saída dos terminais
4. **Ajustar Modelos**: Modificar hiperparâmetros nos scripts de treino
5. **Customizar Dashboard**: Editar `dashboard/app.py`

## 💡 Dicas

- Mantenha a API rodando continuamente para coleta de dados
- Retreine modelos semanalmente para melhor performance
- Use o endpoint `/health` para monitoramento
- Configure um cron job para limpeza automática de dados antigos

## 📞 Suporte

Consulte a documentação completa:
- **Dashboard**: `dashboard/README.md`
- **Modelos**: `docs/prediction_guide.md`
- **Features**: `docs/feature_engineering_guide.md`
- **Projeto Principal**: `README.md`

---

**Última Atualização**: Janeiro 2025
