import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ESTÉTICA AVANÇADA ---
st.set_page_config(page_title="CFO Pessoal | Cashflow", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000000; }
    .stButton>button { width: 100%; background-color: #000000 !important; color: #FFFFFF !important; border-radius: 4px; padding: 12px; font-weight: 600; border: none; margin-top: 10px; }
    .setup-title { font-size: 28px; font-weight: 800; letter-spacing: -1px; text-transform: uppercase; margin-bottom: 5px; }
    .setup-subtitle { font-size: 14px; color: #666; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
    .card { background-color: #F9F9F9; padding: 20px; border-radius: 8px; border: 1px solid #EEE; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'incomes' not in st.session_state: st.session_state.incomes = []
if 'expenses' not in st.session_state: st.session_state.expenses = []

# --- FUNÇÕES DE APOIO ---
def add_income(desc, val, date):
    st.session_state.incomes.append({"desc": desc, "val": val, "date": date})

def add_expense(desc, val, date):
    st.session_state.expenses.append({"desc": desc, "val": val, "date": date})

# --- FLUXO DE ONBOARDING ---

# PASSO 1: RECEITAS (CASH-IN)
if st.session_state.step == 1:
    st.markdown('<p class="setup-title">Cash-In Events</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Adicione suas fontes de receita e datas</p>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        desc = col1.text_input("Descrição", placeholder="Ex: Salário Parte 1", key="inc_desc")
        val = col2.number_input("Valor (R$)", min_value=0.0, step=100.0, key="inc_val")
        date = col3.number_input("Dia", min_value=1, max_value=31, step=1, key="inc_date")
        
        if st.button("＋ ADICIONAR RECEITA"):
            if val > 0:
                add_income(desc, val, date)
                st.rerun()

    # Lista o que já foi adicionado
    for i in st.session_state.incomes:
        st.markdown(f"**{i['desc']}**: R$ {i['val']:.2f} (Dia {i['date']})")
    
    if len(st.session_state.incomes) > 0:
        if st.button("PRÓXIMO: CUSTOS FIXOS"):
            st.session_state.step = 2
            st.rerun()

# PASSO 2: CUSTOS FIXOS (OPEX)
elif st.session_state.step == 2:
    st.markdown('<p class="setup-title">Fixed Outflows</p>', unsafe_allow_html=True)
    st.markdown('<p class="setup-subtitle">Seus compromissos recorrentes</p>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        desc = col1.text_input("Custo", placeholder="Ex: Aluguel", key="exp_desc")
        val = col2.number_input("Valor (R$)", min_value=0.0, step=100.0, key="exp_val")
        date = col3.number_input("Vencimento", min_value=1, max_value=31, step=1, key="exp_date")
        
        if st.button("＋ ADICIONAR CUSTO"):
            if val > 0:
                add_expense(desc, val, date)
                st.rerun()

    for e in st.session_state.expenses:
        st.markdown(f"**{e['desc']}**: R$ {e['val']:.2f} (Dia {e['date']})")

    if len(st.session_state.expenses) > 0:
        if st.button("FINALIZAR E GERAR PROJEÇÃO"):
            st.session_state.step = 3
            st.rerun()

# PASSO 3: DASHBOARD DE CASHFLOW
elif st.session_state.step == 3:
    st.markdown('<p class="setup-title">Performance Projection</p>', unsafe_allow_html=True)
    
    # Lógica de Cashflow Mensal
    dias = list(range(1, 32))
    saldo_diario = []
    saldo_atual = 0
    
    for dia in dias:
        # Soma entradas do dia
        for inc in st.session_state.incomes:
            if inc['date'] == dia: saldo_atual += inc['val']
        # Subtrai saídas do dia
        for exp in st.session_state.expenses:
            if exp['date'] == dia: saldo_atual -= exp['val']
        
        saldo_diario.append(saldo_atual)

    # Gráfico Minimalista (Plotly)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=saldo_diario, mode='lines', fill='tozeroy', 
                             line=dict(color='black', width=2),
                             fillcolor='rgba(0,0,0,0.05)'))
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, title="Dia do Mês"),
        yaxis=dict(showgrid=True, gridcolor='#EEE', title="Saldo (R$)"),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # KPI de Safe-to-Spend
    total_in = sum(i['val'] for i in st.session_state.incomes)
    total_out = sum(e['val'] for e in st.session_state.expenses)
    disponivel = total_in - total_out
    
    st.markdown(f"""
        <div class="card">
            <p style="font-size: 11px; color: #888; letter-spacing: 1px;">DISPONÍVEL PARA VARIÁVEIS</p>
            <p style="font-size: 36px; font-weight: 800; margin:0;">R$ {disponivel:,.2f}</p>
            <p style="font-size: 14px; color: #333;">Cota Diária: <b>R$ {disponivel/30:,.2f}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("RESETAR CONFIGURAÇÃO"):
        st.session_state.clear()
        st.rerun()
