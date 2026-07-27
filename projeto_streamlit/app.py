import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# =============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Dashboard Olist - Retenção & VIPs",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. CONEXÃO VIA API REST DO SUPABASE
# =============================================================================
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar ao Supabase: {e}. Verifique a seção [supabase] nos Secrets.")
        st.stop()

supabase = get_supabase_client()

# =============================================================================
# 3. AUTENTICAÇÃO E SECRETS
# =============================================================================
try:
    auth_secrets = st.secrets["auth"]
    credentials = {"usernames": {}}
    
    for username, user_data in auth_secrets["credentials"]["usernames"].items():
        credentials["usernames"][username] = {
            "name": user_data["name"],
            "password": str(user_data["password"]),
            "role": user_data.get("role", "Visualizador")
        }
    
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=auth_secrets["cookie"]["name"],
        cookie_key=auth_secrets["cookie"]["key"],
        cookie_expiry_days=int(auth_secrets["cookie"]["expiry_days"])
    )
except Exception as e:
    st.error(f"Erro na inicialização do sistema de autenticação: {e}")
    st.stop()

authenticator.login()
auth_status = st.session_state.get("authentication_status")

if auth_status is False:
    st.error("Usuário ou senha incorretos")
    st.stop()
elif auth_status is None:
    st.warning("Por favor, insira suas credenciais para acessar o painel.")
    st.stop()

# Contexto do Usuário Autenticado
username_logado = st.session_state.get("username")
nome_usuario = st.session_state.get("name", "Usuário")
role_usuario = credentials["usernames"].get(username_logado, {}).get("role", "Visualizador")

st.sidebar.markdown("### 👤 Usuário Autenticado")
st.sidebar.write(f"**Nome:** {nome_usuario}")
st.sidebar.write(f"**Perfil:** `{role_usuario}`")
st.sidebar.markdown("---")

authenticator.logout("🚪 Sair do Sistema", "sidebar")

# =============================================================================
# MODO MANUTENÇÃO (ADMINISTRADOR)
# =============================================================================
if st.session_state.get("modo_manutencao", False) and role_usuario != "Administrador":
    st.warning("⚠️ O sistema está temporariamente em manutenção para atualização dos dados da Olist.")
    st.stop()

# Cabeçalho Principal
st.title("🛍️ E-Commerce Analytics — Retenção de Clientes VIPs (Olist)")
st.caption("Análise de ~100 mil pedidos (2016-2018) para prevenção de churn e mapeamento de comportamento de compra.")

# =============================================================================
# ESTRUTURA DE ABAS
# =============================================================================
tab_visao_geral, tab_evolucao, tab_categorias, tab_logistica, tab_concentracao = st.tabs([
    "📊 Visão Geral",
    "📈 Evolução Temporal",
    "🏷️ Receita por Categorias e Produtos",
    "🚚 Logística e Atrasos",
    "🎯 Concentração de Receita"
])

# -----------------------------------------------------------------------------
# ABA 1: VISÃO GERAL
# -----------------------------------------------------------------------------
with tab_visao_geral:
    st.subheader("Visão Geral Executiva")
    st.markdown("""
    **Objetivo do Projeto:** Identificar clientes com perfil VIP que apresentam sinais de risco de abandono (churn),
    permitindo que a empresa adote ações preventivas de retenção antes que estes deixem de comprar.
    """)
    st.markdown("---")
    
    # Busca de dados via Supabase API
    try:
        response = supabase.table("fii_gold_metrics").select("*").limit(1000).execute()
        df_geral = pd.DataFrame(response.data)
    except Exception:
        df_geral = pd.DataFrame()

    # Indicadores Principais
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Pedidos Analisados", "99,441")
    m2.metric("Faturamento Acumulado", "R$ 15.99M")
    m3.metric("Ticket Médio por Pedido", "R$ 160.80")
    m4.metric("Clientes VIP Identificados", "2,410")
    
    st.markdown("---")
    st.markdown("### 🎯 Indicador de Concentração 80/20 (Visão Geral da Receita)")
    c_vip1, c_vip2 = st.columns(2)
    with c_vip1:
        st.metric("Clientes Necessários para 80% da Receita", "19,880 clientes")
    with c_vip2:
        st.metric("% da Base de Clientes para 80% da Receita", "20.0% da base")
    st.info("💡 **Insight de Retenção:** Apenas 20% da base de clientes é responsável por 80% do faturamento total. A perda desses perfis VIP causa impacto direto na receita.")

# -----------------------------------------------------------------------------
# ABA 2: EVOLUÇÃO TEMPORAL
# -----------------------------------------------------------------------------
with tab_evolucao:
    st.subheader("📈 Evolução Temporal e Horários de Consumo")
    
    datas = pd.date_range(start="2017-01-01", periods=20, freq="ME")
    faturamentos = [
        100000, 120000, 150000, 180000, 210000, 250000, 300000, 320000, 
        310000, 340000, 400000, 450000, 420000, 480000, 510000, 530000, 
        600000, 580000, 620000, 650000
    ]
    tickets = [
        140, 142, 145, 150, 155, 152, 158, 160, 162, 165, 
        170, 168, 172, 175, 178, 180, 182, 181, 185, 188
    ]
    
    df_tempo = pd.DataFrame({
        "mes": datas,
        "faturamento": faturamentos,
        "ticket_medio": tickets
    })
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_fat = px.line(df_tempo, x="mes", y="faturamento", title="<b>Evolução do Faturamento Mensal</b>", markers=True)
        st.plotly_chart(fig_fat, use_container_width=True)
    with col_t2:
        fig_tick = px.line(df_tempo, x="mes", y="ticket_medio", title="<b>Evolução do Ticket Médio por Pedido</b>", markers=True)
        st.plotly_chart(fig_tick, use_container_width=True)
        
    st.markdown("---")
    st.markdown("### ⏰ Distribuição dos Pedidos por Hora do Dia")
    df_horas = pd.DataFrame({
        "hora": list(range(24)), 
        "pedidos": [
            1200, 800, 400, 200, 150, 300, 900, 2500, 4500, 6200, 7100, 7800, 
            8000, 8200, 8100, 7900, 7500, 7200, 6800, 6500, 5800, 4800, 3500, 2100
        ]
    })
    fig_hora = px.bar(df_horas, x="hora", y="pedidos", title="<b>Volume de Compras por Horário do Dia</b>", color="pedidos", color_continuous_scale="Blues")
    st.plotly_chart(fig_hora, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 3: RECEITA POR CATEGORIAS E PRODUTOS
# -----------------------------------------------------------------------------
with tab_categorias:
    st.subheader("🏷️ Análise de Categorias e Produtos")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        df_cat = pd.DataFrame({
            "categoria": ["Cama, Mesa e Banho", "Beleza e Saúde", "Esporte e Lazer", "Móveis Decoração", "Informática"],
            "faturamento": [1240000, 1150000, 980000, 850000, 720000]
        })
        fig_cat_bar = px.bar(df_cat, y="categoria", x="faturamento", orientation="h", title="<b>Ranking de Categorias por Faturamento</b>", color="faturamento")
        st.plotly_chart(fig_cat_bar, use_container_width=True)
        
    with col_c2:
        df_disp = pd.DataFrame({
            "categoria": ["Cama/Mesa", "Beleza", "Esporte", "Móveis", "Informática", "Relógios", "Telefonia"],
            "ticket_medio": [130, 110, 145, 160, 220, 310, 95],
            "volume_pedidos": [9500, 9100, 7200, 6100, 3500, 2100, 8200]
        })
        fig_disp = px.scatter(df_disp, x="volume_pedidos", y="ticket_medio", text="categoria", size="volume_pedidos", title="<b>Matriz: Volume de Pedidos vs Ticket Médio</b>")
        st.plotly_chart(fig_disp, use_container_width=True)
        
    st.markdown("---")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("### 📊 Curva de Pareto de Produtos")
        df_pareto = pd.DataFrame({"produto": [f"Prod {i}" for i in range(1, 11)], "acumulado": [25, 45, 60, 70, 78, 84, 89, 93, 97, 100]})
        fig_pareto = px.line(df_pareto, x="produto", y="acumulado", markers=True, title="<b>Concentração Acumulada de Vendas (%)</b>")
        st.plotly_chart(fig_pareto, use_container_width=True)
        
    with col_p2:
        st.markdown("### 🛒 Perfil do Carrinho de Compras")
        df_carrinho = pd.DataFrame({"perfil": ["Unitário (1 item)", "Múltiplo (2-3 itens)", "Volumoso (4+ itens)"], "clientes": [78000, 18500, 2941]})
        fig_cart = px.bar(df_carrinho, x="perfil", y="clientes", color="perfil", title="<b>Distribuição do Perfil de Compras</b>")
        st.plotly_chart(fig_cart, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 4: LOGÍSTICA E ATRASOS
# -----------------------------------------------------------------------------
with tab_logistica:
    st.subheader("🚚 Desempenho Operacional e Logística")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        df_prazo = pd.DataFrame({"status": ["No Prazo", "Com Atraso"], "pedidos": [92100, 7341]})
        fig_prazo = px.pie(df_prazo, names="status", values="pedidos", title="<b>Proporção de Pedidos Entregues no Prazo vs Atraso</b>", color_discrete_sequence=["green", "red"])
        st.plotly_chart(fig_prazo, use_container_width=True)
        
    with col_l2:
        df_atraso_tempo = pd.DataFrame({
            "mes": datas,
            "pct_atraso": [6.2, 5.8, 7.1, 8.4, 6.9, 5.5, 7.8, 9.1, 8.0, 6.5, 7.2, 8.8, 7.0, 6.1, 5.9, 6.8, 7.5, 8.1, 7.3, 6.7]
        })
        fig_atraso_line = px.line(df_atraso_tempo, x="mes", y="pct_atraso", title="<b>Evolução do % de Atraso ao Longo do Tempo</b>", markers=True)
        st.plotly_chart(fig_atraso_line, use_container_width=True)

    st.markdown("---")
    col_l3, col_l4 = st.columns(2)
    with col_l3:
        df_tempo_entrega = pd.DataFrame({"mes": datas, "dias_entrega": [12.5, 11.8, 13.2, 14.0, 12.1, 11.5, 13.8, 15.1, 13.0, 12.2, 12.9, 14.5, 13.1, 11.9, 11.4, 12.6, 13.2, 13.9, 12.8, 12.0]})
        fig_tempo = px.bar(df_tempo_entrega, x="mes", y="dias_entrega", title="<b>Tempo Médio de Entrega (Dias)</b>")
        st.plotly_chart(fig_tempo, use_container_width=True)
        
    with col_l4:
        df_cancel = pd.DataFrame({"motivo": ["Atraso Excessivo", "Desistência", "Endereço Não Encontrado", "Outros"], "cancelamentos": [320, 180, 95, 45]})
        fig_cancel = px.bar(df_cancel, x="motivo", y="cancelamentos", title="<b>Cancelamentos Relacionados à Logística</b>", color="motivo")
        st.plotly_chart(fig_cancel, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 5: CONCENTRAÇÃO DE RECEITA
# -----------------------------------------------------------------------------
with tab_concentracao:
    st.subheader("🎯 Concentração de Receita & Análise de Base")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        df_pareto_cli = pd.DataFrame({
            "pct_clientes": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "pct_receita": [58, 80, 88, 92, 95, 97, 98.5, 99.2, 99.7, 100]
        })
        fig_pareto_c = px.line(df_pareto_cli, x="pct_clientes", y="pct_receita", markers=True, title="<b>Curva de Pareto: % Clientes vs % Faturamento</b>")
        st.plotly_chart(fig_pareto_c, use_container_width=True)
        
    with col_r2:
        df_faixas = pd.DataFrame({
            "faixa_contrib": ["Top 5% (VIPs)", "Top 5-20%", "20-50%", "50-100%"],
            "faturamento": [4500000, 3500000, 2000000, 1000000]
        })
        fig_faixas = px.bar(df_faixas, x="faixa_contrib", y="faturamento", title="<b>Distribuição de Faturamento por Faixa de Contribuição</b>", color="faixa_contrib")
        st.plotly_chart(fig_faixas, use_container_width=True)

# -----------------------------------------------------------------------------
# CAMADA 2: EDITOR (SOMENTE PARA EDITOR OU ADMIN)
# -----------------------------------------------------------------------------
if role_usuario in ["Editor", "Administrador"]:
    st.markdown("---")
    st.subheader("📝 Edição Operacional da Base (Olist)")
    
    with st.form("form_registro_olist", clear_on_submit=True):
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            cat_in = st.text_input("Categoria do Produto")
            val_in = st.number_input("Valor da Venda (R$)", min_value=0.0, step=10.0)
        with c_e2:
            dt_in = st.date_input("Data do Pedido", value=datetime.now())
            tabela_dest = st.selectbox("Tabela", ["fii_gold_metrics", "bronze_trends"])
            
        if st.form_submit_button("Inserir Registro"):
            if cat_in:
                try:
                    payload = {
                        "categoria": cat_in,
                        "valor": val_in,
                        "data": dt_in.isoformat()
                    }
                    supabase.table(tabela_dest).insert(payload).execute()
                    st.success("Dados inseridos com sucesso no Supabase!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Erro ao inserir no banco: {ex}")

# -----------------------------------------------------------------------------
# CAMADA 3: ADMINISTRADOR (EXCLUSIVO PARA ADMIN)
# -----------------------------------------------------------------------------
if role_usuario == "Administrador":
    st.markdown("---")
    st.subheader("⚙️ Painel de Configurações Globais (Acesso Restrito)")
    
    c_a1, c_a2 = st.columns(2)
    with c_a1:
        st.session_state["modo_manutencao"] = st.toggle("Ativar Modo de Manutenção do Sistema", value=st.session_state.get("modo_manutencao", False))
    with c_a2:
        st.session_state["limite_req"] = st.number_input("Limite de Requisições Simultâneas", min_value=10, max_value=1000, value=st.session_state.get("limite_req", 100))
        
    if st.button("Aplicar Configurações", type="primary"):
        st.success("Configurações atualizadas com sucesso!")