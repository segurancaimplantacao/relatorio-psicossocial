import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🩺 Relatório de Avaliação Individual")

# 1. Busca Empresas
response_emp = supabase.table("empresas").select("id, nome_empresa").execute()
df_emp = pd.DataFrame(response_emp.data)
nome_empresa_escolhida = st.selectbox("Selecione a Empresa:", df_emp['nome_empresa'].tolist())
id_empresa = df_emp.loc[df_emp['nome_empresa'] == nome_empresa_escolhida, 'id'].values[0]

# 2. Busca Funcionários
response_funcs = supabase.table("funcionarios").select("nome").eq("empresa_id", int(id_empresa)).execute()
df_funcs = pd.DataFrame(response_funcs.data)

if not df_funcs.empty:
    lista_funcs = df_funcs['nome'].unique().tolist()
    funcionario_selecionado = st.selectbox("Selecione o Funcionário:", lista_funcs)
    
    if funcionario_selecionado:
        # TENTA BUSCAR OS DADOS
        # Verifique se a coluna na tabela 'respostas' se chama 'nome' mesmo!
        response_dados = supabase.table("respostas").select("*").eq("nome", funcionario_selecionado).execute()
        
        if response_dados.data:
            df = pd.DataFrame(response_dados.data)
            
            # Cálculo de risco
            def calcular_risco(row):
                val = row.get('resposta', 0)
                # Verifica se a coluna 'Tipo' existe
                if row.get('Tipo') == 'Positiva':
                    return 4 - val
                return val
            
            df['pontos_risco'] = df.apply(calcular_risco, axis=1)
            total = df['pontos_risco'].sum()
            
            st.metric("Pontuação Total de Risco", total)
            st.write(f"### Classificação: {'Baixo Risco' if total <= 33 else 'Risco Moderado' if total <= 46 else 'Alto Risco'}")
        else:
            st.error("Não achei dados de respostas para este funcionário. Verifique se o nome na tabela 'respostas' é idêntico ao da tabela 'funcionarios'.")
