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

# CONEXÃO COM GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_success = load_lottieurl("https://lottie.host/5a2d67a1-94a3-4886-905c-5912389d4d03/GjX1Xl9T8y.json")

def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    .stButton>button { width: 100%; background-color: #000 !important; color: #FFF !important; border-radius: 0px; padding: 14px; font-weight: 800; border: none; text-transform: uppercase; letter-spacing: 3px; font-size: 10px; }
    .stNumberInput input, .stTextInput input { border: none !important; border-bottom: 1px solid #000 !important; border-radius: 0px !important; font-size: 18px !important; font-weight: 600 !important; }
    .brand-header { font-size: 24px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 40px; border-bottom: 3px solid #000; display: inline-block; }
    .setup-step { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .metric-label { font-size: 10px; color: #999; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 42px; font-weight: 800; margin-top: 10px; letter-spacing: -1px; line-height: 1.1; color: #000; display: block; }
    .card { padding: 40px 0; border-bottom: 1px solid #EEE; margin-bottom: 10px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ENGINE DE ESTADO
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'show_anim']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# TENTATIVA DE CARREGAR DADOS EXISTENTES (PERSISTÊNCIA)
if st.session_state.step == 0:
    try:
        # Tenta ler a aba 'Config' para ver se o setup já foi feito
        check_df = conn.read(worksheet="Config", usecols=[0,1])
        if not check_df.empty:
            # Se houver dados, o app assume que o setup está pronto
            st.session_state.step = 4
    except:
        pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

if st.session_state.show_anim and lottie_success:
    st_lottie(lottie_success, height=80, speed=1.8, key="success_anim")
    time.sleep(0.8)
    st.session_state.show_anim = False
    st.rerun()

# --- TELAS 0, 1, 2 E 3 (IGUAIS AO ANTERIOR) ---
# [Mantenha o código das etapas anteriores aqui...]

# --- ÚLTIMO PASSO: SALVAR ---
if st.session_state.step == 3:
    st.markdown('<p class="setup-step">04_ALOCAÇÃO DE CAPITAL</p>', unsafe_allow_html=True)
    inv = st.number_input("INVESTIMENTOS MENSAL", min_value=0.0, format="%.2f")
    drm = st.number_input("SONHOS / LIFESTYLE", min_value=0.0, format="%.2f")
    if st.button("SALVAR ESTRATÉGIA NO COFRE"):
        st.session_state.investments, st.session_state.dreams = inv, drm
        
        # PREPARAR DADOS PARA PLANILHA
        config_data = pd.DataFrame([
            {"parametro": "saldo_inicial", "valor": st.session_state.opening_balance},
            {"parametro": "reserva", "valor": st.session_state.strategic_reserve},
            {"parametro": "investimento", "valor": st.session_state.investments},
            {"parametro": "sonhos", "valor": st.session_state.dreams}
        ])
        
        # ATUALIZAR GOOGLE SHEETS
        conn.update(worksheet="Config", data=config_data)
        
        st.session_state.step = 4
        st.session_state.show_anim = True
        st.rerun()

# --- DASHBOARD (ETAPA 4 IGUAL AO ANTERIOR) ---
