import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração do Supabase
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
        
        # 3. Busca Dados
        respostas = supabase.table("respostas").select("resposta, pergunta_id").eq("funcionarios_id", id_funcionario).execute().data
        perguntas = supabase.table("perguntas").select("id, categoria, Tipo, pergunta").execute().data
        
        df_respostas = pd.DataFrame(respostas)
        df_perguntas = pd.DataFrame(perguntas)
        
        # Merge para ter tudo junto
        df_completo = df_respostas.merge(df_perguntas, left_on='pergunta_id', right_on='id')
        
        # Lógica de Pontuação (Inverte se for positiva)
        def calcular_pontos(row):
            pts = row['resposta']
            # Se for positiva, invertemos: 1 vira 4, 4 vira 1
            return (5 - pts) if row['Tipo'] == "Positiva" else pts
        
        df_completo['pontos'] = df_completo.apply(calcular_pontos, axis=1)
        
        # 4. Plano de Ação
        planos_de_acao = {
            "Demandas de Trabalho": "Revisar carga horária, redistribuir tarefas e implementar pausas estruturadas.",
            "Controle e Autonomia": "Promover treinamentos de liderança para aumentar a delegação e participação da equipe.",
            "Suporte Social e Relações": "Realizar dinâmicas de team building e estabelecer canais de comunicação clara.",
            "Reconhecimento e Justiça Organizacional": "Instituir política de feedbacks regulares e revisar critérios de meritocracia."
        }

        # 5. Exibição
        st.subheader(f"Análise Detalhada: {funcionario_selecionado}")
        
        resumo_categorias = df_completo.groupby('categoria')['pontos'].sum().reset_index()
        st.write("### Risco por Categoria")
        st.table(resumo_categorias)
        
        # Identifica categoria de maior risco
        cat_critica = resumo_categorias.loc[resumo_categorias['pontos'].idxmax()]['categoria']
        
        st.warning(f"💡 **Foco de Atenção:** {cat_critica}")
        st.info(f"**Plano de Ação sugerido:** {planos_de_acao.get(cat_critica, 'Revisar processos internos de gestão.')}")
        
        total = df_completo['pontos'].sum()
        st.metric("Pontuação Total de Risco", total)
        
        if total <= 33: col = "green"
        elif total <= 46: col = "orange"
        else: col = "red"
        st.markdown(f"### Classificação: <span style='color:{col}'>{'Baixo' if total <= 33 else 'Moderado' if total <= 46 else 'Alto'} Risco</span>", unsafe_allow_html=True)
else:
    st.warning("Nenhum funcionário cadastrado nesta empresa.")
