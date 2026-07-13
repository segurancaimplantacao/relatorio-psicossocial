import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

st.title("Relatório Médico Individual")

# Busca empresas para o seletor
empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data

if empresas_data:
    nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
    empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

    if st.button("CARREGAR RELATÓRIO"):
        # Busca respostas, perguntas e nomes dos funcionários
        res = supabase.table("respostas").select("resposta, perguntas(pergunta), funcionarios(nome)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Ajuste dos dados
            df['Pergunta'] = df['perguntas'].apply(lambda x: x.get('pergunta', ''))
            df['Funcionario'] = df['funcionarios'].apply(lambda x: x.get('nome', 'N/A'))
            
            # Mapeamento de texto (ajuste conforme o seu banco de dados se for 1, 2, 3)
            # Se no seu banco os valores forem diferentes, ajuste aqui:
            mapa_res = {1: "Evidências Claras", 2: "Parcialmente Evidenciado", 3: "Sem Evidências"}
            df['Resposta_Texto'] = df['resposta'].map(mapa_res)
            
            # Exibe a tabela formatada
            st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta_Texto']], use_container_width=True)
            
            # Download CSV
            csv = df[['Funcionario', 'Pergunta', 'Resposta_Texto']].to_csv(index=False).encode('utf-8')
            st.download_button("Baixar CSV para o Doutor", csv, "relatorio_detalhado.csv", "text/csv")
        else:
            st.warning("Nenhum dado encontrado para esta empresa.")
