import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="centered")
st.title("🩺 Relatório de Avaliação Individual")

try:
    # 1. Carregamento dos Dados
    df_perguntas = pd.DataFrame(supabase.table("perguntas").select("*").execute().data)
    df_empresas = pd.DataFrame(supabase.table("empresas").select("*").execute().data)
    df_funcs = pd.DataFrame(supabase.table("funcionarios").select("*").execute().data)
    df_respostas = pd.DataFrame(supabase.table("respostas").select("*").execute().data)

    # 2. Seletores
    emp_map = dict(zip(df_empresas['nome_empresa'], df_empresas['id']))
    emp_selecionada = st.selectbox("Selecione uma empresa:", list(emp_map.keys()))
    
    funcs_emp = df_funcs[df_funcs['empresa_id'] == emp_map[emp_selecionada]]
    func_map = dict(zip(funcs_emp['nome'], funcs_emp['id']))
    func_selecionado = st.selectbox("Selecione o Funcionário:", list(func_map.keys()))

    if st.button("Gerar Análise"):
        func_id = func_map[func_selecionado]
        
        # 3. Processamento e Merge
        # Filtra respostas pelo ID do funcionário
        df_f = df_respostas[df_respostas['funcionarios_id'] == func_id].merge(
            df_perguntas, left_on='pergunta_id', right_on='id'
        )
        
        # Identifica se a coluna de tipo é 'Tipo' ou 'tipo'
        col_tipo = 'Tipo' if 'Tipo' in df_f.columns else 'tipo'

        if df_f.empty:
            st.error("Nenhuma resposta encontrada para este colaborador. Verifique o banco de dados.")
        else:
            # 4. Cálculo de Pontos (Lógica justa)
            def calc_pts(row):
                pts = row['resposta']
                # Se Positiva (ex: comunicação): Concordar (3) é bom (0 pts)
                if row[col_tipo] == 'Positiva':
                    return 3 - pts
                # Se Negativa (ex: sobrecarga): Concordar (3) é ruim (2 pts)
                else:
                    return pts - 1
            
            df_f['pontos'] = df_f.apply(calc_pts, axis=1)
            resumo = df_f.groupby('categoria')['pontos'].sum().reset_index()

            # 5. Exibição Visual (Formato Retrato/Vertical)
            st.subheader(f"Análise: {func_selecionado}")
            for _, row in resumo.iterrows():
                st.write(f"**{row['categoria']}**: {row['pontos']} pontos")
            
            # Cálculo de %
            total_pontos = df_f['pontos'].sum()
            max_possivel = len(df_f) * 2
            porcentagem = (total_pontos / max_possivel) * 100

            # Classificação
            if porcentagem < 25: status, cor = "Fora de Risco", "success"
            elif porcentagem < 60: status, cor = "Risco Moderado", "warning"
            else: status, cor = "Alto Risco", "error"

            st.metric("Nível de Risco", f"{porcentagem:.0f}%", delta=status, delta_color="inverse")
            
            # Destaque de Risco
            maior_risco = resumo.loc[resumo['pontos'].idxmax()]
            getattr(st, cor)(f"💡 **Situação: {status}**")
            st.info(f"**Plano de Ação:** Priorizar melhorias em **{maior_risco['categoria']}**.")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
