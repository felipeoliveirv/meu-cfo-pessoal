import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- ESTÉTICA PERFORMANCE TERMINAL (Apple/Satisfy/247) ---
st.set_page_config(page_title="CFO Pessoal v7", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    .stButton>button { width: 100%; background-color: #000 !important; color: #FFF !important; border-radius: 4px; padding: 12px; font-weight: 600; border: none; }
    .setup-title { font-size: 26px; font-weight: 800; letter-spacing: -1.2px; text-transform: uppercase; margin: 0; }
    .total-badge { font-size: 20px; font-weight: 800; color: #000; text-align: right; }
    .card { background-color: #FBFBFB; padding: 20px; border-radius: 12px; border: 1px solid #F0F0F0; }
    .metric-label { font-size: 10px; color: #888; letter-spacing: 1px; text-transform: uppercase; }
    .metric-value { font-size: 32px; font-weight: 800; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO APP ---
for key in ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams']:
    if key not in st.session_state:
        if key == 'step': st.session_state[key] = 0
        elif key in ['incomes', 'expenses']: st.session_state[key] = []
        else: st.session_state[key] = 0.0

# --- FLUXO ONBOARDING ---

# PASSO 0: SALDO E RESERVA
if st.session_state.step == 0:
    st.markdown('<p class="setup-title">Liquidez Inicial</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#888; font-size:13px; margin-bottom:20px;">DEFINA O SEU PONTO DE PARTIDA</p>', unsafe_allow_html=True)
    
    with st.expander("💡 ENTENDA A ESTRATÉGIA"):
        st.write("**Saldo Total:** O capital bruto disponível hoje. \n\n**Reserva:** O valor que você deseja 'blindar'. O app não contará esse valor para seus gastos diários, protegendo seu patrimônio.")

    val_total = st.number_input("Saldo Bruto em Conta (R$)", min_value=0.0, step=500.0, format="%.2f")
    val_reserva = st.number_input("Reserva Estratégica (R$)", min_value=0.0, step=500.0, format="%.2f")
    
    if st.button("PRÓXIMO: ENTRADAS"):
        st.session_state.opening_balance = val_total
        st.session_state.strategic_reserve = val_reserva
        st.session_state.step = 1; st.rerun()

# PASSO 1: CASH-IN
elif st.session_state.step == 1:
    total_inc = sum(i['val'] for i in st.session_state.incomes)
    c1, c2 = st.columns([1.5, 1])
    c1.markdown('<p class="setup-title">Cash-In</p>', unsafe_allow_html=True)
    c2.markdown(f'<p class="total-badge">{total_inc/1000:.1f}k</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("Origem", placeholder="Ex: Salário", key="inc_desc")
    val = col2.number_input("Valor", min_value=0.0, step=100.0, key="inc_val")
    date = col3.number_input("Dia", 1, 31, 15, key="inc_date")
    
    if st.button("＋ ADICIONAR"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date})
        st.rerun()
    
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1])
        cl1.text(f"✓ {i['desc']}: R$ {i['val']:.2f} (Dia {i['date']})")
        if cl2.button("✕", key=f"d_inc_{idx}"):
            st.session_state.incomes.pop(idx); st.rerun()

    if len(st.session_state.incomes) > 0 and st.button("PRÓXIMO: CUSTOS FIXOS"):
        st.session_state.step = 2; st.rerun()

# PASSO 2: CUSTOS FIXOS
elif st.session_state.step == 2:
    total_exp = sum(e['val'] for e in st.session_state.expenses)
    c1, c2 = st.columns([1.5, 1])
    c1.markdown('<p class="setup-title">Fixed Costs</p>', unsafe_allow_html=True)
    c2.markdown(f'<p class="total-badge">{total_exp/1000:.1f}k</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("Item", placeholder="Ex: Aluguel", key="exp_desc")
    val = col2.number_input("Valor", min_value=0.0, step=100.0, key="exp_val")
    date = col3.number_input("Dia", 1, 31, 5, key="exp_date")
    
    if st.button("＋ ADICIONAR"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date})
        st.rerun()

    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1])
        cl1.text(f"✗ {e['desc']}: R$ {e['val']:.2f} (Dia {e['date']})")
        if cl2.button("✕", key=f"d_exp_{idx}"):
            st.session_state.expenses.pop(idx); st.rerun()

    if len(st.session_state.expenses) > 0 and st.button("PRÓXIMO: ALOCAÇÃO"):
        st.session_state.step = 3; st.rerun()

# PASSO 3: ALOCAÇÃO FINAL
elif st.session_state.step == 3:
    st.markdown('<p class="setup-title">Capital Allocation</p>', unsafe_allow_html=True)
    inv = st.number_input("Aporte em Investimentos (R$)", min_value=0.0, step=100.0)
    drm = st.number_input("Provisão para Sonhos (R$)", min_value=0.0, step=100.0)
    if st.button("FINALIZAR DASHBOARD"):
        st.session_state.investments = inv
        st.session_state.dreams = drm
        st.session_state.step = 4; st.rerun()

# PASSO 4: DASHBOARD ANALYTICS
elif st.session_state.step == 4:
    st.markdown('<p class="setup-title">CFO Insight</p>', unsafe_allow_html=True)
    
    # Lógica de Dados
    dias = np.arange(1, 32)
    saldo_diario = []
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams
    
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # GRÁFICO PERFORMANCE (R$ k format)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=saldo_diario, mode='lines', line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: R$ %{y:,.2f}<extra></extra>'))
    fig.add_hline(y=st.session_state.strategic_reserve, line_dash="dash", line_color="#888")
    
    # Área de Performance (Color Fill)
    fig.add_trace(go.Scatter(x=dias, y=[max(x, st.session_state.strategic_reserve) for x in saldo_diario], fill='tonexty', 
                             fillcolor='rgba(0, 200, 100, 0.05)', line=dict(width=0), showlegend=False))

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', height=350, margin=dict(l=0, r=10, t=20, b=0),
        xaxis=dict(showgrid=False, title="Timeline Mensal"),
        yaxis=dict(gridcolor='#F0F0F0', ticksuffix='k', tickformat='.1f', 
                   # Transforma 12000 em 12.0k
                   tickvals=np.arange(min(saldo_diario)-1000, max(saldo_diario)+2000, 2000),
                   ticktext=[f"{v/1000:.1f}k" for v in np.arange(min(saldo_diario)-1000, max(saldo_diario)+2000, 2000)])
    )
    st.plotly_chart(fig, use_container_width=True)

    # INDICADORES PRINCIPAIS
    total_in = sum(i['val'] for i in st.session_state.incomes)
    total_out = sum(e['val'] for e in st.session_state.expenses)
    livre_operacional = (st.session_state.opening_balance - st.session_state.strategic_reserve + total_in) - total_out - st.session_state.investments - st.session_state.dreams
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="card"><p class="metric-label">Capital Operacional 💡</p><p class="metric-value">R$ {livre_operacional/1000:.1f}k</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="card"><p class="metric-label">Cota Diária 💡</p><p class="metric-value">R$ {max(livre_operacional/30, 0):.0f}</p></div>', unsafe_allow_html=True)

    # DRILL-DOWN: COMPOSIÇÃO DOS NÚMEROS
    with st.expander("🔍 VER DETALHAMENTO DO FLUXO (AUDIT)"):
        st.write("Entenda como chegamos ao seu Capital Operacional:")
        audit_data = {
            "Item": ["(+) Saldo Bruto Inicial", "(-) Reserva Estratégica", "(+) Total de Entradas", "(-) Custos Fixos", "(-) Alocação (Invest/Sonhos)"],
            "Valor": [f"R$ {st.session_state.opening_balance:,.2f}", f"- R$ {st.session_state.strategic_reserve:,.2f}", f"+ R$ {total_in:,.2f}", f"- R$ {total_out:,.2f}", f"- R$ {st.session_state.investments + st.session_state.dreams:,.2f}"]
        }
        st.table(pd.DataFrame(audit_data))
        st.markdown(f"**RESULTADO FINAL: R$ {livre_operacional:,.2f}**")

    if st.button("REINICIAR ESTRATÉGIA"):
        st.session_state.step = 0; st.rerun()
