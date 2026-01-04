import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

# --- CONFIGURAÇÃO CFO. ---
st.set_page_config(page_title="CFO. | Operação", layout="centered")

def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$  {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_success = load_lottieurl("https://lottie.host/5a2d67a1-94a3-4886-905c-5912389d4d03/GjX1Xl9T8y.json")

# --- CSS PRECISÃO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    .stButton>button { width: 100%; background-color: #000 !important; color: #FFF !important; border-radius: 0px; padding: 14px; font-weight: 800; border: none; text-transform: uppercase; letter-spacing: 2px; font-size: 11px; }
    .back-arrow>div>button { background-color: transparent !important; color: #000 !important; border: none !important; font-size: 24px !important; padding: 0 !important; width: 40px !important; height: 40px !important; line-height: 1 !important; }
    .stNumberInput input, .stTextInput input { border: none !important; border-bottom: 1px solid #000 !important; border-radius: 0px !important; font-size: 18px !important; font-weight: 600 !important; }
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 40px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 38px; font-weight: 800; margin-top: 5px; letter-spacing: 1px; line-height: 1.1; color: #000; display: block; }
    .card { padding: 30px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'show_anim', 'reset_mode']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# --- CONEXÃO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    if st.session_state.step == 0 and not st.session_state.reset_mode:
        check_df = conn.read(worksheet="Config", usecols=[0,1], ttl=0)
        if not check_df.empty:
            st.session_state.step = 4
            for _, row in check_df.iterrows():
                if row['parametro'] == 'saldo_inicial': st.session_state.opening_balance = float(row['valor'])
                if row['parametro'] == 'reserva': st.session_state.strategic_reserve = float(row['valor'])
                if row['parametro'] == 'investimento': st.session_state.investments = float(row['valor'])
                if row['parametro'] == 'sonhos': st.session_state.dreams = float(row['valor'])
except: pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

if st.session_state.show_anim and lottie_success:
    st_lottie(lottie_success, height=80, speed=1.8, key="success_anim")
    time.sleep(0.8)
    st.session_state.show_anim = False
    st.rerun()

# --- ETAPAS 0-3 (Liquidez, Entradas, Custos, Alocação) ---
# [Mantenha o código das etapas anteriores igual ao da V29/V30]
# ... (Navegação com flechas minimalistas) ...

# --- DASHBOARD (PASSO 4) ---
if st.session_state.step == 4:
    st.markdown('<p class="setup-step">VISÃO ANALÍTICA CFO.</p>', unsafe_allow_html=True)
    
    # 1. PROCESSAMENTO DE GASTOS (FORÇANDO ATUALIZAÇÃO)
    gastos_totais_mes = 0.0
    gastos_hoje = 0.0
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    try:
        # ttl=0 obriga o app a buscar dados novos no Google
        df_l = conn.read(worksheet="Lancamentos", ttl=0)
        if not df_l.empty:
            df_l['valor'] = pd.to_numeric(df_l['valor'], errors='coerce').fillna(0)
            gastos_totais_mes = df_l['valor'].sum()
            gastos_hoje = df_l[df_l['data'].str.contains(data_hoje, na=False)]['valor'].sum()
    except:
        df_l = pd.DataFrame(columns=['data', 'descricao', 'valor'])

    # 2. CÁLCULO DE FLUXO
    dias_restantes = max(31 - datetime.now().day, 1)
    dias = np.arange(1, 32)
    saldo_diario = []
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams - gastos_totais_mes
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # 3. GRÁFICO
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in saldo_diario]))
    fig.add_hline(y=st.session_state.strategic_reserve/1000, line_dash="dash", line_color="#CCC", line_width=1)
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F9F9F9', tickformat='.0f', ticksuffix='k'),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 4. KPIs
    t_in, t_out = sum(i['val'] for i in st.session_state.incomes), sum(e['val'] for e in st.session_state.expenses)
    livre_mes = (st.session_state.opening_balance - st.session_state.strategic_reserve + t_in) - t_out - st.session_state.investments - st.session_state.dreams - gastos_totais_mes
