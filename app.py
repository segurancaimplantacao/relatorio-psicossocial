import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS para aumentar fonte e escurecer texto
st.markdown("""
    <style>
    .stApp { font-size: 16px !important; color: #000000 !important; }
    h1, h2, h3 { color: #000000 !important; }
    div[data-testid="stDataFrame"] { font-size: 14px !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

if menu == "Funcionário":
    st.title("Acesso ao Questionário")
    cpf = st.text_input("Digite seu CPF:")
    # (Lógica do funcionário vai aqui)
    st.info("Formulário disponível para preenchimento.")

else:
    st.title("Painel do Gestor")
    
    # Checkboxes de filtro
    st.sidebar.subheader("Filtrar Status:")
    c1 = st.sidebar.checkbox("Sem evidência de risco", value=True)
    c2 = st.sidebar.checkbox("Parcial", value=True)
    c3 = st.sidebar.checkbox("Evidências de risco", value=True)
    
    status_selecionados = []
    if c1: status_selecionados.append("Sem evidência de risco")
    if c2: status_selecionados.append("Parcial")
    if c3: status_selecionados.append("Evidências de risco")

    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
    empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

    if st.button("CARREGAR DADOS"):
        res = supabase.table("respostas").select("resposta, perguntas(pergunta)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            df['Pergunta'] = df['perguntas'].apply(lambda x: x['pergunta'])
            
            def status_map(r):
                if r == 1: return "Sem evidência de risco"
                if r == 2: return "Parcial"
                return "Evidências de risco"
            
            df['Status'] = df['resposta'].apply(status_map)
            df_plot = df[df['Status'].isin(status_selecionados)]
            
            fig = px.bar(df_plot.groupby(['Pergunta', 'Status']).size().reset_index(name='Contagem'), 
                         y="Pergunta", x="Contagem", color="Status", orientation='h',
                         color_discrete_map={"Parcial": "#FFEB3B", "Sem evidência de risco": "#4F81BD", "Evidências de risco": "#C0504D"})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela limpa (apenas Pergunta e Status)
            st.subheader("Detalhes das Respostas")
            st.dataframe(df[['Pergunta', 'Status']], use_container_width=True)
        else:
            st.error("Nenhum dado encontrado.")
