import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração da conexão
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="centered")
st.title("🩺 Relatório de Avaliação Individual")

try:
    # 1. Carregamento dos dados
    df_perguntas = pd.DataFrame(supabase.table("perguntas").select("*").execute().data)
    df_empresas = pd.DataFrame(supabase.table("empresas").select("*").execute().data)
    df_funcs = pd.DataFrame(supabase.table("funcionarios").select("*").execute().data)
    df_respostas = pd.DataFrame(supabase.table("respostas").select("*").execute().data)

    # 2. Seletores de Empresa e Funcionário
    emp_map = dict(zip(df_empresas['nome_empresa'], df_empresas['id']))
    emp_selecionada = st.selectbox("Selecione uma empresa:", list(emp_map.keys()))
    
    funcs_emp = df_funcs[df_funcs['empresa_id'] == emp_map[emp_selecionada]]
    func_map = dict(zip(funcs_emp['nome'], funcs_emp['id']))
    func_selecionado = st.selectbox("Selecione o Funcionário:", list(func_map.keys()))

    if st.button("Gerar Análise"):
        func_id = func_map[func_selecionado]
        
        # 3. Merge: Garantindo uso de 'funcionarios_id' e 'pergunta_id'
        df_f = df_respostas[df_respostas['funcionarios_id'] == func_id].merge(
            df_perguntas, left_on='pergunta_id', right_on='id'
        )
        
        # Correção dinâmica de coluna 'tipo'
        col_tipo = 'Tipo' if 'Tipo' in df_f.columns else 'tipo'

        if df_f.empty:
            st.error(f"Nenhuma resposta encontrada para {func_selecionado} (ID: {func_id}).")
        else:
            # 4. Cálculo de Pontos (Corrigido com os dois-pontos ':')
            def calc_pts(row):
                pts = row['resposta']
                if row[col_tipo] == 'Positiva':
                    return 3 - pts
                else:
                    return pts - 1
            
            df_f['pontos'] = df_f.apply(calc_pts, axis=1)
            resumo = df_f.groupby('categoria')['pontos'].sum().reset_index()

            # 5. Cálculo de Risco
            total_pts = df_f['pontos'].sum()
            max_possivel = len(df_f) * 2
            porcentagem = (total_pts / max_possivel) * 100
