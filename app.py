import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime, timedelta

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

# --- CSS ULTRA-MINIMALISTA (NAV STEALTH SEM FUNDO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    
    /* Botão Principal Estilo CFO. */
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 2px; font-size: 11px;
    }

    /* Twin Arrows ULTRA-STEALTH (Puramente texto) */
    .nav-btn>div>button {
        background: transparent !important; 
        border: none !important; 
        box-shadow: none !important;
        color: #000 !important; 
        font-size: 32px !important; 
        width: auto !important;
        height: auto !important;
        padding: 0 12px !important; 
        margin: 0 !important; 
        line-height: 1 !important;
        transition: color 0.3s ease;
    }
    .nav-btn>div>button:hover, .nav-btn>div>button:active, .nav-btn>div>button:focus { 
        color: #888 !important; 
        background: transparent !important; 
        border: none !important;
        box-shadow: none !important;
    }

    .stNumberInput input, .stTextInput input {
        border: none !important; border-bottom: 1px solid #000 !important;
        border-radius: 0px !important; font-size: 18px !important; font-weight: 600 !important;
    }
    
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 38px; font-weight: 800; margin-top: 5px; letter-spacing: normal; line-height: 1.1; color: #000; display: block; }
    .card { padding: 30px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE ESTADO ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'show_anim', 'reset_mode']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# --- CARREGAMENTO INTEGRAL ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    if st.session_state.step == 0 and not st.session_state.reset_mode:
        config_df = conn.read(worksheet="Config", ttl=0)
        if not config_df.empty:
            for _, row in config_df.iterrows():
                if row['parametro'] == 'saldo_inicial': st.session_state.opening_balance = float(row['valor'])
                if row['parametro'] == 'reserva': st.session_state.strategic_reserve = float(row['valor'])
                if row['parametro'] == 'investimento': st.session_state.investments = float(row['valor'])
                if row['parametro'] == 'sonhos': st.session_state.dreams = float(row['valor'])
            
            inc_df = conn.read(worksheet="Receitas", ttl=0)
            if not inc_df.empty: st.session_state.incomes = inc_df.to_dict('records')
            
            exp_df = conn.read(worksheet="Custos", ttl=0)
            if not exp_df.empty: st.session_state.expenses = exp_df.to_dict('records')
            st.session_state.step = 4
except: pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

if st.session_state.show_anim and lottie_success:
    st_lottie(lottie_success, height=80, speed=1.8, key="success_anim")
    time.sleep(0.8)
    st.session_state.show_anim = False
    st.rerun()

# --- NAVEGAÇÃO TWIN ARROWS (ULTRA-STEALTH) ---
if 0 < st.session_state.step < 4:
    c_nav1, c_nav2, _ = st.columns([0.4, 0.4, 9.2])
    with c_nav1:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("←", key="prev"): st.session_state.step -= 1; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_nav2:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("→", key="next"): st.session_state.step += 1; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- SETUP STEPS ---
if st.session_state.step == 0:
    st.markdown('<p class="setup-step">01_LIQUIDEZ</p>', unsafe_allow_html=True)
    v_t = st.number_input("SALDO ATUAL", min_value=0.0, format="%.2f", value=st.session_state.opening_balance)
    v_r = st.number_input("RESERVA ESTRATÉGICA", min_value=0.0, format="%.2f", value=st.session_state.strategic_reserve)
    if st.button("CONFIRMAR E AVANÇAR"):
        st.session_state.opening_balance, st.session_state.strategic_reserve = v_t, v_r
        st.session_state.step = 1; st.session_state.reset_mode = False; st.rerun()

elif st.session_state.step == 1:
    total_in = sum(i['val'] for i in st.session_state.incomes)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">02_ENTRADAS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_in)}</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    d, v, dt = col1.text_input("NOME"), col2.number_input("VALOR", format="%.2f"), col3.number_input("DIA", 1, 31, 15)
    if st.button("ADICIONAR RECEITA"):
        st.session_state.incomes.append({"desc": d, "val": v, "date": dt}); st.rerun()
    for idx, i in enumerate(st.session_state.incomes):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{i['desc']}** • {format_br(i['val'])} (Dia {i['date']})");
        if cl2.button("✕", key=f"d_i_{idx}"): st.session_state.incomes.pop(idx); st.rerun()

elif st.session_state.step == 2:
    total_out = sum(e['val'] for e in st.session_state.expenses)
    c1, c2 = st.columns([2, 1])
    c1.markdown('<p class="setup-step">03_CUSTOS FIXOS</p>', unsafe_allow_html=True)
    c2.markdown(f'<p style="text-align:right; font-weight:800; font-size:12px;">{format_br(total_out)}</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    d, v, dt = col1.text_input("ITEM"), col2.number_input("VALOR", format="%.2f"), col3.number_input("DIA", 1, 31, 5)
    if st.button("ADICIONAR CUSTO"):
        st.session_state.expenses.append({"desc": d, "val": v, "date": dt}); st.rerun()
    for idx, e in enumerate(st.session_state.expenses):
        cl1, cl2 = st.columns([0.9, 0.1]); cl1.markdown(f"**{e['desc']}** • {format_br(e['val'])} (Dia {e['date']})");
        if cl2.button("✕", key=f"d_e_{idx}"): st.session_state.expenses.pop(idx); st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-step">04_ALOCAÇÃO</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTOS", format="%.2f", value=st.session_state.investments)
    drm = st.number_input("SONHOS", format="%.2f", value=st.session_state.dreams)
    if st.button("SALVAR E FINALIZAR SETUP"):
        st.session_state.investments, st.session_state.dreams = inv, drm
        with st.spinner("Gravando no cofre..."):
            try:
                df_c = pd.DataFrame([{"parametro": "saldo_inicial", "valor": st.session_state.opening_balance}, {"parametro": "reserva", "valor": st.session_state.strategic_reserve}, {"parametro": "investimento", "valor": st.session_state.investments}, {"parametro": "sonhos", "valor": st.session_state.dreams}])
                conn.update(worksheet="Config", data=df_c)
                if st.session_state.incomes: conn.update(worksheet="Receitas", data=pd.DataFrame(st.session_state.incomes))
                if st.session_state.expenses: conn.update(worksheet="Custos", data=pd.DataFrame(st.session_state.expenses))
                st.session_state.step = 4; st.session_state.show_anim = True; st.rerun()
            except: st.error("Erro na sincronização das abas.")

# --- DASHBOARD ---
elif st.session_state.step == 4:
    st.markdown('<p class="setup-step">VISÃO ANALÍTICA CFO.</p>', unsafe_allow_html=True)
    agora_br = datetime.now() - timedelta(hours=3) 
    hoje_str = agora_br.strftime("%d/%m/%Y")
    
    g_tot, g_hj = 0.0, 0.0
    try:
        df_l = conn.read(worksheet="Lancamentos", ttl=0)
        if not df_l.empty:
            df_l['valor'] = pd.to_numeric(df_l['valor'], errors='coerce').fillna(0)
            g_tot = df_l['valor'].sum()
            g_hj = df_l[df_l['data'].str.contains(hoje_str, na=False)]['valor'].sum()
    except: df_l = pd.DataFrame(columns=['data', 'descricao', 'valor'])

    dias_restantes = max(31 - agora_br.day, 1)
    dias = np.arange(1, 32)
    s_d = []
    cx = st.session_state.opening_balance - st.session_state.investments - st.session_state.dreams - g_tot
    for d in dias:
        for i in st.session_state.incomes:
            if i['date'] == d: cx += i['val']
        for e in st.session_state.expenses:
            if e['date'] == d: cx -= e['val']
        s_d.append(cx)

    # GRÁFICO (REMOÇÃO DEFINITIVA DO TRACE 0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dias, y=[v/1000 for v in s_d], mode='lines', 
                             line=dict(color='black', width=3), 
                             hovertemplate='Saldo: %{customdata}<extra></extra>',
                             customdata=[format_br(v) for v in s_d]))
    fig.add_hline(y=st.session_state.strategic_reserve/1000, line_dash="dash", line_color="#CCC")
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=250, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F9F9F9', tickformat='.0f', ticksuffix='k'), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    ti, to = sum(i['val'] for i in st.session_state.incomes), sum(e['val'] for e in st.session_state.expenses)
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + ti) - to - st.session_state.investments - st.session_state.dreams - g_tot
    meta_d = (livre + g_hj) / (dias_restantes + 1)
    ct_h = meta_d - g_hj

    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<div class="card"><p class="metric-label">Operacional Restante</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="card"><p class="metric-label">Cota Restante (Hoje)</p><p class="metric-value">{format_br(ct_h)[:-3]}</p></div>', unsafe_allow_html=True)

    with st.expander("DETALHAMENTO E AUDITORIA", expanded=False):
        audit_h = f"""<div style="font-size: 11px; color: #666; font-family: 'Inter'; letter-spacing: 0.5px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(+) SALDO INICIAL</span><span>{format_br(st.session_state.opening_balance)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(-) RESERVA BLINDADA</span><span>{format_br(st.session_state.strategic_reserve)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(+) TOTAL RECEITAS</span><span>{format_br(ti)}</span></div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>(-) CUSTOS FIXOS</span><span>{format_br(to)}</span></div>
            <div style="display: flex; justify-content: space-between; padding: 10px 0; color: #000; font-weight: 800; border-top: 1px solid #000;"><span>LIQUIDEZ OPERACIONAL</span><span>{format_br(livre + g_tot)}</span></div>
        </div>"""
        st.markdown(audit_h, unsafe_allow_html=True)

    with st.expander("📝 REGISTRAR NOVO GASTO", expanded=False):
        c_l1, c_l2 = st.columns([2, 1])
        l_d, l_v = c_l1.text_input("DESCRIÇÃO"), c_l2.number_input("VALOR", min_value=0.0, format="%.2f")
        if st.button("LANÇAR GASTO"):
            with st.spinner("Sincronizando..."):
                st.cache_data.clear()
                f_l = conn.read(worksheet="Lancamentos", ttl=0)
                n_e = pd.DataFrame([{"data": agora_br.strftime("%d/%m/%Y %H:%M"), "descricao": l_d, "valor": l_v}])
                final = pd.concat([f_l, n_e], ignore_index=True) if not f_l.empty else n_e
                conn.update(worksheet="Lancamentos", data=final)
                st.session_state.show_anim = True; st.rerun()

        if not df_l.empty:
            st.markdown("---")
            st.markdown('<p style="font-size:10px; color:#888; letter-spacing: 2px;">ÚLTIMOS LANÇAMENTOS:</p>', unsafe_allow_html=True)
            # Tabela Estilo Auditoria
            l_html = '<div style="font-size: 11px; color: #666; font-family: \'Inter\'; letter-spacing: 0.5px;">'
            for _, r in df_l.tail(5).iloc[::-1].iterrows():
                l_html += f'<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 12px 0;"><span>{r["descricao"]}</span><span>{format_br(r["valor"])}</span></div>'
            l_html += '</div>'
            st.markdown(l_html, unsafe_allow_html=True)

    if st.button("REDEFINIR ESTRATÉGIA"):
        st.session_state.step = 0; st.session_state.reset_mode = True; st.rerun()
