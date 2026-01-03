import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- ESTÉTICA CFO PERFORMANCE ---
st.set_page_config(page_title="CFO Pessoal v4", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000000; }
    .stButton>button { width: 100%; background-color: #000000 !important; color: #FFFFFF !important; border-radius: 4px; padding: 12px; font-weight: 600; border: none; margin-top: 10px; }
    .setup-title { font-size: 28px; font-weight: 800; letter-spacing: -1.2px; text-transform: uppercase; margin-bottom: 5px; }
    .setup-subtitle { font-size: 13px; color: #888; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; }
    .card { background-color: #FBFBFB; padding: 25px; border-radius: 12px; border: 1px solid #F0F0F0; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO APP ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'opening_balance' not in st.session_state: st.session_state.opening_balance = 0.0
if 'strategic_reserve' not in st.session_state: st.session_state.strategic_reserve = 0.0
if 'incomes' not in st.session_state: st.session_state.incomes = []
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'investments' not in st.session_state: st.session_state.investments = 0.0
if 'dreams' not in st.session_state: st.session_state.dreams = 0.0

# --- FLUXO ONBOARDING ---

# PASSO 0: LIQUIDEZ E RESERVA
if st.session_state.step == 0:
    st.markdown('<p class="setup-title">Liquidez de Partida</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Separe o capital operacional da sua reserva</p>', unsafe_allow_html=True)
    val_total = st.number_input("Saldo Total em Conta (R$)", min_value=0.0, step=500.0, format="%.2f")
    val_reserva = st.number_input("Reserva Intocável / Economias (R$)", min_value=0.0, step=500.0, format="%.2f", help="Este valor não será usado para calcular sua cota diária.")
    
    if st.button("DEFINIR ESTRATÉGIA"):
        st.session_state.opening_balance = val_total
        st.session_state.strategic_reserve = val_reserva
        st.session_state.step = 1
        st.rerun()

# PASSO 1: RECEITAS
elif st.session_state.step == 1:
    st.markdown('<p class="setup-title">Cash-In</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Entradas previstas</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("Origem", placeholder="Salário", key="inc_desc")
    val = col2.number_input("Valor", min_value=0.0, step=100.0, key="inc_val")
    date = col3.number_input("Dia", 1, 31, 15, key="inc_date")
    if st.button("＋ ADICIONAR"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date})
        st.rerun()
    for i in st.session_state.incomes: st.text(f"✓ {i['desc']}: R$ {i['val']:.2f}")
    if len(st.session_state.incomes) > 0 and st.button("PRÓXIMO: CUSTOS"):
        st.session_state.step = 2
        st.rerun()

# PASSO 2: CUSTOS FIXOS
elif st.session_state.step == 2:
    st.markdown('<p class="setup-title">Fixed Outflows</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Seu ponto de equilíbrio</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("Custo", placeholder="Aluguel", key="exp_desc")
    val = col2.number_input("Valor", min_value=0.0, step=100.0, key="exp_val")
    date = col3.number_input("Dia", 1, 31, 5, key="exp_date")
    if st.button("＋ ADICIONAR"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date})
        st.rerun()
    for e in st.session_state.expenses: st.text(f"✗ {e['desc']}: R$ {e['val']:.2f}")
    if len(st.session_state.expenses) > 0 and st.button("PRÓXIMO: PROVISÕES"):
        st.session_state.step = 3
        st.rerun()

# PASSO 3: ALOCAÇÃO DE CAPITAL
elif st.session_state.step == 3:
    st.markdown('<p class="setup-title">Capital Allocation</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Novos aportes deste mês</p>', unsafe_allow_html=True)
    inv = st.number_input("Investir este mês (R$)", min_value=0.0, step=100.0)
    drm = st.number_input("Para Sonhos/Lifestyle (R$)", min_value=0.0, step=100.0)
    if st.button("GERAR DASHBOARD"):
        st.session_state.investments = inv
        st.session_state.dreams = drm
        st.session_state.step = 4
        st.rerun()

# PASSO 4: DASHBOARD
elif st.session_state.step == 4:
    st.markdown('<p class="setup-title">CFO Insight</p>', unsafe_allow_html=True)
    
    # Lógica de Projeção
    dias = np.arange(1, 32)
    saldo_diario = []
    # Saldo Operacional = Total - Reserva - Investimentos Novos - Sonhos Novos
    saldo_operacional = st.session_state.opening_balance - st.session_state.strategic_reserve - st.session_state.investments - st.session_state.dreams
    
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams
    
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # GRÁFICO PERFORMANCE
    fig = go.Figure()
    
    # Linha de Saldo Total
    fig.add_trace(go.Scatter(x=dias, y=saldo_diario, mode='lines', line=dict(color='black', width=3), name='Saldo Total'))
    
    # Linha de Reserva Estratégica (O limite que você não quer cruzar)
    fig.add_hline(y=st.session_state.strategic_reserve, line_dash="dash", line_color="#888", annotation_text="Reserva")

    # Pintura de áreas: Acima da reserva (Verde), Abaixo da reserva (Vermelho)
    fig.add_trace(go.Scatter(x=dias, y=[max(x, st.session_state.strategic_reserve) for x in saldo_diario], fill='tonexty', 
                             fillcolor='rgba(0, 200, 100, 0.1)', line=dict(width=0), showlegend=False))
    
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=350, margin=dict(l=0, r=0, t=20, b=0),
                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F0F0F0'))
    
    st.plotly_chart(fig, use_container_width=True)

    # CÁLCULO COTA DIÁRIA (Baseada apenas no que sobrou fora da reserva)
    total_in = sum(i['val'] for i in st.session_state.incomes)
    total_out = sum(e['val'] for e in st.session_state.expenses)
    livre_operacional = (st.session_state.opening_balance - st.session_state.strategic_reserve + total_in) - total_out - st.session_state.investments - st.session_state.dreams
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="card"><p style="font-size:10px; color:#888;">CAPITAL OPERACIONAL</p><h3>R$ {livre_operacional:,.2f}</h3></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="card"><p style="font-size:10px; color:#888;">COTA DIÁRIA</p><h3>R$ {max(livre_operacional/30, 0):,.2f}</h3></div>', unsafe_allow_html=True)

    if st.button("RESET"):
        st.session_state.step = 0
        st.rerun()
