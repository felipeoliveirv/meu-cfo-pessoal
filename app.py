import streamlit as st
import pandas as pd

# Configuração de Estética Apple/Satisfy
st.set_page_config(page_title="CFO Pessoal", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000000; }
    .stButton>button { width: 100%; background-color: #000000 !important; color: #FFFFFF !important; border-radius: 4px; padding: 15px; font-weight: 600; border: none; margin-top: 20px; }
    .setup-title { font-size: 32px; font-weight: 800; letter-spacing: -1.5px; text-transform: uppercase; margin-bottom: 5px; }
    .setup-subtitle { font-size: 16px; color: #666; margin-bottom: 30px; }
    .stNumberInput input { font-size: 24px !important; border: none !important; border-bottom: 2px solid #EEE !important; border-radius: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de Navegação
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# Fluxo de Onboarding
if st.session_state.step <= 4:
    steps = {1: "Revenue Stream", 2: "Operating Expenses", 3: "Capital Allocation", 4: "Dream Provision"}
    subs = {1: "Renda mensal líquida (salário)", 2: "Custos fixos totais (contas)", 3: "Meta de investimento mensal", 4: "Reserva mensal para sonhos"}
    
    st.markdown(f'<p class="setup-title">{steps[st.session_state.step]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="setup-subtitle">{subs[st.session_state.step]}</p>', unsafe_allow_html=True)
    
    val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key=f"in_{st.session_state.step}")
    
    if st.button("PRÓXIMO"):
        st.session_state.data[steps[st.session_state.step]] = val
        st.session_state.step += 1
        st.rerun()

else:
    # Cálculo do CFO
    d = st.session_state.data
    saldo_livre = d["Revenue Stream"] - d["Operating Expenses"] - d["Capital Allocation"] - d["Dream Provision"]
    cota_diaria = saldo_livre / 30

    st.markdown('<p class="setup-title">Setup Finalizado</p>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background-color: #F8F8F8; padding: 30px; border-radius: 8px; margin: 20px 0;">
            <p style="font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin:0;">Cota Tática Diária</p>
            <p style="font-size: 48px; font-weight: 800; color: #000; margin: 0;">R$ {cota_diaria:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("SALVAR E IR PARA O DASHBOARD"):
        st.success("Configuração salva localmente. Próximo passo: Conectar ao Google Sheets!")
