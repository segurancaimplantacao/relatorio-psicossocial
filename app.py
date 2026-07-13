import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="centered") # layout centrado para melhor formato retrato

st.title("🩺 Relatório de Avaliação Individual")

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
        df_f = df_respostas[df_respostas['funcionarios_id'] == func_id].merge(df_perguntas, left_on='pergunta_id', right_on='id')
        col_tipo = 'Tipo' if 'Tipo' in df_f.columns else 'tipo'
        
        # Cálculo: invertendo perguntas negativas para somar como risco
        def calc_pts(row):
            pts = row['resposta']
            return pts if row[col_tipo] == 'Negativa' else (4 - pts)
        
        df_f['pontos'] = df_f.apply(calc_pts, axis=1)
        resumo = df_f.groupby('categoria')['pontos'].sum().reset_index()

        # Exibição vertical (retrato)
        st.subheader(f"Análise: {func_selecionado}")
        for _, row in resumo.iterrows():
            st.write(f"**{row['categoria']}**: {row['pontos']} pontos")
        
        # Lógica de Foco de Atenção
        maior_risco = resumo.loc[resumo['pontos'].idxmax()]
        st.warning(f"💡 **Foco de Atenção:** {maior_risco['categoria']}")
        
        st.write("### Plano de Ação Sugerido")
        st.success(f"Desenvolver ações focadas em {maior_risco['categoria']} para melhorar a pontuação do colaborador.")
        
        total = resumo['pontos'].sum()
        st.metric("Pontuação Total de Risco", total)

except Exception as e:
    st.error("Erro ao gerar relatório.")
