import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar # Nova biblioteca para inteligência de datas

# --- CONFIGURAÇÃO CFO. ---
st.set_page_config(page_title="CFO. | Operação", layout="centered")

def format_br(val):
    if val is None: return "R$ 0,00"
    return "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# --- CSS PRECISÃO V60.0 (CALENDAR AWARE) ---
# --- CSS PRECISÃO V60.0 (LUXURY UPDATE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #000; }
    
    /* Botões pretos sólidos e arredondados */
    .stButton>button { 
        width: 100%; background-color: #000 !important; color: #FFF !important; 
        border-radius: 12px; padding: 16px; font-weight: 600; border: none; 
        text-transform: uppercase; letter-spacing: 1px; font-size: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.15); }

    /* Inputs minimalistas */
    .stNumberInput input, .stTextInput input {
        border: none !important; border-bottom: 2px solid #E0E0E0 !important;
        background-color: transparent !important;
        border-radius: 0px !important; font-size: 20px !important; font-weight: 600 !important;
        color: #000 !important; padding-left: 0px !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus { border-bottom: 2px solid #000 !important; }
    
    /* Header da Marca */
    .brand-header { font-size: 18px; font-weight: 900; letter-spacing: -1px; text-transform: uppercase; margin-bottom: 30px; display: inline-block; }
    
    /* Métricas Gigantes (Estilo da Imagem) */
    .metric-label { font-size: 11px; color: #666; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
    .metric-value { font-size: 48px; font-weight: 900; letter-spacing: -2px; line-height: 1; color: #000; display: block; margin-bottom: 10px; }
    
    /* Cards Flutuantes */
    .card { 
        padding: 20px; border-radius: 20px; 
        background: #FFFFFF; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.04); 
        margin-bottom: 15px; border: 1px solid #F0F0F0;
    }
    .card-sec { 
        padding: 15px; border-radius: 16px; 
        background: #F8F8F8; margin-bottom: 10px; 
    }
    
    /* Auditoria estilo "Pílula" */
    .audit-card { background: #F5F5F5; padding: 12px 18px; border-radius: 12px; margin-bottom: 8px; font-size: 12px; font-weight: 500; color: #444; border: none; }
    .audit-alert { background: #FFF0F0; color: #D00000; padding: 12px 18px; border-radius: 12px; margin-bottom: 8px; font-size: 12px; font-weight: 700; }
    
    /* Remover elementos padrão do Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stExpander"] { border: none; box-shadow: none; background-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
keys = ['step', 'opening_balance', 'strategic_reserve', 'incomes', 'expenses', 'investments', 'dreams', 'cc_bill', 'cc_due_day', 'reset_mode']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['incomes', 'expenses'] else (0 if key == 'step' else 0.0)

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

if st.session_state.step == 0 and not st.session_state.reset_mode:
    try:
        config_df = conn.read(worksheet="Config", ttl=0)
        if not config_df.empty:
            for _, row in config_df.iterrows():
                p, v = row['parametro'], row['valor']
                if p == 'saldo_inicial': st.session_state.opening_balance = float(v)
                if p == 'reserva': st.session_state.strategic_reserve = float(v)
                if p == 'investimento': st.session_state.investments = float(v)
                if p == 'sonhos': st.session_state.dreams = float(v)
                if p == 'fatura_cc': st.session_state.cc_bill = float(v)
                if p == 'vencimento_cc': st.session_state.cc_due_day = int(v)
            st.session_state.incomes = conn.read(worksheet="Receitas", ttl=0).to_dict('records')
            st.session_state.expenses = conn.read(worksheet="Custos", ttl=0).to_dict('records')
            st.session_state.step = 4
    except: pass

st.markdown('<p class="brand-header">CFO.</p>', unsafe_allow_html=True)

# --- FLUXO DE REVISÃO ---
if st.session_state.step == 0:
    st.markdown('<p class="setup-step">Revisão 01/05</p>', unsafe_allow_html=True)
    st.markdown('### Saldo bancário ATUAL')
    st.session_state.opening_balance = st.number_input("R$", value=st.session_state.opening_balance, step=100.0, label_visibility="collapsed")
    if st.button("PRÓXIMO"): st.session_state.step = 1; st.rerun()

elif st.session_state.step == 1:
    st.markdown('<p class="setup-step">Revisão 02/05</p>', unsafe_allow_html=True)
    st.markdown('### Reservas e Investimentos')
    st.session_state.strategic_reserve = st.number_input("Reserva Blindada", value=st.session_state.strategic_reserve, step=100.0)
    st.session_state.investments = st.number_input("Investimentos", value=st.session_state.investments, step=100.0)
    st.session_state.dreams = st.number_input("Sonhos", value=st.session_state.dreams, step=100.0)
    c1, c2 = st.columns([0.2, 0.8])
    if c1.button("←"): st.session_state.step = 0; st.rerun()
    if c2.button("PRÓXIMO"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.markdown('<p class="setup-step">Revisão 03/05</p>', unsafe_allow_html=True)
    st.markdown('### Cartão de Crédito')
    st.session_state.cc_bill = st.number_input("Valor da Fatura (R$)", value=st.session_state.cc_bill, step=50.0)
    st.session_state.cc_due_day = st.number_input("Dia do Vencimento", value=int(st.session_state.cc_due_day) if st.session_state.cc_due_day > 0 else 10, min_value=1, max_value=31)
    c1, c2 = st.columns([0.2, 0.8])
    if c1.button("←"): st.session_state.step = 1; st.rerun()
    if c2.button("PRÓXIMO"): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.markdown('<p class="setup-step">Revisão 04/05</p>', unsafe_allow_html=True)
    st.markdown('### Fluxo de Receitas e Custos')
    
    # Cálculo dinâmico do último dia do mês para limitar o input
    _, ultimo_dia_mes = calendar.monthrange(datetime.now().year, datetime.now().month)
    
    with st.expander("Receitas (Salário, Extras)", expanded=True):
        with st.form("f_inc", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            d, v, dia = c1.text_input("Descrição"), c2.number_input("Valor (R$)", min_value=0.0), c3.number_input("Dia", 1, ultimo_dia_mes, 5)
            if st.form_submit_button("ADD"): st.session_state.incomes.append({"desc": d, "val": v, "dia": dia}); st.rerun()
        for idx, i in enumerate(st.session_state.incomes):
            col = st.columns([0.9, 0.1])
            col[0].write(f"✅ Dia {i.get('dia', 1)} | {i['desc']}: {format_br(i['val'])}")
            if col[1].button("✕", key=f"d_inc_{idx}"): st.session_state.incomes.pop(idx); st.rerun()

    with st.expander("Custos Fixos (Aluguel, Luz)", expanded=False):
        with st.form("f_exp", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            d, v, dia = c1.text_input("Descrição"), c2.number_input("Valor (R$)", min_value=0.0), c3.number_input("Dia", 1, ultimo_dia_mes, 10)
            if st.form_submit_button("ADD"): st.session_state.expenses.append({"desc": d, "val": v, "dia": dia}); st.rerun()
        for idx, e in enumerate(st.session_state.expenses):
            col = st.columns([0.9, 0.1])
            col[0].write(f"❌ Dia {e.get('dia', 1)} | {e['desc']}: {format_br(e['val'])}")
            if col[1].button("✕", key=f"d_exp_{idx}"): st.session_state.expenses.pop(idx); st.rerun()

    c1, c2 = st.columns([0.2, 0.8])
    if c1.button("←"): st.session_state.step = 2; st.rerun()
    if c2.button("FINALIZAR"):
        data_config = pd.DataFrame([{"parametro": "saldo_inicial", "valor": st.session_state.opening_balance},{"parametro": "reserva", "valor": st.session_state.strategic_reserve},{"parametro": "investimento", "valor": st.session_state.investments},{"parametro": "sonhos", "valor": st.session_state.dreams},{"parametro": "fatura_cc", "valor": st.session_state.cc_bill},{"parametro": "vencimento_cc", "valor": st.session_state.cc_due_day}])
        conn.update(worksheet="Config", data=data_config)
        
        df_inc = pd.DataFrame(st.session_state.incomes)
        if df_inc.empty: df_inc = pd.DataFrame(columns=["desc", "val", "dia"])
        conn.update(worksheet="Receitas", data=df_inc)
        
        df_exp = pd.DataFrame(st.session_state.expenses)
        if df_exp.empty: df_exp = pd.DataFrame(columns=["desc", "val", "dia"])
        conn.update(worksheet="Custos", data=df_exp)
        
        st.session_state.step = 4; st.rerun()

# --- DASHBOARD ---
elif st.session_state.step == 4:
    agora_br = datetime.now() - timedelta(hours=3)
    hoje_dia = agora_br.day
    hoje_str = agora_br.strftime("%d/%m/%Y")
    
    # Inteligência de Calendário: Descobre o último dia deste mês (28, 29, 30 ou 31)
    _, ultimo_dia_mes = calendar.monthrange(agora_br.year, agora_br.month)
    
    try:
        df_l = conn.read(worksheet="Lancamentos", ttl=0)
        df_l['valor'] = pd.to_numeric(df_l['valor'], errors='coerce').fillna(0)
        g_tot = df_l['valor'].sum()
        g_hj = df_l[df_l['data'].str.contains(hoje_str, na=False)]['valor'].sum()
    except: g_tot, g_hj, df_l = 0.0, 0.0, pd.DataFrame(columns=['data', 'descricao', 'valor'])

    # LÓGICA SMART FUTURE
    ti_futuro = sum(i['val'] for i in st.session_state.incomes if int(i.get('dia', 1)) >= hoje_dia)
    to_futuro = sum(e['val'] for e in st.session_state.expenses if int(e.get('dia', 1)) >= hoje_dia)
    cc_restante = st.session_state.cc_bill if int(st.session_state.cc_due_day) >= hoje_dia else 0.0
    
    livre = (st.session_state.opening_balance - st.session_state.strategic_reserve + ti_futuro) - to_futuro - st.session_state.investments - st.session_state.dreams - cc_restante
    
    # Lógica de Liquidez Diária (Ajustada para o Fim do Mês correto)
    projecao_diaria = []
    saldo_simulado = st.session_state.opening_balance
    
    for d in range(hoje_dia, ultimo_dia_mes + 1):
        inc_dia = sum(i['val'] for i in st.session_state.incomes if int(i.get('dia', 1)) == d)
        exp_dia = sum(e['val'] for e in st.session_state.expenses if int(e.get('dia', 1)) == d)
        cc_dia = st.session_state.cc_bill if d == int(st.session_state.cc_due_day) else 0
        
        saldo_simulado = saldo_simulado + inc_dia - exp_dia - cc_dia
        projecao_diaria.append({"dia": d, "saldo": saldo_simulado})
    
    df_proj = pd.DataFrame(projecao_diaria)
    
    if not df_proj.empty:
        menor_saldo = df_proj['saldo'].min()
        dia_critico = df_proj.loc[df_proj['saldo'] == menor_saldo, 'dia'].values[0]
    else:
        menor_saldo = st.session_state.opening_balance
        dia_critico = hoje_dia

    # Métricas Secundárias (Com dias reais)
    d_rest = max(ultimo_dia_mes - hoje_dia, 1)
    cota_amanha = livre / d_rest if d_rest > 0 else 0
    ct_h = ((livre + g_hj) / (d_rest + 1)) - g_hj

    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<div class="card"><p class="metric-label">Operacional Restante</p><p class="metric-value">{format_br(livre)}</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="card"><p class="metric-label">Cota Restante (Hoje)</p><p class="metric-value">{format_br(ct_h)}</p></div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="card-sec"><p class="sec-label">Cota (Amanhã)</p><p class="sec-value">{format_br(cota_amanha)}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-sec"><p class="sec-label">Dias Restantes</p><p class="sec-value">{d_rest} Dias</p></div>', unsafe_allow_html=True)

    st.markdown('<p class="metric-label" style="margin-top:25px;">Fluxo de Caixa Projetado (Liquidez)</p>', unsafe_allow_html=True)
    fig = go.Figure()
    if not df_proj.empty:
        fig.add_trace(go.Scatter(x=df_proj['dia'], y=df_proj['saldo'], fill='tozeroy', mode='lines', name="Fluxo (R$)", line=dict(color='#F0F0F0', width=0.5), fillcolor='rgba(240, 240, 240, 0.3)', hovertemplate='Fluxo: R$ %{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(x=[hoje_dia], y=[livre], marker_color='#000', width=0.6, name="Operacional Atual", hovertemplate='Operacional: R$ %{y:,.2f}<extra></extra>'))
    
    # Eixo X dinâmico baseado no tamanho do mês
    tick_vals = [1, 10, 20, ultimo_dia_mes]
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#CCC'), tickvals=tick_vals), yaxis=dict(showgrid=True, gridcolor='#F9F9F9', tickfont=dict(size=10, color='#CCC')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with st.expander("🔍 AUDITORIA E VALE DE CAIXA", expanded=False):
        if menor_saldo < 0:
            st.markdown(f'<div class="audit-alert">⚠️ ALERTA: Saldo ficará negativo em {format_br(menor_saldo)} no dia {dia_critico}.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="audit-card" style="border-left: 3px solid #2ECC71;">✅ <b>Menor Saldo Previsto:</b> {format_br(menor_saldo)} (Dia {dia_critico})</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="audit-card">💰 <b>Saldo Atual (Banco):</b> {format_br(st.session_state.opening_balance)}</div>
        <div class="audit-card">🛡️ <b>Reserva Blindada:</b> - {format_br(st.session_state.strategic_reserve)}</div>
        <div class="audit-card">📉 <b>Custos Fixos (Restantes):</b> - {format_br(to_futuro)}</div>
        <div class="audit-card">💳 <b>Fatura (Se ainda não venceu):</b> - {format_br(cc_restante)}</div>
        <div class="audit-card" style="background:#000; color:#FFF;"><b>DISPONÍVEL TOTAL:</b> {format_br(livre)}</div>
        """, unsafe_allow_html=True)

    with st.expander("📝 REGISTRAR OU EDITAR GASTOS", expanded=True):
        c_l1, c_l2 = st.columns([2, 1])
        l_d, l_v = c_l1.text_input("Descrição"), c_l2.number_input("Valor", min_value=0.0, key="g_val")
        if st.button("LANÇAR GASTO"):
            st.cache_data.clear()
            f_l = conn.read(worksheet="Lancamentos", ttl=0)
            n_e = pd.DataFrame([{"data": agora_br.strftime("%d/%m/%Y %H:%M"), "descricao": l_d, "valor": l_v}])
            final = pd.concat([f_l, n_e], ignore_index=True) if not f_l.empty else n_e
            conn.update(worksheet="Lancamentos", data=final); st.rerun()
        if not df_l.empty:
            df_hj = df_l[df_l['data'].str.contains(hoje_str, na=False)]
            for idx, r in df_hj.iloc[::-1].iterrows():
                row = st.columns([0.9, 0.1])
                row[0].markdown(f'<div class="hist-item"><span>{r["descricao"]}</span><b>{format_br(r["valor"])}</b></div>', unsafe_allow_html=True)
                if row[1].button("✕", key=f"del_h_{idx}"): df_l = df_l.drop(idx); conn.update(worksheet="Lancamentos", data=df_l); st.rerun()

    if st.button("REDEFINIR ESTRATÉGIA"): st.session_state.step = 0; st.session_state.reset_mode = True; st.rerun()
