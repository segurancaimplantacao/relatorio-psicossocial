import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")
st.title("Diagnóstico de Dados")

# Teste simples de conexão
try:
    res = supabase.table("empresas").select("id, nome_empresa").execute()
    empresas = res.data
    st.write(f"Conexão OK. Empresas encontradas: {len(empresas)}")
    
    nomes = {e['nome_empresa']: e['id'] for e in empresas}
    selecionada = st.selectbox("Selecione", list(nomes.keys()))
    
    if st.button("CARREGAR DADOS"):
        # Chamada protegida
        res_respostas = supabase.table("respostas").select("resposta, perguntas(pergunta)").eq("empresa_id", nomes[selecionada]).execute()
        
        if not res_respostas.data:
            st.warning("O Supabase retornou vazio.")
        else:
            st.write("Dados recebidos do banco:")
            st.json(res_respostas.data[0]) # Mostra o primeiro item para vermos a estrutura
            
            # Tenta converter
            df = pd.DataFrame(res_respostas.data)
            st.write("DataFrame criado com sucesso!")
            st.dataframe(df.head())

except Exception as e:
    st.error(f"ERRO ENCONTRADO: {e}")
