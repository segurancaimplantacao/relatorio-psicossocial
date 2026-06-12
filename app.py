import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🩺 Relatório de Avaliação Individual")

# 1. Busca os IDs das empresas disponíveis
response_empresas = supabase.table("respostas").select("empresa_id").execute()
df_empresas = pd.DataFrame(response_empresas.data)
# Pega os IDs únicos e transforma em lista
lista_empresas = df_empresas['empresa_id'].unique().tolist()

# 2. Seleção de Empresa (ID)
empresa_selecionada = st.selectbox("Selecione o ID da Empresa:", lista_empresas)

if empresa_selecionada:
    # 3. Busca funcionários apenas daquele ID de empresa
    response_funcs = supabase.table("respostas").select("nome").eq("empresa_id", empresa_selecionada).execute()
    df_funcs = pd.DataFrame(response_funcs.data)
    lista_funcs = df_funcs['nome'].unique().tolist()
    
    # 4. Seleção de Funcionário
    funcionario_selecionado = st.selectbox("Selecione o Funcionário:", lista_funcs)
    
    if funcionario_selecionado:
        # 5. Busca dados específicos do funcionário selecionado
        response_dados = supabase.table("respostas").select("*").eq("nome", funcionario_selecionado).execute()
        dados = response_dados.data
        
        if dados:
            df = pd.DataFrame(dados)
            
            # Lógica de cálculo (ajuste conforme necessário)
            def calcular_risco(row):
                if row['Tipo'] == 'Positiva':
                    return 4 - row['resposta']
                else:
                    return row['resposta']
            
            df['pontos_risco'] = df.apply(calcular_risco, axis=1)
            total = df['pontos_risco'].sum()
            
            # Classificação
            if total <= 33: classificacao = "Baixo Risco"
            elif total <= 46: classificacao = "Risco Moderado"
            else: classificacao = "Alto Risco"
                
            st.subheader(f"Resultado para: {funcionario_selecionado}")
            st.metric("Pontuação Total de Risco", total)
            st.write(f"### Classificação: {classificacao}")
