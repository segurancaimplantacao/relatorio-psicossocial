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
response_funcs = supabase.table("funcionarios").select("id, nome").eq("empresa_id", int(id_empresa)).execute()
df_funcs = pd.DataFrame(response_funcs.data)

if not df_funcs.empty:
    nome_para_id = dict(zip(df_funcs['nome'], df_funcs['id']))
    funcionario_selecionado = st.selectbox("Selecione o Funcionário:", list(nome_para_id.keys()))
    
    if funcionario_selecionado:
        id_funcionario = nome_para_id[funcionario_selecionado]
        
        # 3. Busca respostas e as perguntas associadas
        # Aqui usamos o conceito de JOIN para trazer o texto da pergunta e o tipo
        response_dados = supabase.table("respostas").select("resposta, perguntas(pergunta, tipo)").eq("funcionarios_id", id_funcionario).execute()
        
        if response_dados.data:
            dados = []
            for item in response_dados.data:
                # Transforma a resposta texto (ex: "Concordo") em pontos (1 a 4)
                # Exemplo: Concordo=4, Discordo=1
                valor = 4 if item['resposta'] == "Concordo" else 1
                
                # Se for pergunta Positiva, invertemos o valor
                if item['perguntas']['tipo'] == "Positiva":
                    valor = 5 - valor # Converte: 4 vira 1, 1 vira 4
                
                dados.append(valor)
            
            total = sum(dados)
            
            # Classificação
            if total <= 33: classificacao = "Baixo Risco"
            elif total <= 46: classificacao = "Risco Moderado"
            else: classificacao = "Alto Risco"
                
            st.subheader(f"Resultado: {funcionario_selecionado}")
            st.metric("Pontuação Total de Risco", total)
            st.write(f"### Classificação: {classificacao}")
        else:
            st.error("Não foram encontradas respostas para este funcionário.")
else:
    st.warning("Nenhum funcionário cadastrado nesta empresa.")
