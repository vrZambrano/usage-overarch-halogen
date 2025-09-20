# Guia de Feature Engineering para Bitcoin

Este documento descreve a implementação completa do sistema de feature engineering para dados de preço do Bitcoin, seguindo as técnicas avançadas de machine learning para séries temporais financeiras.

## Visão Geral

O sistema transforma dados simples de preço do Bitcoin em um conjunto rico de features para machine learning, incluindo:

- **Features Temporais**: Padrões baseados em tempo
- **Features de Lag**: Valores históricos
- **Features Rolling**: Estatísticas de janelas deslizantes
- **Indicadores Técnicos**: RSI, MACD, Bollinger Bands, ATR, Stochastic
- **Features de Volatilidade**: Mudanças e volatilidade
- **Features de Momentum**: Indicadores de momentum
- **Features Normalizadas**: Dados preparados para ML

## Arquitetura

### Componentes Principais

1. **ModelDBBitcoinFeatures** (`models/database.py`)
   - Nova tabela com prefixo `modeldb_`
   - 50+ campos de features enriquecidas
   - Otimizada para machine learning

2. **BitcoinFeatureEngineer** (`services/feature_engineer.py`)
   - Engine principal de feature engineering
   - Implementa todos os indicadores técnicos
   - Pipeline completo de transformação

3. **DataEnricher** (`services/data_enricher.py`)
   - Processa dados históricos e em tempo real
   - Gerencia salvamento na nova tabela
   - Integração com o sistema existente

4. **Scripts de Utilidade**
   - `scripts/enrich_historical_data.py`: Processa dados históricos
   - `scripts/test_feature_engineering.py`: Testes e validação

## Features Implementadas

### 1. Features Temporais
```python
- minute_of_hour (0-59)
- hour_of_day (0-23)
- day_of_week (0-6)
- week_of_year (1-53)
```

### 2. Features de Lag (Atraso)
```python
- price_lag_1min
- price_lag_5min
- price_lag_15min
- price_lag_30min
- price_lag_60min
```

### 3. Features Rolling (Janelas Deslizantes)
```python
# Médias móveis
- rolling_mean_5min
- rolling_mean_15min
- rolling_mean_30min
- rolling_mean_60min

# Desvios padrão
- rolling_std_5min
- rolling_std_15min
- rolling_std_30min
- rolling_std_60min

# Min/Max
- rolling_min_30min
- rolling_max_30min
```

### 4. Indicadores Técnicos

#### RSI (Relative Strength Index)
```python
- rsi_14: Índice de força relativa (14 períodos)
```

#### MACD (Moving Average Convergence Divergence)
```python
- macd_line: Linha MACD
- macd_signal: Linha de sinal
- macd_histogram: Histograma MACD
```

#### Bollinger Bands
```python
- bb_upper: Banda superior
- bb_middle: Média móvel central
- bb_lower: Banda inferior
- bb_width: Largura das bandas
- bb_position: Posição do preço nas bandas (0-1)
```

#### ATR (Average True Range)
```python
- atr_14: Volatilidade média (14 períodos)
```

#### Stochastic Oscillator
```python
- stoch_k: %K estocástico
- stoch_d: %D estocástico
```

### 5. Features de Volatilidade
```python
# Mudanças absolutas
- price_change_1min
- price_change_5min
- price_change_15min

# Mudanças percentuais
- price_change_pct_1min
- price_change_pct_5min
- price_change_pct_15min

# Volatilidade
- volatility_30min
```

### 6. Features de Momentum
```python
- momentum_5min
- momentum_15min
- momentum_30min
```

### 7. Features Normalizadas
```python
- price_normalized: Preço normalizado (MinMaxScaler)
- volume_normalized: Volume normalizado (futuro uso)
```

## Como Usar

### 1. Processar Dados Históricos

```bash
# Processar todos os dados históricos
cd usage-overarch-halogen
python scripts/enrich_historical_data.py

# Processar apenas 1000 registros
python scripts/enrich_historical_data.py --limit 1000

# Usar lotes menores (500 registros por vez)
python scripts/enrich_historical_data.py --batch-size 500

# Apenas mostrar estatísticas
python scripts/enrich_historical_data.py --stats-only
```

### 2. Testar a Implementação

```bash
# Executar testes completos
python scripts/test_feature_engineering.py
```

### 3. Usar em Código Python

```python
from services.feature_engineer import BitcoinFeatureEngineer
from services.data_enricher import DataEnricher

# Feature engineering básico
engineer = BitcoinFeatureEngineer()
enriched_df = engineer.engineer_all_features(df)

# Enriquecimento completo com salvamento
enricher = DataEnricher()
success = enricher.enrich_historical_data()

# Enriquecer registro único
enriched_record = enricher.enrich_single_record(
    price=50000.0,
    timestamp=datetime.now(),
    source="binance"
)
```

### 4. Integração com Price Collector

O sistema está automaticamente integrado com o coletor de preços:

```python
# O collector agora salva dados enriquecidos automaticamente
from services.price_collector import BitcoinPriceCollector

# Com enriquecimento (padrão)
collector = BitcoinPriceCollector(enable_enrichment=True)

# Sem enriquecimento
collector = BitcoinPriceCollector(enable_enrichment=False)
```

## Estrutura da Base de Dados

### Tabela Original: `bitcoin_prices`
```sql
- id (Primary Key)
- price (Numeric)
- timestamp (DateTime)
- source (String)
- created_at (DateTime)
```

### Nova Tabela: `modeldb_bitcoin_features`
```sql
- id (Primary Key)
- price (Numeric)
- timestamp (DateTime)
- source (String)

-- Features temporais (4 campos)
- minute_of_hour, hour_of_day, day_of_week, week_of_year

-- Features de lag (5 campos)
- price_lag_1min, price_lag_5min, price_lag_15min, price_lag_30min, price_lag_60min

-- Features rolling (10 campos)
- rolling_mean_*, rolling_std_*, rolling_min_30min, rolling_max_30min

-- Indicadores técnicos (13 campos)
- rsi_14, macd_*, bb_*, atr_14, stoch_*

-- Features de volatilidade (7 campos)
- price_change_*, price_change_pct_*, volatility_30min

-- Features de momentum (3 campos)
- momentum_5min, momentum_15min, momentum_30min

-- Features normalizadas (2 campos)
- price_normalized, volume_normalized

- created_at (DateTime)
```

**Total: 50+ features para machine learning**

## Benefícios para Machine Learning

### 1. Contexto Temporal Rico
- Captura padrões intradiários e semanais
- Informações sobre tendências de curto e longo prazo

### 2. Indicadores Técnicos Profissionais
- RSI para condições de sobrecompra/sobrevenda
- MACD para mudanças de momentum
- Bollinger Bands para volatilidade e posicionamento
- ATR para medição de volatilidade
- Stochastic para momentum

### 3. Features de Volatilidade
- Mudanças absolutas e percentuais
- Medidas de volatilidade rolling

### 4. Dados Normalizados
- Prontos para algoritmos de ML
- Escalas consistentes

### 5. Tratamento de Dados Faltantes
- Estratégias robustas para NaN
- Forward fill e interpolação quando apropriado

## Performance e Otimização

### Processamento em Lotes
- Inserção otimizada em lotes de 1000 registros
- Reduz overhead de transações de banco

### Caching Inteligente
- MinMaxScaler reutilizado para normalização
- Cálculos otimizados para janelas rolling

### Tratamento de Erros
- Enriquecimento em tempo real não bloqueia coleta básica
- Logs detalhados para debugging

## Monitoramento e Logs

### Logs Detalhados
```
2025-01-19 23:00:00 INFO: Iniciando feature engineering...
2025-01-19 23:00:01 INFO: Features temporais criadas
2025-01-19 23:00:02 INFO: Features de lag criadas
2025-01-19 23:00:03 INFO: Features rolling criadas
2025-01-19 23:00:04 INFO: Indicadores técnicos criados
2025-01-19 23:00:05 INFO: Features de volatilidade criadas
2025-01-19 23:00:06 INFO: Features de momentum criadas
2025-01-19 23:00:07 INFO: Features normalizadas
2025-01-19 23:00:08 INFO: Feature engineering concluído. Shape final: (1000, 52)
```

### Estatísticas
```python
stats = enricher.get_enriched_data_stats()
# {
#     'total_records': 1000,
#     'oldest_record': '2025-01-19 22:00:00',
#     'newest_record': '2025-01-19 23:00:00',
#     'total_features': 47
# }
```

## Próximos Passos

### 1. Expansão de Features
- Volume de negociação (quando disponível)
- Features de correlação com outros ativos
- Indicadores de sentimento de mercado

### 2. Otimizações
- Processamento paralelo para grandes volumes
- Cache distribuído para features computacionalmente caras

### 3. Integração com ML
- Pipeline automático para treinamento de modelos
- Feature selection automática
- Validação cruzada temporal

## Troubleshooting

### Problemas Comuns

1. **Erro de dependências**
   ```bash
   # Instalar dependências
   cd usage-overarch-halogen
   poetry install
   ```

2. **Tabela não existe**
   ```bash
   # Recriar tabelas
   python -c "from src.core.database import engine; from src.models.database import Base; Base.metadata.create_all(bind=engine)"
   ```

3. **Dados insuficientes para features**
   - Features de lag precisam de histórico mínimo
   - Indicadores técnicos precisam de pelo menos 26 períodos para MACD

4. **Performance lenta**
   - Usar batch_size menor
   - Processar em horários de menor carga
   - Verificar índices no banco de dados

### Logs de Debug
```bash
# Habilitar logs detalhados
export PYTHONPATH="${PYTHONPATH}:./src"
python scripts/enrich_historical_data.py --limit 100
```

## Conclusão

Este sistema de feature engineering transforma dados simples de preço do Bitcoin em um dataset rico e multidimensional, pronto para alimentar modelos de machine learning sofisticados. A implementação segue as melhores práticas da indústria e está otimizada para performance e escalabilidade.

A base `modeldb_bitcoin_features` agora contém todas as informações necessárias para treinar modelos preditivos avançados, capturando a dinâmica complexa do mercado de Bitcoin através de 50+ features cuidadosamente engineered.
