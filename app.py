import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração do Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🩺 Relatório de Avaliação Individual")

# 1. Busca todas as empresas para o primeiro menu
response_emp = supabase.table("empresas").select("id, nome_empresa").execute()
df_emp = pd.DataFrame(response_emp.data)

# Menu 1: Selecionar Empresa
nome_empresa_escolhida = st.selectbox("Selecione a Empresa:", df_emp['nome_empresa'].tolist())

# Pega o ID correspondente à empresa escolhida
id_empresa = df_emp.loc[df_emp['nome_empresa'] == nome_empresa_escolhida, 'id'].values[0]

# 2. Busca funcionários daquela empresa específica
# Filtramos a tabela 'funcionarios' pelo 'empresa_id'
response_funcs = supabase.table("funcionarios").select("nome").eq("empresa_id", int(id_empresa)).execute()
df_funcs = pd.DataFrame(response_funcs.data)

if not df_funcs.empty:
    lista_funcs = df_funcs['nome'].unique().tolist()
    
    # Menu 2: Selecionar Funcionário
    funcionario_selecionado = st.selectbox("Selecione o Funcionário:", lista_funcs)
    
    if funcionario_selecionado:
        # 3. Busca os resultados da avaliação desse funcionário
        # Assumindo que você busca na tabela 'respostas' pelo nome
        response_dados = supabase.table("respostas").select("*").eq("nome", funcionario_selecionado).execute()
        dados = response_dados.data
        
        if dados:
            df = pd.DataFrame(dados)
            
            # Lógica de cálculo de risco
            def calcular_risco(row):
                # Se a coluna 'Tipo' existir e for 'Positiva', inverte a pontuação
                if 'Tipo' in row and row['Tipo'] == 'Positiva':
                    return 4 - row['resposta']
                return row['resposta']
            
            df['pontos_risco'] = df.apply(calcular_risco, axis=1)
            total = df['pontos_risco'].sum()
            
            # Classificação
            if total <= 33: classificacao = "Baixo Risco"
            elif total <= 46: classificacao = "Risco Moderado"
            else: classificacao = "Alto Risco"
                
            st.subheader(f"Resultado: {funcionario_selecionado}")
            st.metric("Pontuação Total de Risco", total)
            st.write(f"### Classificação: {classificacao}")
        else:
            st.info("Nenhuma avaliação encontrada para este funcionário.")
else:
    st.warning("Nenhum funcionário cadastrado nesta empresa.")
