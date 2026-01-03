import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- ESTÉTICA PERFORMANCE TERMINAL (Apple/Satisfy/247) ---
st.set_page_config(page_title="CFO Pessoal v9", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    
    /* Botões */
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 2px; padding: 12px; font-weight: 600; border: none; 
        text-transform: uppercase; letter-spacing: 1px; font-size: 12px;
    }
    
    /* Títulos e Textos */
    .setup-title { font-size: 24px; font-weight: 800; letter-spacing: -1px; text-transform: uppercase; margin: 0; }
    .total-badge { font-size: 18px; font-weight: 800; color: #000; text-align: right; }
    
    /* Cards de Métricas */
    .card { background-color: #FBFBFB; padding: 20px; border-radius: 0px; border-bottom: 1px solid #000; margin-bottom: 15px; }
    .metric-label { font-size: 9px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -1px; }

    /* Tabela de Auditoria Estilo Invoice */
    .audit-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
    .audit-table tr { border-bottom: 1px solid #EEE; }
    .audit-table td { padding: 12px 0; }
    .audit-table .label { color: #888; text-transform: uppercase; letter-spacing: 1px; font-size: 10px; }
    .audit-table .value { text-align: right; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO APP ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# --- FLUXO ONBOARDING (ESTÉTICA REFINADA) ---
if st.session_state.step == 0:
    st.markdown('<p class="setup-title">Liquidez Inicial</p>', unsafe_allow_html=True)
    val_total = st.number_input("SALDO BRUTO (R$)", min_value=0.0, step=500.0, format="%.2f", help="Total em conta hoje.")
    val_reserva = st.number_input("RESERVA ESTRATÉGICA (R$)", min_value=0.0, step=500.0, format="%.2f", help="Capital blindado.")
    if st.button("DEFINIR ESTRATÉGIA"):
        st.session_state.opening_balance, st.session_state.strategic_reserve, st.session_state.step = val_total, val_reserva, 1
        st.rerun()

elif st.session_state.step == 1:
    total_inc = sum(i['val'] for i in st.session_state.incomes)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-title">Cash-In</p>', unsafe_allow_html=True)
    c2.markdown(f'<p class="total-badge">{total_inc/1000:.1f}k</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("ORIGEM", key="inc_desc")
    val = col2.number_input("VALOR", min_value=0.0, key="inc_val")
    date = col3.number_input("DIA", 1, 31, 15, key="inc_date")
    if st.button("＋ ADICIONAR"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date}); st.rerun()
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.text(f"✓ {i['desc']}: R$ {i['val']:.2f}"); 
        if cl2.button("✕", key=f"d_inc_{idx}"): st.session_state.incomes.pop(idx); st.rerun()
    if len(st.session_state.incomes) > 0 and st.button("PRÓXIMO: CUSTOS"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    total_exp = sum(e['val'] for e in st.session_state.expenses)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-title">Fixed Costs</p>', unsafe_allow_html=True)
    c2.markdown(f'<p class="total-badge">{total_exp/1000:.1f}k</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("ITEM", key="exp_desc")
    val = col2.number_input("VALOR", min_value=0.0, key="exp_val")
    date = col3.number_input("DIA", 1, 31, 5, key="exp_date")
    if st.button("＋ ADICIONAR"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date}); st.rerun()
    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.text(f"✗ {e['desc']}: R$ {e['val']:.2f}"); 
        if cl2.button("✕", key=f"d_exp_{idx}"): st.session_state.expenses.pop(idx); st.rerun()
    if len(st.session_state.expenses) > 0 and st.button("PRÓXIMO: ALOCAÇÃO"): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-title">Capital Allocation</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTOS (R$)", min_value=0.0)
    drm = st.number_input("SONHOS (R$)", min_value=0.0)
    if st.button("GERAR DASHBOARD"):
        st.session_state.investments, st.session_state.dreams, st.session_state.step = inv, drm, 4; st.rerun()

# --- DASHBOARD FINAL ---
elif st.session_state.step == 4:
    st.markdown('<p class="setup-title">CFO Insight</p>', unsafe_allow_html=True)
    
    dias = np.arange(1, 32)
    saldo_diario = []
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams
    
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # GRÁFICO (RECALIBRADO)
    fig = go.Figure()
    # Dividimos por 1000 apenas na exibição (y)
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', 
                             line=dict(color='black', width=2),
                             hovertemplate='Dia %{x}<br>Saldo: R$ %{customdata:,.2f}<extra></extra>',
                             customdata=saldo_diario))
    
    # Linha da Reserva (em k)
    reserva_k = st.session_state.strategic_reserve / 1000
    fig.add_hline(y=reserva_k, line_dash="dash", line_color="#CCC", line_width=1)
    
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', height=300, margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, title="Timeline", tickfont=dict(size=10, color='#888')),
        yaxis=dict(gridcolor='#F5F5F5', ticksuffix='k', tickformat='.1f', tickfont=dict(size=10, color='#888')),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # KPIS
    total_in = sum(i['val'] for i in st.session_state.incomes)
    total_out = sum(e['val'] for e in st.session_state.expenses)
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + total_in) - total_out - st.session_state.investments - st.session_state.dreams
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="card"><p class="metric-label">Capital Operacional</p><p class="metric-value">R$ {livre/1000:.1f}k</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="card"><p class="metric-label">Cota Diária</p><p class="metric-value">R$ {max(livre/30, 0):.0f}</p></div>', unsafe_allow_html=True)

    # AUDIT TRAIL (REINVENTADO)
    with st.expander("DETALHAMENTO ESTRATÉGICO"):
        html_table = f"""
        <table class="audit-table">
            <tr><td class="label">Saldo Bruto Inicial</td><td class="value">R$ {st.session_state.opening_balance:,.2f}</td></tr>
            <tr><td class="label">Reserva Blindada</td><td class="value">- R$ {st.session_state.strategic_reserve:,.2f}</td></tr>
            <tr><td class="label">Entradas Projetadas</td><td class="value">+ R$ {total_in:,.2f}</td></tr>
            <tr><td class="label">Custos Fixos</td><td class="value">- R$ {total_out:,.2f}</td></tr>
            <tr><td class="label">Alocações Futuras</td><td class="value">- R$ {st.session_state.investments + st.session_state.dreams:,.2f}</td></tr>
            <tr style="border-top: 2px solid #000;"><td class="label" style="color:#000; font-weight:800;">Líquido Operacional</td><td class="value" style="font-size:16px;">R$ {livre:,.2f}</td></tr>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)

    if st.button("REINICIAR"):
        st.session_state.step = 0; st.rerun()
