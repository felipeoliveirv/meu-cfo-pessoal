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

# --- TELAS DE CONFIGURAÇÃO (0 A 3) ---
# [O código das etapas anteriores permanece igual ao da V26]
# ... (Aqui viria o código de Liquidez, Entradas, Custos e Alocação) ...

# --- DASHBOARD DINÂMICO (PASSO 4) ---
if st.session_state.step == 4:
    st.markdown('<p class="setup-step">VISÃO ANALÍTICA CFO.</p>', unsafe_allow_html=True)
    
    # 1. CARREGAR GASTOS REAIS COM FORÇA DE TIPAGEM
    gastos_reais = 0.0
    try:
        lancamentos_df = conn.read(worksheet="Lancamentos", ttl=0)
        if not lancamentos_df.empty:
            # Força a conversão para numérico para evitar erros de soma
            lancamentos_df['valor'] = pd.to_numeric(lancamentos_df['valor'], errors='coerce')
            gastos_reais = lancamentos_df['valor'].sum()
    except: pass

    # 2. CÁLCULO DE FLUXO (ABATENDO GASTOS REAIS)
    dias_no_mes = 30
    dia_atual = datetime.now().day
    dias_restantes = max(dias_no_mes - dia_atual, 1)

    dias = np.arange(1, 32)
    saldo_diario = []
    # O caixa atual já nasce subtraindo o que você já gastou este mês
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams - gastos_reais
    
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # 3. GRÁFICO ATUALIZADO
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in saldo_diario]))
    fig.add_hline(y=st.session_state.strategic_reserve/1000, line_dash="dash", line_color="#CCC", line_width=1)
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F9F9F9', tickformat='.0f', ticksuffix='k'),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 4. KPIs REAIS
    t_in = sum(i['val'] for i in st.session_state.incomes)
    t_out = sum(e['val'] for e in st.session_state.expenses)
    
    # O Capital Operacional agora mostra estritamente o que resta "na mão"
    total_operacional = (st.session_state.opening_balance - st.session_state.strategic_reserve + t_in) - t_out - st.session_state.investments - st.session_state.dreams
    livre_agora = total_operacional - gastos_reais
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card"><p class="metric-label">Operacional Restante</p><p class="metric-value">{format_br(livre_agora)}</p></div>', unsafe_allow_html=True)
    with col2:
        # Cota Diária agora divide o que SOBROU pelos dias que FALTAM
        st.markdown(f'<div class="card"><p class="metric-label">Cota Diária (Hoje)</p><p class="metric-value">{format_br(max(livre_agora/dias_restantes, 0))[:-3]}</p></div>', unsafe_allow_html=True)

    st.markdown(f'<p style="color:#888; font-size:11px; margin-top:-10px;">Gasto acumulado no mês: {format_br(gastos_reais)}</p>', unsafe_allow_html=True)

    # 5. LANÇAMENTO (DAILY LOG)
    with st.expander("📝 REGISTRAR NOVO GASTO", expanded=False):
        c_l1, c_l2 = st.columns([2, 1])
        l_desc = c_l1.text_input("DESCRIÇÃO", placeholder="Ex: Jantar")
        l_val = c_l2.number_input("VALOR", min_value=0.0, format="%.2f")
        if st.button("LOG_CASH_OUT"):
            novo_log = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "descricao": l_desc, "valor": l_val}])
            try:
                hist_df = conn.read(worksheet="Lancamentos", ttl=0)
                updated_df = pd.concat([hist_df, novo_log], ignore_index=True)
                conn.update(worksheet="Lancamentos", data=updated_df)
                st.session_state.show_anim = True; st.rerun()
            except:
                conn.update(worksheet="Lancamentos", data=novo_log)
                st.session_state.show_anim = True; st.rerun()

    if st.button("REDEFINIR ESTRATÉGIA"):
        st.session_state.step = 0; st.session_state.reset_mode = True; st.rerun()
