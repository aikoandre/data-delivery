import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Page Configuration
st.set_page_config(page_title="Data Delivery - Dashboard", page_icon="🍕", layout="wide")

# Responsive CSS for small screens
st.markdown("""
<style>
    /* Center title */
    h1 { text-align: center; }

    /* Center KPI metrics */
    .kpi-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .kpi-label {
        font-size: 1rem;
        color: var(--text-color);
        opacity: 0.7;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-color);
    }

    /* Stack columns on small screens */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        [data-testid="stMetric"] {
            font-size: 0.85rem;
        }
        .block-container {
            padding: 1rem 0.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🍕 Data Delivery")
st.markdown("<p style='text-align: center;'>Interactive dashboard connected to the Data Warehouse (PostgreSQL) for order and revenue analysis.</p>", unsafe_allow_html=True)

# 2. Conexão com o Banco de Dados (Cache para não reconectar toda hora)
@st.cache_resource
def get_engine():
    # Conectando na porta 5433 conforme configurado no seu Docker!
    return create_engine('postgresql+psycopg2://usuario_etl:senha_super_secreta@localhost:5433/data_delivery')

engine = get_engine()

# 3. Funções para buscar os dados (Cache para performance)
@st.cache_data
def get_kpis():
    query = """
    SELECT 
        COUNT(pedido_id) as total_pedidos,
        SUM(valor_total) as faturamento_total
    FROM dw.fato_pedidos
    WHERE status = 'Entregue';
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_ticket_medio():
    query = """
    SELECT 
        dr.tipo_culinaria,
        ROUND(AVG(fp.valor_total)::numeric, 2) AS ticket_medio,
        COUNT(fp.pedido_id) AS total_pedidos
    FROM dw.fato_pedidos fp
    JOIN dw.dim_restaurantes dr ON fp.restaurante_id = dr.restaurante_id
    WHERE fp.status = 'Entregue'
    GROUP BY dr.tipo_culinaria
    ORDER BY ticket_medio DESC;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_ranking_estados():
    query = """
    SELECT 
        du.usuario_estado,
        dr.restaurante_nome,
        SUM(fp.valor_total) AS faturamento_total
    FROM dw.fato_pedidos fp
    JOIN dw.dim_usuarios du ON fp.usuario_id = du.usuario_id
    JOIN dw.dim_restaurantes dr ON fp.restaurante_id = dr.restaurante_id
    WHERE fp.status = 'Entregue'
    GROUP BY du.usuario_estado, dr.restaurante_nome
    ORDER BY du.usuario_estado, faturamento_total DESC;
    """
    return pd.read_sql(query, engine)

# 4. Carregando os Dados
try:
    df_kpis = get_kpis()
    df_ticket = get_ticket_medio()
    df_ranking = get_ranking_estados()
    
    # --- UI do Dashboard ---
    
    # Linha de KPIs
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>📦 Total Delivered Orders</div>
            <div class='kpi-value'>{df_kpis['total_pedidos'][0]}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        revenue = f"R$ {df_kpis['faturamento_total'][0]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>💰 Total Revenue</div>
            <div class='kpi-value'>{revenue}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Gráficos em duas colunas
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.markdown("<h3 style='text-align: center;'>Average Ticket by Cuisine</h3>", unsafe_allow_html=True)
        fig_ticket = px.bar(
            df_ticket, 
            x='tipo_culinaria', 
            y='ticket_medio',
            text='ticket_medio',
            color='ticket_medio',
            color_continuous_scale='Blues',
            labels={'tipo_culinaria': 'Cuisine Type', 'ticket_medio': 'Avg. Ticket (R$)'}
        )
        fig_ticket.update_traces(texttemplate='R$ %{text}', textposition='outside')
        fig_ticket.update_layout(showlegend=False)
        st.plotly_chart(fig_ticket, use_container_width=True)

    with col_grafico2:
        st.markdown("<h3 style='text-align: center;'>Revenue by State</h3>", unsafe_allow_html=True)
        # Agrupando por estado para um gráfico de pizza
        df_estado_total = df_ranking.groupby('usuario_estado')['faturamento_total'].sum().reset_index()
        fig_estado = px.pie(
            df_estado_total, 
            names='usuario_estado', 
            values='faturamento_total',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_estado, use_container_width=True)

    st.divider()
    
    # Tabela Interativa de Ranking
    st.subheader("🏆 Revenue Table by Restaurant and State")
    st.dataframe(
        df_ranking.style.format({"faturamento_total": "R$ {:.2f}"}),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Failed to connect to the database or load data. Make sure Docker is running! Details: {e}")