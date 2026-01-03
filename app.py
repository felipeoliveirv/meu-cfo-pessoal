import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# --- CONFIGURAÇÃO CFO. ---
st.set_page_config(page_title="CFO. | Operação", layout="centered")

# 1. FUNÇÃO DE FORMATAÇÃO
def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# 2. FUNÇÃO DE ANIMAÇÃO
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_success = load_lottieurl("https://lottie.host/5a2d67a1-94a3-4886-905c-5912389d4d03/GjX1Xl9T8y.json")

# 3. ESTILIZAÇÃO CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #FFFFFF; 
        color: #000; 
    }

    /* Botão Principal Estilo CFO. */
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 3px; font-size: 10px;
    }

    /* Botão de Voltar (Sutil) */
    .back-btn>div>button {
        width: auto !important;
        background-color: transparent !important;
        color: #888 !important;
        padding: 0px !important;
        font-size: 10px !important;
        letter-spacing: 1px !important;
        text-align: left !important;
        border: none !important;
        margin-bottom: 20px !important;
    }
    .back-btn>div>button:hover { color: #000 !important; }

    .stNumberInput input, .stTextInput input {
        border: none !important;
        border-bottom: 1px solid #000 !important;
        border-radius: 0px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 40px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 40px; font-weight: 800; margin-top: 10px; letter-spacing: 0px; line-height: 1.1; color: #000; display: block; }
    .card { padding: 40px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 4. ENGINE DE ESTADO
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'show_anim']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# 5. CONEXÃO GSHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    if st.session_state.step == 0:
        check_df = conn.read(worksheet="Config", usecols=[0,1], ttl=0)
        if not check_df.empty:
            st.session_state.step = 4
            for _, row in check_df.iterrows():
                if row['parametro'] == 'saldo_inicial': st.session_state.opening_balance = float(row['valor'])
                if row['parametro'] == 'reserva': st.session_state.strategic_reserve = float(row['valor'])
                if row['parametro'] == 'investimento': st.session_state.investments = float(row['valor'])
                if row['parametro'] == 'sonhos': st.session_state.dreams = float(row['valor'])
except:
    pass

# --- INTERFACE ---
st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

if st.session_state.show_anim and lottie_success:
    st_lottie(lottie_success, height=80, speed=1.8, key="success_anim")
    time.sleep(0.8)
    st.session_state.show_anim = False
    st.rerun()

# --- NAVEGAÇÃO ENTRE ETAPAS ---

# PASSO 0: LIQUIDEZ
if st.session_state.step == 0:
    st.markdown('<p class="setup-step">01_CONFIGURAÇÃO DE CAIXA</p>', unsafe_allow_html=True)
    v_total = st.number_input("SALDO TOTAL HOJE", min_value=0.0, format="%.2f", value=st.session_state.opening_balance)
    v_reserva = st.number_input("RESERVA ESTRATÉGICA", min_value=0.0, format="%.2f", value=st.session_state.strategic_reserve)
    if st.button("CONFIRMAR ESTRATÉGIA"):
        st.session_state.opening_balance, st.session_state.strategic_reserve = v_total, v_reserva
        st.session_state.step = 1; st.session_state.show_anim = True; st.rerun()

# PASSO 1: ENTRADAS
elif st.session_state.step == 1:
    # Botão Voltar
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← VOLTAR PARA LIQUIDEZ"):
        st.session_state.step = 0; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    total_in = sum(i['val'] for i in st.session_state.incomes)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">02_FLUXO DE ENTRADAS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_in)}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc, val, date = col1.text_input("NOME"), col2.number_input("VALOR", format="%.2f"), col3.number_input("DIA", 1, 31, 15)
    if st.button("ADICIONAR RECEITA"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date}); st.rerun()
    
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{i['desc']}** • {format_br(i['val'])} (Dia {i['date']})")
        if cl2.button("✕", key=f"d_inc_{idx}"): st.session_state.incomes.pop(idx); st.rerun()
    
    if len(st.session_state.incomes) > 0 and st.button("AVANÇAR PARA CUSTOS FIXOS"):
        st.session_state.step = 2; st.session_state.show_anim = True; st.rerun()

# PASSO 2: CUSTOS
elif st.session_state.step == 2:
    # Botão Voltar
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← VOLTAR PARA ENTRADAS"):
        st.session_state.step = 1; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    total_out = sum(e['val'] for e in st.session_state.expenses)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">03_CUSTOS FIXOS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_out)}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc, val, date = col1.text_input("ITEM"), col2.number_input("VALOR", format="%.2f"), col3.number_input("DIA", 1, 31, 5)
    if st.button("ADICIONAR CUSTO"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date}); st.rerun()
    
    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{e['desc']}** • {format_br(e['val'])} (Dia {e['date']})")
        if cl2.button("✕", key=f"d_exp_{idx}"): st.session_state.expenses.pop(idx); st.rerun()
    
    if len(st.session_state.expenses) > 0 and st.button("AVANÇAR PARA ALOCAÇÃO"):
        st.session_state.step = 3; st.session_state.show_anim = True; st.rerun()

# PASSO 3: ALOCAÇÃO
elif st.session_state.step == 3:
    # Botão Voltar
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← VOLTAR PARA CUSTOS FIXOS"):
        st.session_state.step = 2; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="setup-step">04_ALOCAÇÃO DE CAPITAL</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTOS MENSAL", min_value=0.0, format="%.2f", value=st.session_state.investments)
    drm = st.number_input("SONHOS / LIFESTYLE", min_value=0.0, format="%.2f", value=st.session_state.dreams)
    
    if st.button("SALVAR ESTRATÉGIA NO COFRE"):
        st.session_state.investments, st.session_state.dreams = inv, drm
        try:
            config_df = pd.DataFrame([
                {"parametro": "saldo_inicial", "valor": st.session_state.opening_balance},
                {"parametro": "reserva", "valor": st.session_state.strategic_reserve},
                {"parametro": "investimento", "valor": st.session_state.investments},
                {"parametro": "sonhos", "valor": st.session_state.dreams}
            ])
            conn.update(worksheet="Config", data=config_df)
        except: pass
        st.session_state.step = 4; st.session_state.show_anim = True; st.rerun()

# PASSO 4: DASHBOARD
elif st.session_state.step == 4:
    st.markdown('<p class="setup-step">VISÃO ANALÍTICA CFO.</p>', unsafe_allow_html=True)
    
    dias = np.arange(1, 32)
    saldo_diario = []
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in saldo_diario]))
    fig.add_hline(y=st.session_state.strategic_reserve/1000, line_dash="dash", line_color="#CCC", line_width=1)
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(showgrid=False, tickfont=dict(size=9, color='#AAA')),
                      yaxis=dict(gridcolor='#F9F9F9', tickformat='.0f', tickfont=dict(size=9, color='#AAA'), ticksuffix='k'),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    t_in, t_out = sum(i['val'] for i in st.session_state.incomes), sum(e['val'] for e in st.session_state.expenses)
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + t_in) - t_out - st.session_state.investments - st.session_state.dreams
    
    st.markdown(f'<div class="card"><p class="metric-label">Capital Operacional</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card"><p class="metric-label">Cota Diária</p><p class="metric-value">{format_br(max(livre/30, 0))[:-3]}</p></div>', unsafe_allow_html=True)

    with st.expander("DETALHAMENTO E AUDITORIA", expanded=False):
        audit_html = f"""
        <div style="font-size: 11px; color: #666; font-family: 'Inter'; letter-spacing: 0.5px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(+) SALDO INICIAL</span><span>{format_br(st.session_state.opening_balance)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(-) RESERVA BLINDADA</span><span>{format_br(st.session_state.strategic_reserve)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(+) TOTAL RECEITAS</span><span>{format_br(t_in)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(-) CUSTOS FIXOS</span><span>{format_br(t_out)}</span></div>
            <div style="display: flex; justify-content: space-between; padding: 10px 0; color: #000; font-weight: 800; border-top: 1px solid #000;"><span>LIQUIDEZ OPERACIONAL</span><span>{format_br(livre)}</span></div>
        </div>
        """
        st.markdown(audit_html, unsafe_allow_html=True)

    if st.button("REDEFINIR ESTRATÉGIA"):
        st.session_state.step = 0; st.rerun()
