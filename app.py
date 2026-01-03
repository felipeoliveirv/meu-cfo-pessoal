import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# --- ESTÉTICA PERFORMANCE TERMINAL (RUNWAY / APPLE / SATISFY) ---
st.set_page_config(page_title="RUNWAY | CFO Pessoal", layout="centered")

# Função Segura para carregar animações
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# Carregamento sutil de checkmark
lottie_success = load_lottieurl("https://lottie.host/5a2d67a1-94a3-4886-905c-5912389d4d03/GjX1Xl9T8y.json")

# Função de Formatação Brasileira (Ex: 13.000,00)
def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #FFFFFF; 
        color: #000; 
    }

    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 3px; font-size: 10px;
        transition: 0.3s ease;
    }
    .stButton>button:hover { background-color: #333 !important; }

    .stNumberInput input, .stTextInput input {
        border: none !important;
        border-bottom: 1px solid #000 !important;
        border-radius: 0px !important;
        background-color: transparent !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 9px; color: #999; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-value { font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -2px; line-height: 1; }
    .card { padding: 25px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE & ESTADO ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'show_anim']
for key in keys:
    if key not in st.session_state:
        if key == 'step': st.session_state[key] = 0
        elif key in ['incomes', 'expenses']: st.session_state[key] = []
        elif key == 'show_anim': st.session_state[key] = False
        else: st.session_state[key] = 0.0

# --- HEADER ---
st.markdown('<p class="brand-header">RUNWAY</p>', unsafe_allow_html=True)

# --- MICRO-ANIMAÇÃO (CONTROLE DE ERRO) ---
if st.session_state.show_anim:
    if lottie_success:
        st_lottie(lottie_success, height=80, speed=1.5, key="success_anim")
        time.sleep(0.8)
    st.session_state.show_anim = False
    st.rerun()

# --- ETAPAS ---
if st.session_state.step == 0:
    st.markdown('<p class="setup-step">01_CONFIGURAÇÃO DE CAIXA</p>', unsafe_allow_html=True)
    val_total = st.number_input("SALDO ATUAL EM CONTA", min_value=0.0, format="%.2f")
    val_reserva = st.number_input("RESERVA ESTRATÉGICA", min_value=0.0, format="%.2f")
    if st.button("CONFIRMAR ESTRATÉGIA"):
        st.session_state.opening_balance, st.session_state.strategic_reserve = val_total, val_reserva
        st.session_state.step = 1
        st.session_state.show_anim = True
        st.rerun()

elif st.session_state.step == 1:
    total_in = sum(i['val'] for i in st.session_state.incomes)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">02_ENTRADAS PREVISTAS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_in)}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("NOME DA RECEITA", placeholder="Ex: Salário")
    val = col2.number_input("VALOR", format="%.2f")
    date = col3.number_input("DIA", 1, 31, 15)
    if st.button("ADICIONAR RECEITA"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date})
        st.rerun()
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{i['desc']}** • {format_br(i['val'])} (Dia {i['date']})")
        if cl2.button("✕", key=f"d_inc_{idx}"): st.session_state.incomes.pop(idx); st.rerun()
    if len(st.session_state.incomes) > 0 and st.button("AVANÇAR PARA CUSTOS FIXOS"):
        st.session_state.step = 2; st.session_state.show_anim = True; st.rerun()

elif st.session_state.step == 2:
    total_out = sum(e['val'] for e in st.session_state.expenses)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">03_CUSTOS OPERACIONAIS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_out)}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("NOME DO CUSTO", placeholder="Ex: Aluguel")
    val = col2.number_input("VALOR", format="%.2f")
    date = col3.number_input("DIA", 1, 31, 5)
    if st.button("ADICIONAR CUSTO"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date})
        st.rerun()
    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{e['desc']}** • {format_br(e['val'])} (Dia {e['date']})")
        if cl2.button("✕", key=f"d_exp_{idx}"): st.session_state.expenses.pop(idx); st.rerun()
    if len(st.session_state.expenses) > 0 and st.button("AVANÇAR PARA ALOCAÇÃO"):
        st.session_state.step = 3; st.session_state.show_anim = True; st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-step">04_PROTEÇÃO E INVESTIMENTOS</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTO MENSAL", min_value=0.0, format="%.2f")
    drm = st.number_input("SONHOS / LIFESTYLE", min_value=0.0, format="%.2f")
    if st.button("FINALIZAR ESTRATÉGIA"):
        st.session_state.investments, st.session_state.dreams = inv, drm
        st.session_state.step = 4; st.session_state.show_anim = True; st.rerun()

# --- DASHBOARD ---
elif st.session_state.step == 4:
    st.markdown('<p class="setup-step">VISÃO ANALÍTICA CFO</p>', unsafe_allow_html=True)
    
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
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', 
                             line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in saldo_diario]))
    fig.add_hline(y=st.session_state.strategic_reserve/1000, line_dash="dash", line_color="#CCC", line_width=1)
    
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(showgrid=False, tickfont=dict(size=9, color='#AAA')),
                      yaxis=dict(gridcolor='#F9F9F9', tickformat='.0f', tickfont=dict(size=9, color='#AAA'), ticksuffix='k'),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    t_in = sum(i['val'] for i in st.session_state.incomes)
    t_out = sum(e['val'] for e in st.session_state.expenses)
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
            <div style="display: flex; justify-content: space-between; padding: 12px 0; color: #000; font-weight: 800; border-top: 1px solid #000;"><span>LIQUIDEZ LÍQUIDA</span><span>{format_br(livre)}</span></div>
        </div>
        """
        st.markdown(audit_html, unsafe_allow_html=True)

    if st.button("REINICIAR ESTRATÉGIA"):
        st.session_state.step = 0; st.rerun()
