import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- ESTÉTICA PERFORMANCE UTILITY (247 / SATISFY / APPLE) ---
st.set_page_config(page_title="CFO Pessoal v11", layout="centered")

def format_br(val):
    return f"R$ {val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #FFFFFF; 
        color: #000; 
    }

    /* Botão Principal: Estética Brutalista Clean */
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 3px; font-size: 10px;
        transition: 0.2s;
    }
    .stButton>button:hover { background-color: #333 !important; }

    /* Inputs: Ghost UI Style */
    .stNumberInput input, .stTextInput input {
        border: none !important;
        border-bottom: 1px solid #000 !important;
        border-radius: 0px !important;
        background-color: transparent !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        padding-left: 0px !important;
    }
    
    /* Typography Refinement */
    .setup-title { font-size: 20px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px; border-bottom: 2px solid #000; display: inline-block; }
    .metric-label { font-size: 9px; color: #999; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; }
    .metric-value { font-size: 34px; font-weight: 800; margin: 0; letter-spacing: -2px; line-height: 1; }
    
    /* Dashboard Cards */
    .card { padding: 25px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE & STATE ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# --- NAV & SCREENS ---
if st.session_state.step == 0:
    st.markdown('<p class="setup-title">01_Liquidez</p>', unsafe_allow_html=True)
    val_total = st.number_input("SALDO ATUAL BRUTO", min_value=0.0, format="%.2f", help="Total em custódia hoje.")
    val_reserva = st.number_input("RESERVA ESTRATÉGICA", min_value=0.0, format="%.2f", help="Patrimônio blindado.")
    if st.button("CONFIRM_STRATEGY"):
        st.session_state.opening_balance, st.session_state.strategic_reserve, st.session_state.step = val_total, val_reserva, 1
        st.rerun()

elif st.session_state.step == 1:
    st.markdown('<p class="setup-title">02_Cash_In</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("ORIGEM")
    val = col2.number_input("VALOR", format="%.2f")
    date = col3.number_input("DIA", 1, 31, 15)
    if st.button("LOG_INCOME"):
        st.session_state.incomes.append({"desc": desc, "val": val, "date": date}); st.rerun()
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{i['desc']}** • {format_br(i['val'])} (Dia {i['date']})")
        if cl2.button("✕", key=f"d_inc_{idx}"): st.session_state.incomes.pop(idx); st.rerun()
    if len(st.session_state.incomes) > 0:
        if st.button("NEXT_FIXED_COSTS"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.markdown('<p class="setup-title">03_Fixed_Costs</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    desc = col1.text_input("ITEM")
    val = col2.number_input("VALOR", format="%.2f")
    date = col3.number_input("DIA", 1, 31, 5)
    if st.button("LOG_EXPENSE"):
        st.session_state.expenses.append({"desc": desc, "val": val, "date": date}); st.rerun()
    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{e['desc']}** • {format_br(e['val'])} (Dia {e['date']})")
        if cl2.button("✕", key=f"d_exp_{idx}"): st.session_state.expenses.pop(idx); st.rerun()
    if len(st.session_state.expenses) > 0:
        if st.button("NEXT_ALLOCATION"): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-title">04_Allocation</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTOS MENSAL", min_value=0.0)
    drm = st.number_input("SONHOS / LIFESTYLE", min_value=0.0)
    if st.button("LAUNCH_DASHBOARD"):
        st.session_state.investments, st.session_state.dreams, st.session_state.step = inv, drm, 4; st.rerun()

# --- FINAL DASHBOARD ANALYTICS ---
elif st.session_state.step == 4:
    st.markdown('<p class="setup-title">CFO_Insight</p>', unsafe_allow_html=True)
    
    dias = np.arange(1, 32)
    saldo_diario = []
    current_cash = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams
    
    for dia in dias:
        for inc in st.session_state.incomes:
            if inc['date'] == dia: current_cash += inc['val']
        for exp in st.session_state.expenses:
            if exp['date'] == dia: current_cash -= exp['val']
        saldo_diario.append(current_cash)

    # GRÁFICO PERFORMANCE (ESTILO SATISFY)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in saldo_diario], mode='lines', 
                             line=dict(color='black', width=3),
                             hovertemplate='Dia %{x}<br>Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in saldo_diario]))
    
    reserva_k = st.session_state.strategic_reserve / 1000
    fig.add_hline(y=reserva_k, line_dash="dash", line_color="#CCC", line_width=1)
    
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color='#AAA')),
        yaxis=dict(gridcolor='#F9F9F9', ticksuffix='k', tickformat='.0f', tickfont=dict(size=9, color='#AAA')),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # INDICADORES ALPHA
    total_in = sum(i['val'] for i in st.session_state.incomes)
    total_out = sum(e['val'] for e in st.session_state.expenses)
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + total_in) - total_out - st.session_state.investments - st.session_state.dreams
    
    st.markdown(f'<div class="card"><p class="metric-label">Capital Operacional</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card"><p class="metric-label">Cota Diária</p><p class="metric-value">{format_br(max(livre/30, 0))[:-3]}</p></div>', unsafe_allow_html=True)

    with st.expander("DETAILS_AND_AUDIT", expanded=False):
        audit_html = f"""
        <div style="font-size: 11px; color: #666; font-family: 'Inter'; letter-spacing: 0.5px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 10px 0;"><span>(+) SALDO INICIAL</span><span>{format_br(st.session_state.opening_balance)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 10px 0;"><span>(-) RESERVA BLINDADA</span><span>{format_br(st.session_state.strategic_reserve)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 10px 0;"><span>(+) TOTAL RECEITAS</span><span>{format_br(total_inc)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 10px 0;"><span>(-) CUSTOS FIXOS</span><span>{format_br(total_out)}</span></div>
            <div style="display: flex; justify-content: space-between; padding: 10px 0; color: #000; font-weight: 800;"><span>NET_LIQUIDITY</span><span>{format_br(livre)}</span></div>
        </div>
        """
        st.markdown(audit_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("RESET_STRATEGY"):
        st.session_state.step = 0; st.rerun()
