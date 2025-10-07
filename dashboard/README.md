# Bitcoin Price Prediction Dashboard

Dashboard interativo em Streamlit para visualização de previsões de preço e tendência do Bitcoin usando modelos de Machine Learning.

## 🎯 Funcionalidades

### 1. Métricas em Tempo Real
- **Preço Atual**: Último preço do Bitcoin coletado
- **Previsão de Preço**: Previsão para 15 minutos à frente
- **Tendência Prevista**: Direção do movimento (UP/DOWN) com nível de confiança
- **Probabilidades**: Probabilidades de tendência de alta e baixa

### 2. Gráfico Principal: Previsto vs Real
- Linha temporal do preço real do Bitcoin
- Pontos de previsões realizadas
- Comparação visual entre valores previstos e reais
- Área sombreada indicando margem de erro (±MAE)
- Períodos configuráveis: 1h, 6h, 24h, 7 dias

### 3. Análise de Performance dos Modelos

#### Modelo de Preço (XGBoost Regressor)
- **MAE** (Mean Absolute Error): Erro absoluto médio
- **MAPE** (Mean Absolute Percentage Error): Erro percentual médio
- **RMSE** (Root Mean Squared Error): Raiz do erro quadrático médio
- **Gráfico de Dispersão**: Previsto vs Real com linha de tendência

#### Modelo de Tendência (XGBoost Classifier)
- **Acurácia**: Taxa de acerto geral
- **Precision**: Precisão das previsões positivas
- **Recall**: Sensibilidade do modelo
- **F1-Score**: Média harmônica entre precision e recall
- **Matriz de Confusão**: Visualização de acertos e erros

### 4. Feature Importance
- Top 15 features mais importantes para o modelo de tendência
- Visualização em gráfico de barras horizontal
- Ajuda a entender quais indicadores técnicos são mais relevantes

### 5. Tabela de Previsões Recentes
- Últimas 20 previsões realizadas
- Comparação entre valores previstos e reais
- Indicadores visuais de acerto/erro (✅/❌/⏳)
- Status de verificação das previsões

## 🚀 Como Executar

### Pré-requisitos

1. API FastAPI rodando (porta 8000 por padrão)
2. Modelos treinados (XGBoost para preço e tendência)
3. Banco de dados PostgreSQL com dados de previsões

### Instalação de Dependências

```bash
# No diretório raiz do projeto com Poetry (recomendado)
poetry install

# Ou instalar apenas as dependências do dashboard
poetry add streamlit plotly pandas requests
```

### Executar o Dashboard

```bash
# Opção 1: Usando Poetry (recomendado)
poetry run streamlit run dashboard/app.py

# Opção 2: Dentro do ambiente virtual Poetry
poetry shell
streamlit run dashboard/app.py
```

O dashboard estará disponível em: `http://localhost:8501`

### Configuração

#### Variável de Ambiente

Por padrão, o dashboard busca a API em `http://localhost:8000`. Para mudar:

```bash
export API_URL=http://sua-api:porta
streamlit run dashboard/app.py
```

#### Configurações na Interface

- **Intervalo de Atualização**: Configure entre 10 e 300 segundos (sidebar)
- **Período de Análise**: Escolha entre 1h, 6h, 24h ou 7 dias (sidebar)

## 📊 Estrutura de Dados

### Endpoints Utilizados

1. **`GET /price/latest`**: Último preço do Bitcoin
2. **`GET /price/predict/next`**: Previsão de preço
3. **`GET /trend/predict`**: Previsão de tendência
4. **`GET /predictions/history`**: Histórico de previsões
5. **`GET /price/history`**: Histórico de preços
6. **`GET /predictions/accuracy`**: Métricas de acurácia
7. **`GET /trend/feature-importance`**: Importância das features

## 🎨 Personalização

### Modificar Cores

Edite a seção de estilos CSS no início de `app.py`:

```python
st.markdown("""
<style>
    .main-header {
        color: #f7931a;  # Cor laranja do Bitcoin
    }
    .up-trend {
        color: #00c853;  # Verde para tendências de alta
    }
    .down-trend {
        color: #d32f2f;  # Vermelho para tendências de baixa
    }
</style>
""", unsafe_allow_html=True)
```

### Adicionar Novos Gráficos

O dashboard usa Plotly para visualizações. Exemplo:

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=data['x'], y=data['y']))
st.plotly_chart(fig, use_container_width=True)
```

## 🔧 Troubleshooting

### Dashboard não carrega dados

1. Verifique se a API está rodando: `curl http://localhost:8000/health`
2. Confirme que os modelos foram treinados
3. Verifique se há dados no banco de dados

### Gráficos vazios

- Aguarde pelo menos 15 minutos após iniciar o sistema para que previsões sejam verificadas
- Verifique os logs da API para erros no prediction_collector

### Performance lenta

- Reduza o intervalo de atualização
- Limite o período de análise (use 1h ou 6h)
- Verifique a performance do banco de dados

## 📈 Métricas e Interpretação

### Modelo de Preço

- **MAE < $500**: Excelente
- **MAE $500-$1000**: Bom
- **MAE > $1000**: Precisa melhorar

### Modelo de Tendência

- **Acurácia > 60%**: Melhor que chance aleatória
- **Acurácia > 70%**: Bom desempenho
- **Acurácia > 80%**: Excelente desempenho

## 🔄 Auto-Refresh

O dashboard atualiza automaticamente a cada intervalo configurado. O cache de dados é:

- **Preços e Previsões**: 60 segundos
- **Feature Importance**: 5 minutos (300 segundos)

## 💡 Dicas de Uso

1. **Análise de Curto Prazo**: Use período de 1h ou 6h para decisões rápidas
2. **Análise de Tendência**: Use 24h ou 7d para entender padrões mais longos
3. **Validação de Modelo**: Acompanhe a seção de Performance para verificar se os modelos precisam retreino
4. **Feature Importance**: Use para entender quais indicadores são mais relevantes no momento

## 📝 Notas

- As previsões são atualizadas a cada minuto pelo prediction_collector
- Valores reais são preenchidos após 15 minutos da previsão
- Dados mais antigos que 90 dias são removidos automaticamente
- O dashboard é read-only, não modifica dados no banco

## 🆘 Suporte

Para issues e bugs, consulte a documentação principal do projeto em `../README.md`
