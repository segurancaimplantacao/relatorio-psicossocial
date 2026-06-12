import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração do Supabase (O Streamlit vai ler isso das suas "Secrets")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🩺 Relatório de Avaliação Individual")

cpf = st.text_input("Digite o CPF do colaborador:")

if cpf:
    # Busca as respostas do funcionário
    response = supabase.table("respostas").select("*").eq("cpf", cpf).execute()
    dados = response.data
    
    if dados:
        df = pd.DataFrame(dados)
        st.write(f"### Avaliação encontrada para: {cpf}")
        
        # Aqui entra a lógica de cálculo que definimos
        # (Depois vamos refinar essa parte juntos para mostrar o risco)
        st.dataframe(df)
    else:
        st.warning("Nenhuma avaliação encontrada para este CPF.")
