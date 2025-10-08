import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os
import warnings
import pytz
warnings.filterwarnings('ignore', category=FutureWarning, module='plotly')

# Configuração da página
st.set_page_config(
    page_title="Bitcoin Price Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# URL da API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Estilo customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #f7931a;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .up-trend {
        color: #00c853;
        font-weight: bold;
    }
    .down-trend {
        color: #d32f2f;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="main-header">₿ Bitcoin Price Prediction Dashboard</h1>', unsafe_allow_html=True)

# Função para buscar dados da API
@st.cache_data(ttl=60)
def fetch_latest_price():
    """Busca o último preço do Bitcoin"""
    try:
        response = requests.get(f"{API_URL}/price/latest", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar preço atual: {str(e)}")
        return None

@st.cache_data(ttl=60)
def fetch_price_prediction():
    """Busca previsão de preço"""
    try:
        response = requests.get(f"{API_URL}/price/predict/next", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def fetch_trend_prediction():
    """Busca previsão de tendência"""
    try:
        response = requests.get(f"{API_URL}/trend/predict", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def fetch_predictions_history(hours=24):
    """Busca histórico de previsões"""
    try:
        response = requests.get(f"{API_URL}/predictions/history?hours={hours}&limit=1000", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Erro ao buscar histórico de previsões: {str(e)}")
        return []

@st.cache_data(ttl=60)
def fetch_price_history(hours=24):
    """Busca histórico de preços"""
    try:
        response = requests.get(f"{API_URL}/price/history?hours={hours}&limit=1500", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Erro ao buscar histórico de preços: {str(e)}")
        return []

@st.cache_data(ttl=60)
def fetch_accuracy_metrics(hours=24):
    """Busca métricas de acurácia"""
    try:
        response = requests.get(f"{API_URL}/predictions/accuracy?hours={hours}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_feature_importance():
    """Busca importância das features"""
    try:
        response = requests.get(f"{API_URL}/trend/feature-importance", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

# Auto-refresh
refresh_interval = st.sidebar.number_input("Intervalo de atualização (segundos)", min_value=10, max_value=300, value=60)
time_range = st.sidebar.selectbox("Período de análise", ["1h", "6h", "24h", "7d"], index=2)

# Mapear período para horas
hours_map = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}
selected_hours = hours_map[time_range]

# Placeholder para auto-refresh
placeholder = st.empty()

# Loop de atualização
refresh_counter = 0
while True:
    refresh_counter += 1
    with placeholder.container():
        # ========== SEÇÃO 1: MÉTRICAS EM TEMPO REAL ==========
        st.markdown("### 📊 Métricas em Tempo Real")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Buscar dados
        latest_price = fetch_latest_price()
        price_pred = fetch_price_prediction()
        trend_pred = fetch_trend_prediction()
        
        with col1:
            if latest_price:
                price_val = float(latest_price['price'])
                st.metric(
                    label="💰 Preço Atual",
                    value=f"${price_val:,.2f}",
                    delta=None
                )
            else:
                st.metric(label="💰 Preço Atual", value="N/A")
        
        with col2:
            if price_pred:
                predicted_price = price_pred['predicted_price']
                price_change = price_pred['price_change']
                st.metric(
                    label="🔮 Previsão 15min",
                    value=f"${predicted_price:,.2f}",
                    delta=f"${price_change:+,.2f}"
                )
            else:
                st.metric(label="🔮 Previsão 15min", value="N/A")
        
        with col3:
            if trend_pred:
                trend = trend_pred['trend']
                confidence = trend_pred['confidence'] * 100
                trend_color = "🟢" if trend == "UP" else "🔴"
                st.metric(
                    label=f"{trend_color} Tendência Prevista",
                    value=trend,
                    delta=f"{confidence:.1f}% confiança"
                )
            else:
                st.metric(label="📈 Tendência", value="N/A")
        
        with col4:
            if trend_pred:
                prob_up = trend_pred['probability_up'] * 100
                prob_down = trend_pred['probability_down'] * 100
                st.metric(
                    label="⚖️ Probabilidades",
                    value=f"↑{prob_up:.0f}% / ↓{prob_down:.0f}%"
                )
            else:
                st.metric(label="⚖️ Probabilidades", value="N/A")
        
        st.markdown("---")
        
        # ========== SEÇÃO 2: GRÁFICO PRINCIPAL - PREVISTO VS REAL ==========
        st.markdown("### 📈 Análise: Previsto vs Real")
        
        # Buscar histórico
        predictions = fetch_predictions_history(selected_hours)
        price_history = fetch_price_history(selected_hours)
        
        if predictions and price_history:
            # Converter para DataFrame
            df_pred = pd.DataFrame(predictions)
            df_prices = pd.DataFrame(price_history)
            
            # Converter timestamps para timezone de Brasília
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            
            df_pred['timestamp'] = pd.to_datetime(df_pred['timestamp'])
            df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'])
            
            # Converter para Brasília/São Paulo
            if df_pred['timestamp'].dt.tz is None:
                df_pred['timestamp'] = df_pred['timestamp'].dt.tz_localize('UTC').dt.tz_convert(brasilia_tz)
            else:
                df_pred['timestamp'] = df_pred['timestamp'].dt.tz_convert(brasilia_tz)
            
            if df_prices['timestamp'].dt.tz is None:
                df_prices['timestamp'] = df_prices['timestamp'].dt.tz_localize('UTC').dt.tz_convert(brasilia_tz)
            else:
                df_prices['timestamp'] = df_prices['timestamp'].dt.tz_convert(brasilia_tz)
            
            # Criar gráfico
            fig = go.Figure()
            
            # Linha do preço real
            fig.add_trace(go.Scatter(
                x=df_prices['timestamp'],
                y=df_prices['price'].astype(float),
                mode='lines',
                name='Preço Real',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Pontos de previsão
            df_pred_with_actual = df_pred[df_pred['actual_price'].notna()]
            if not df_pred_with_actual.empty:
                fig.add_trace(go.Scatter(
                    x=df_pred_with_actual['timestamp'],
                    y=df_pred_with_actual['predicted_price'].astype(float),
                    mode='markers',
                    name='Previsão',
                    marker=dict(color='#ff7f0e', size=8, symbol='diamond')
                ))
                
                # Linha conectando previsões
                fig.add_trace(go.Scatter(
                    x=df_pred_with_actual['timestamp'],
                    y=df_pred_with_actual['predicted_price'].astype(float),
                    mode='lines',
                    name='Linha de Previsão',
                    line=dict(color='#ff7f0e', width=1, dash='dot'),
                    showlegend=False
                ))
            
            # Área de erro (MAE)
            if price_pred and 'model_mae' in price_pred:
                mae = price_pred['model_mae']
                current_prices = df_prices['price'].astype(float)
                fig.add_trace(go.Scatter(
                    x=df_prices['timestamp'],
                    y=current_prices + mae,
                    mode='lines',
                    name='Margem de Erro',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                fig.add_trace(go.Scatter(
                    x=df_prices['timestamp'],
                    y=current_prices - mae,
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(68, 68, 68, 0.1)',
                    fill='tonexty',
                    name='±MAE',
                    showlegend=True,
                    hoverinfo='skip'
                ))
            
            fig.update_layout(
                title=f"Preço do Bitcoin - Últimas {time_range}",
                xaxis_title="Timestamp",
                yaxis_title="Preço (USD)",
                hovermode='x unified',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, width='stretch', key=f'main_chart_{refresh_counter}')
        else:
            st.info("Aguardando dados de previsões...")
        
        st.markdown("---")
        
        # ========== SEÇÃO 3: ANÁLISE DE PERFORMANCE ==========
        st.markdown("### 🎯 Análise de Performance dos Modelos")
        
        col_left, col_right = st.columns(2)
        
        # Buscar métricas
        accuracy_metrics = fetch_accuracy_metrics(selected_hours)
        
        with col_left:
            st.markdown("#### 💵 Modelo de Preço (XGBoost Regressor)")
            
            if accuracy_metrics and accuracy_metrics['verified_predictions'] > 0:
                metrics_df = pd.DataFrame({
                    'Métrica': ['MAE Médio', 'MAPE Médio', 'RMSE'],
                    'Valor': [
                        f"${accuracy_metrics['price_mae_avg']:.2f}",
                        f"{accuracy_metrics['price_mape_avg']:.2f}%",
                        f"${accuracy_metrics['price_rmse']:.2f}"
                    ]
                })
                st.dataframe(metrics_df, hide_index=True)
                
                # Gráfico de dispersão previsto vs real
                if predictions:
                    df_verified = df_pred[df_pred['actual_price'].notna()].copy()
                    if not df_verified.empty:
                        fig_scatter = px.scatter(
                            df_verified,
                            x='predicted_price',
                            y='actual_price',
                            title="Previsto vs Real",
                            labels={'predicted_price': 'Preço Previsto', 'actual_price': 'Preço Real'}
                        )
                        fig_scatter.add_trace(go.Scatter(
                            x=[df_verified['predicted_price'].min(), df_verified['predicted_price'].max()],
                            y=[df_verified['predicted_price'].min(), df_verified['predicted_price'].max()],
                            mode='lines',
                            name='Linha Ideal',
                            line=dict(color='red', dash='dash')
                        ))
                        st.plotly_chart(fig_scatter, width='stretch', key=f'scatter_chart_{refresh_counter}')
            else:
                st.info("Aguardando previsões verificadas...")
        
        with col_right:
            st.markdown("#### 📊 Modelo de Tendência (XGBoost Classifier)")
            
            if accuracy_metrics and accuracy_metrics['verified_predictions'] > 0:
                metrics_df = pd.DataFrame({
                    'Métrica': ['Acurácia', 'Precision', 'Recall', 'F1-Score'],
                    'Valor': [
                        f"{accuracy_metrics['trend_accuracy']*100:.1f}%",
                        f"{accuracy_metrics['trend_precision']*100:.1f}%",
                        f"{accuracy_metrics['trend_recall']*100:.1f}%",
                        f"{accuracy_metrics['trend_f1']*100:.1f}%"
                    ]
                })
                st.dataframe(metrics_df, hide_index=True)
                
                # Matriz de confusão
                cm_data = [
                    [accuracy_metrics['true_negatives'], accuracy_metrics['false_positives']],
                    [accuracy_metrics['false_negatives'], accuracy_metrics['true_positives']]
                ]
                fig_cm = go.Figure(data=go.Heatmap(
                    z=cm_data,
                    x=['DOWN', 'UP'],
                    y=['DOWN', 'UP'],
                    text=cm_data,
                    texttemplate='%{text}',
                    colorscale='Blues'
                ))
                fig_cm.update_layout(
                    title="Matriz de Confusão",
                    xaxis_title="Previsto",
                    yaxis_title="Real",
                    height=350
                )
                st.plotly_chart(fig_cm, width='stretch', key=f'confusion_matrix_{refresh_counter}')
            else:
                st.info("Aguardando previsões verificadas...")
        
        st.markdown("---")
        
        # ========== SEÇÃO 4: FEATURE IMPORTANCE ==========
        st.markdown("### 🔍 Importância das Features (Top 15)")
        
        feature_data = fetch_feature_importance()
        
        if feature_data and feature_data['features']:
            top_features = feature_data['features'][:15]
            df_features = pd.DataFrame(top_features)
            
            fig_features = px.bar(
                df_features,
                x='importance',
                y='feature',
                orientation='h',
                title="Features Mais Importantes para Previsão de Tendência",
                labels={'importance': 'Importância', 'feature': 'Feature'},
                color='importance',
                color_continuous_scale='Viridis'
            )
            fig_features.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_features, width='stretch', key=f'features_chart_{refresh_counter}')
        else:
            st.info("Dados de feature importance não disponíveis")
        
        st.markdown("---")
        
        # ========== SEÇÃO 5: TABELA DE PREVISÕES RECENTES ==========
        st.markdown("### 📋 Previsões Recentes")
        
        if predictions:
            df_recent = df_pred.head(60).copy()
            
            # Converter timestamps para timezone de Brasília
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            # Check if already tz-aware, if not localize first
            if df_recent['timestamp'].dt.tz is None:
                df_recent['timestamp_brasilia'] = df_recent['timestamp'].dt.tz_localize('UTC').dt.tz_convert(brasilia_tz)
            else:
                df_recent['timestamp_brasilia'] = df_recent['timestamp'].dt.tz_convert(brasilia_tz)
            
            # Preparar dados para exibição
            display_df = pd.DataFrame({
                'Timestamp': df_recent['timestamp_brasilia'].dt.strftime('%Y-%m-%d %H:%M'),
                'Preço Atual': df_recent['current_price'].astype(float).apply(lambda x: f"${x:,.2f}"),
                'Previsto': df_recent['predicted_price'].astype(float).apply(lambda x: f"${x:,.2f}"),
                'Real': df_recent['actual_price'].apply(lambda x: f"${float(x):,.2f}" if pd.notna(x) else "Aguardando"),
                'Erro': df_recent['prediction_error'].apply(lambda x: f"${float(x):+,.2f}" if pd.notna(x) else "-"),
                'Tendência Prev.': df_recent['predicted_trend'],
                'Tendência Real': df_recent['actual_trend'].fillna('-'),
                'Status': df_recent['trend_correct'].apply(
                    lambda x: "✅" if x == 1 else ("❌" if x == 0 else "⏳")
                )
            })
            
            st.dataframe(display_df, hide_index=True)
        else:
            st.info("Nenhuma previsão disponível ainda")
        
        # Informações de atualização
        st.markdown("---")
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.caption(f"📅 Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        with col_info2:
            st.caption(f"🔄 Próxima atualização em: {refresh_interval}s")
        with col_info3:
            if accuracy_metrics:
                st.caption(f"📊 Previsões verificadas: {accuracy_metrics['verified_predictions']}/{accuracy_metrics['total_predictions']}")
    
    # Aguardar antes da próxima atualização
    time.sleep(refresh_interval)
