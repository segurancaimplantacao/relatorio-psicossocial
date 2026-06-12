import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🩺 Relatório de Avaliação Individual")

# 1. Busca todas as empresas (nomes e IDs) para montar o menu
response_emp = supabase.table("empresas").select("id, nome_fantasia").execute()
df_emp = pd.DataFrame(response_emp.data)

# Criamos um dicionário para facilitar: {ID: Nome}
mapa_empresas = dict(zip(df_emp['id'], df_emp['nome_fantasia']))

# 2. Seleção de Empresa pelo nome
nome_empresa_escolhida = st.selectbox("Selecione a Empresa:", df_emp['nome_fantasia'].tolist())

# Descobre qual o ID da empresa que tem esse nome
id_empresa_escolhida = df_emp.loc[df_emp['nome_fantasia'] == nome_empresa_escolhida, 'id'].values[0]

# 3. Busca funcionários daquela empresa (usando o ID)
response_funcs = supabase.table("respostas").select("nome").eq("empresa_id", id_empresa_escolhida).execute()
df_funcs = pd.DataFrame(response_funcs.data)
lista_funcs = df_funcs['nome'].unique().tolist()

# 4. Seleção de Funcionário
funcionario_selecionado = st.selectbox("Selecione o Funcionário:", lista_funcs)

if funcionario_selecionado:
    # 5. Busca dados do funcionário
    response_dados = supabase.table("respostas").select("*").eq("nome", funcionario_selecionado).execute()
    dados = response_dados.data
    
    if dados:
        df = pd.DataFrame(dados)
        
        # Lógica de cálculo
        def calcular_risco(row):
            if row['Tipo'] == 'Positiva':
                return 4 - row['resposta']
            else:
                return row['resposta']
        
        df['pontos_risco'] = df.apply(calcular_risco, axis=1)
        total = df['pontos_risco'].sum()
        
        if total <= 33: classificacao = "Baixo Risco"
        elif total <= 46: classificacao = "Risco Moderado"
        else: classificacao = "Alto Risco"
            
        st.subheader(f"Resultado para: {funcionario_selecionado}")
        st.metric("Pontuação Total de Risco", total)
        st.write(f"### Classificação: {classificacao}")
