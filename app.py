import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO CFO. ---
st.set_page_config(page_title="CFO. | Operação", layout="centered")

def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# --- CSS PRECISÃO V51.0 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 2px; font-size: 11px;
    }

    /* Botão de Voltar Discreto */
    div[data-testid="stColumn"]:nth-child(1) .stButton>button {
        background-color: transparent !important; color: #BBB !important;
        border: 1px solid #EEE !important; font-size: 16px !important;
    }
    div[data-testid="stColumn"]:nth-child(1) .stButton>button:hover {
        color: #000 !important; border-color: #000 !important;
    }

    .stNumberInput input, .stTextInput input {
        border: none !important; border-bottom: 1px solid #000 !important;
        border-radius: 0px !important; font-size: 24px !important; font-weight: 800 !important;
    }
    
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 36px; font-weight: 800; margin-top: 5px; letter-spacing: normal; line-height: 1.1; color: #000; display: block; }
    
    .sec-label { font-size: 9px; color: #BBB; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; }
    .sec-value { font-size: 22px; font-weight: 700; color: #444; margin-top: 2px; }
    
    .audit-card { background: #F9F9F9; padding: 15px; border-left: 3px solid #000; margin-bottom: 5px; font-size: 12px; }
    .card { padding: 25px 0; border-bottom: 1px solid #EEE; margin-bottom: 5px; }
    .card-sec { padding: 15px 0; border-bottom: 1px solid #F5F5F5; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'installments', 'reset_mode']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses', 'installments'] else (0 if key == 'step' else 0.0)

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

if st.session_state.step == 0 and not st.session_state.reset_mode:
    try:
        config_df = conn.read(worksheet="Config", ttl=0)
        if not config_df.empty:
            for _, row in config_df.iterrows():
                if row['parametro'] == 'saldo_inicial': st.session_state.opening_balance = float(row['valor'])
                if row['parametro'] == 'reserva': st.session_state.strategic_reserve = float(row['valor'])
                if row['parametro'] == 'investimento': st.session_state.investments = float(row['valor'])
                if row['parametro'] == 'sonhos': st.session_state.dreams = float(row['valor'])
            st.session_state.incomes = conn.read(worksheet="Receitas", ttl=0).to_dict('records')
            st.session_state.expenses = conn.read(worksheet="Custos", ttl=0).to_dict('records')
            try: st.session_state.installments = conn.read(worksheet="Parcelas", ttl=0).to_dict('records')
            except: pass
            st.session_state.step = 4
    except: pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

# --- FLUXO DE REVISÃO/CONFIGURAÇÃO ---

if st.session_state.step == 0:
    st.markdown('<p class="setup-step">Revisão 01/04</p>', unsafe_allow_html=True)
    st.markdown('### Qual seu saldo bancário atual?')
    val = st.number_input("R$ Saldo Atual", value=st.session_state.opening_balance, step=100.0, label_visibility="collapsed")
    if st.button("PRÓXIMO"):
        st.session_state.opening_balance = val
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.markdown('<p class="setup-step">Revisão 02/04</p>', unsafe_allow_html=True)
    st.markdown('### Reservas e Investimentos')
    res = st.number_input("Reserva Blindada", value=st.session_state.strategic_reserve, step=100.0)
    inv = st.number_input("Investimentos do Mês", value=st.session_state.investments, step=100.0)
    drm = st.number_input("Reserva para Sonhos", value=st.session_state.dreams, step=100.0)
    
    c_btn1, c_btn2 = st.columns([0.2, 0.8])
    if c_btn1.button("←", key="back_0"):
        st.session_state.step = 0
        st.rerun()
    if c_btn2.button("PRÓXIMO"):
        st.session_state.strategic_reserve = res
        st.session_state.investments = inv
        st.session_state.dreams = drm
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.markdown('<p class="setup-step">Revisão 03/04</p>', unsafe_allow_html=True)
    st.markdown('### Receitas do Mês')
    with st.form("form_incomes", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        desc = c1.text_input("Nova Receita")
        valor = c2.number_input("Valor", min_value=0.0, step=100.0)
        if st.form_submit_button("ADICIONAR"):
            st.session_state.incomes.append({"desc": desc, "val": valor})
            st.rerun()
    
    for idx, i in enumerate(st.session_state.incomes):
        col_i1, col_i2 = st.columns([0.9, 0.1])
        col_i1.write(f"✅ {i['desc']}: {format_br(i['val'])}")
        if col_i2.button("✕", key=f"del_inc_{idx}"):
            st.session_state.incomes.pop(idx)
            st.rerun()
    
    st.markdown("---")
    c_btn1, c_btn2 = st.columns([0.2, 0.8])
    if c_btn1.button("←", key="back_1"):
        st.session_state.step = 1
        st.rerun()
    if c_btn2.button("PRÓXIMO"):
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-step">Revisão 04/04</p>', unsafe_allow_html=True)
    st.markdown('### Custos Fixos')
    with st.form("form_expenses", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        desc = c1.text_input("Novo Custo")
        valor = c2.number_input("Valor", min_value=0.0, step=100.0)
        if st.form_submit_button("ADICIONAR"):
            st.session_state.expenses.append({"desc": desc, "val": valor})
            st.rerun()
    
    for idx, e in enumerate(st.session_state.expenses):
        col_e1, col_e2 = st.columns([0.9, 0.1])
        col_e1.write(f"❌ {e['desc']}: {format_br(e['val'])}")
        if col_e2.button("✕", key=f"del_exp_{idx}"):
            st.session_state.expenses.pop(idx)
            st.rerun()
    
    st.markdown("---")
    c_btn1, c_btn2 = st.columns([0.2, 0.8])
    if c_btn1.button("←", key="back_2"):
        st.session_state.step = 2
        st.rerun()
    if c_btn2.button("FINALIZAR REVISÃO"):
        config_data = pd.DataFrame([
            {"parametro": "saldo_inicial", "valor": st.session_state.opening_balance},
            {"parametro": "reserva", "valor": st.session_state.strategic_reserve},
            {"parametro": "investimento", "valor": st.session_state.investments},
            {"parametro": "sonhos", "valor": st.session_state.dreams}
        ])
        conn.update(worksheet="Config", data=config_data)
        conn.update(worksheet="Receitas", data=pd.DataFrame(st.session_state.incomes))
        conn.update(worksheet="Custos", data=pd.DataFrame(st.session_state.expenses))
        st.session_state.step = 4
        st.rerun()

# --- DASHBOARD ---

elif st.session_state.step == 4:
    agora_br = datetime.now() - timedelta(hours=3)
    hoje_str = agora_br.strftime("%d/%m/%Y")
    
    try:
        df_l = conn.read(worksheet="Lancamentos", ttl=0)
        df_l['valor'] = pd.to_numeric(df_l['valor'], errors='coerce').fillna(0)
        g_tot = df_l['valor'].sum()
        g_hj = df_l[df_l['data'].str.contains(hoje_str, na=False)]['valor'].sum()
    except: g_tot, g_hj = 0.0, 0.0

    valor_parcelas_mes = 0.0
    for p in st.session_state.installments:
        try:
            meses_decorridos = (agora_br.year - int(p['ano_inicio'])) * 12 + (agora_br.month - int(p['mes_inicio']))
            if 0 <= meses_decorridos < int(p['parcelas']):
                valor_parcelas_mes += float(p['valor_total']) / int(p['parcelas'])
        except: pass

    d_rest = max(31 - agora_br.day, 1)
    ti, to = sum(i['val'] for i in st.session_state.incomes), sum(e['val'] for e in st.session_state.expenses)
    
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + ti) - to - st.session_state.investments - st.session_state.dreams - g_tot - valor_parcelas_mes
    ct_h = ((livre + g_hj) / (d_rest + 1)) - g_hj
    disponivel_total = livre + g_tot

    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<div class="card"><p class="metric-label">Operacional Restante</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="card"><p class="metric-label">Cota Restante (Hoje)</p><p class="metric-value">{format_br(ct_h)}</p></div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="card-sec"><p class="sec-label">Cota (Amanhã)</p><p class="sec-value">{format_br(livre / d_rest if d_rest > 0 else 0)}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-sec"><p class="sec-label">Fatura Atual (Cartão)</p><p class="sec-value">{format_br(valor_parcelas_mes)}</p></div>', unsafe_allow_html=True)

    st.markdown('<p class="metric-label" style="margin-top:25px;">Projeção de Consumo Operacional</p>', unsafe_allow_html=True)
    dias_mes = list(range(1, 32))
    projecao_sobra = [disponivel_total - (disponivel_total/30 * (d-1)) for d in dias_mes]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias_mes, y=projecao_sobra, fill='tozeroy', mode='lines', name='Meta', line=dict(color='#F0F0F0', width=0.5), fillcolor='rgba(240, 240, 240, 0.5)', hovertemplate='Sobra Sugerida: R$ %{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(x=[agora_br.day], y=[livre], name='Sobra Real', marker_color='#000000', width=0.7, hovertemplate='Sobra Real: R$ %{y:,.2f}<br>Dia: %{x}<extra></extra>'))
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#999'), tickvals=[1, 5, 10, 15, 20, 25, 30]), yaxis=dict(showgrid=True, gridcolor='#F5F5F5', tickfont=dict(size=10, color='#999'), tickprefix="R$ "))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with st.expander("🔍 AUDITORIA DE FLUXO", expanded=False):
        st.markdown(f"""
        <div class="audit-card">💰 <b>Saldo Inicial:</b> {format_br(st.session_state.opening_balance)}</div>
        <div class="audit-card">🛡️ <b>Reserva Blindada:</b> - {format_br(st.session_state.strategic_reserve)}</div>
        <div class="audit-card">📈 <b>Receitas Previstas:</b> + {format_br(ti)}</div>
        <div class="audit-card">📉 <b>Custos Fixos:</b> - {format_br(to)}</div>
        <div class="audit-card">💳 <b>Fatura Estimada:</b> - {format_br(valor_parcelas_mes)}</div>
        <div class="audit-card" style="background:#000; color:#FFF;"><b>DISPONÍVEL TOTAL:</b> {format_br(disponivel_total)}</div>
        """, unsafe_allow_html=True)

    with st.expander("💳 GESTÃO DE PARCELAMENTOS", expanded=False):
        c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
        p_d = c_p1.text_input("DESCRIÇÃO COMPRA")
        p_v = c_p2.number_input("VALOR TOTAL", min_value=0.0, key="p_val")
        p_n = c_p3.number_input("Nº PARCELAS", 1, 48, 12, key="p_num")
        if st.button("REGISTRAR PARCELAMENTO"):
            st.session_state.installments.append({"descricao": p_d, "valor_total": p_v, "parcelas": p_n, "mes_inicio": agora_br.month, "ano_inicio": agora_br.year})
            conn.update(worksheet="Parcelas", data=pd.DataFrame(st.session_state.installments))
            st.rerun()

    with st.expander("📝 REGISTRAR OU EDITAR GASTOS", expanded=False):
        c_l1, c_l2 = st.columns([2, 1])
        l_d, l_v = c_l1.text_input("DESCRIÇÃO GASTO"), c_l2.number_input("VALOR GASTO", min_value=0.0, key="g_val")
        if st.button("LANÇAR GASTO"):
            st.cache_data.clear()
            f_l = conn.read(worksheet="Lancamentos", ttl=0)
            n_e = pd.DataFrame([{"data": agora_br.strftime("%d/%m/%Y %H:%M"), "descricao": l_d, "valor": l_v}])
            final = pd.concat([f_l, n_e], ignore_index=True) if not f_l.empty else n_e
            conn.update(worksheet="Lancamentos", data=final)
            st.rerun()

    if st.button("REDEFINIR ESTRATÉGIA"):
        st.session_state.step = 0
        st.session_state.reset_mode = True
        st.rerun()
