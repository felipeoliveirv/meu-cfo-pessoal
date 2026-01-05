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

# --- CSS PRECISÃO V46.1 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 0px; padding: 14px; font-weight: 800; border: none; 
        text-transform: uppercase; letter-spacing: 2px; font-size: 11px;
    }

    .nav-arrow-container button {
        background-color: transparent !important; border: none !important;
        color: #000000 !important; font-size: 32px !important; padding: 0px !important;
    }

    .stNumberInput input, .stTextInput input {
        border: none !important; border-bottom: 1px solid #000 !important;
        border-radius: 0px !important; font-size: 18px !important; font-weight: 600 !important;
    }
    
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 36px; font-weight: 800; margin-top: 5px; letter-spacing: normal; line-height: 1.1; color: #000; display: block; }
    
    .sec-label { font-size: 9px; color: #BBB; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; }
    .sec-value { font-size: 22px; font-weight: 700; color: #444; margin-top: 2px; }
    
    .card { padding: 25px 0; border-bottom: 1px solid #EEE; margin-bottom: 5px; }
    .card-sec { padding: 15px 0; border-bottom: 1px solid #F5F5F5; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'installments', 'show_anim', 'reset_mode']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses', 'installments'] else (0 if key == 'step' else 0.0)

# --- CONEXÃO ---
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
            st.session_state.incomes = conn.read(worksheet="Receitas", ttl=0).to_dict('records')
            st.session_state.expenses = conn.read(worksheet="Custos", ttl=0).to_dict('records')
            try: st.session_state.installments = conn.read(worksheet="Parcelas", ttl=0).to_dict('records')
            except: pass
            st.session_state.step = 4
except: pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

# --- DASHBOARD ---
if st.session_state.step == 4:
    agora_br = datetime.now() - timedelta(hours=3)
    hoje_str = agora_br.strftime("%d/%m/%Y")
    
    try:
        df_l = conn.read(worksheet="Lancamentos", ttl=0)
        if not df_l.empty:
            df_l['valor'] = pd.to_numeric(df_l['valor'], errors='coerce').fillna(0)
            g_tot, g_hj = df_l['valor'].sum(), df_l[df_l['data'].str.contains(hoje_str, na=False)]['valor'].sum()
        else: g_tot, g_hj = 0.0, 0.0
    except: 
        df_l = pd.DataFrame(columns=['data', 'descricao', 'valor'])
        g_tot, g_hj = 0.0, 0.0

    # LÓGICA SMART DE PARCELAS
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

    # KPIs PRIMÁRIOS
    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<div class="card"><p class="metric-label">Operacional Restante</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="card"><p class="metric-label">Cota Restante (Hoje)</p><p class="metric-value">{format_br(ct_h)}</p></div>', unsafe_allow_html=True)

    # KPIs SECUNDÁRIOS (CORRIGIDO)
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="card-sec"><p class="sec-label">Cota (Amanhã)</p><p class="sec-value">{format_br(livre / d_rest if d_rest > 0 else 0)}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-sec"><p class="sec-label">Fatura Atual (Cartão)</p><p class="sec-value">{format_br(valor_parcelas_mes)}</p></div>', unsafe_allow_html=True)

    # PARCELAMENTOS
    with st.expander("💳 GESTÃO DE PARCELAMENTOS", expanded=False):
        c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
        p_d = c_p1.text_input("DESCRIÇÃO COMPRA")
        p_v = c_p2.number_input("VALOR TOTAL", min_value=0.0, key="p_val")
        p_n = c_p3.number_input("Nº PARCELAS", 1, 48, 12, key="p_num")
        if st.button("REGISTRAR PARCELAMENTO"):
            st.session_state.installments.append({
                "descricao": p_d, "valor_total": p_v, "parcelas": p_n, 
                "mes_inicio": agora_br.month, "ano_inicio": agora_br.year
            })
            conn.update(worksheet="Parcelas", data=pd.DataFrame(st.session_state.installments))
            st.rerun()
        
        if st.session_state.installments:
            st.markdown("---")
            for idx, p in enumerate(st.session_state.installments):
                meses_passados = (agora_br.year - int(p['ano_inicio'])) * 12 + (agora_br.month - int(p['mes_inicio']))
                if 0 <= meses_passados < int(p['parcelas']):
                    cp1, cp2 = st.columns([0.9, 0.1])
                    cp1.markdown(f"**{p['descricao']}** • {meses_passados+1}/{p['parcelas']} de {format_br(float(p['valor_total'])/int(p['parcelas']))}")
                    if cp2.button("✕", key=f"del_p_{idx}"):
                        st.session_state.installments.pop(idx)
                        conn.update(worksheet="Parcelas", data=pd.DataFrame(st.session_state.installments))
                        st.rerun()

    # GESTÃO DE GASTOS
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

        if not df_l.empty:
            st.markdown("---")
            for idx, r in df_l.tail(5).iloc[::-1].iterrows():
                row_c1, row_c2 = st.columns([0.9, 0.1])
                row_c1.markdown(f"""<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EEE; padding: 10px 0; font-size:12px;"><span>{r['descricao']}</span><span>{format_br(r['valor'])}</span></div>""", unsafe_allow_html=True)
                if row_c2.button("✕", key=f"del_l_{idx}"):
                    df_l = df_l.drop(idx)
                    conn.update(worksheet="Lancamentos", data=df_l)
                    st.rerun()

    if st.button("REDEFINIR ESTRATÉGIA"):
        st.session_state.step = 0; st.session_state.reset_mode = True; st.rerun()
