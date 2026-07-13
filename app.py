import streamlit as st
from supabase import create_client
import pandas as pd

# Conexão (mantenha a sua chave)
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# --- BARRA LATERAL (SEPARAÇÃO DE MÓDULOS) ---
modo = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- LÓGICA DO FUNCIONÁRIO (QUESTIONÁRIO) ---
if modo == "Funcionário":
    st.title("👤 Área do Funcionário")
    cpf = st.text_input("Digite seu CPF:")
    
    if cpf:
        # Aqui você insere a lógica original que abre o questionário para o funcionário
        st.write(f"Buscando questionário para o CPF: {cpf}...")
        # Adicione aqui o seu código de carregar perguntas e exibir o formulário

# --- LÓGICA DO GESTOR (RELATÓRIO) ---
elif modo == "Gestor":
    st.title("🩺 Relatório de Avaliação Individual")
    
    # Carregamento de dados para o Gestor
    try:
        df_perguntas = pd.DataFrame(supabase.table("perguntas").select("*").execute().data)
        df_empresas = pd.DataFrame(supabase.table("empresas").select("*").execute().data)
        df_funcs = pd.DataFrame(supabase.table("funcionarios").select("*").execute().data)
        df_respostas = pd.DataFrame(supabase.table("respostas").select("*").execute().data)

        emp_map = dict(zip(df_empresas['nome_empresa'], df_empresas['id']))
        emp_selecionada = st.selectbox("Selecione uma empresa:", list(emp_map.keys()))
        
        funcs_emp = df_funcs[df_funcs['empresa_id'] == emp_map[emp_selecionada]]
        func_map = dict(zip(funcs_emp['nome'], funcs_emp['id']))
        func_selecionado = st.selectbox("Selecione o Funcionário:", list(func_map.keys()))

        if st.button("Gerar Análise"):
            func_id = func_map[func_selecionado]
            df_f = df_respostas[df_respostas['funcionarios_id'] == func_id]
            
            if df_f.empty:
                st.error(f"Nenhuma resposta encontrada para {func_selecionado} (ID: {func_id}).")
            else:
                st.success("Dados encontrados!")
                # Aqui entra o seu código de processamento/cálculo do gráfico
    except Exception as e:
        st.error(f"Erro ao carregar dados do gestor: {e}")
