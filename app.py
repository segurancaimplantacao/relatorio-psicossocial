import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

st.title("🩺 Relatório de Avaliação Individual")

# 1. Carregar dados básicos
empresas = supabase.table("empresas").select("id, nome_empresa").execute().data
funcs = supabase.table("funcionarios").select("id, nome, empresa_id").execute().data
perguntas = supabase.table("perguntas").select("id, pergunta, categoria, tipo").execute().data
respostas = supabase.table("respostas").select("funcionario_id, pergunta_id, resposta").execute().data

df_perguntas = pd.DataFrame(perguntas)
df_respostas = pd.DataFrame(respostas)
df_funcs = pd.DataFrame(funcs)

# 2. Filtros de Seleção
empresa_map = {e['nome_empresa']: e['id'] for e in empresas}
emp_nome = st.selectbox("Selecione uma empresa:", list(empresa_map.keys()))
emp_id = empresa_map[emp_nome]

funcs_empresa = [f for f in funcs if f['empresa_id'] == emp_id]
func_map = {f['nome']: f['id'] for f in funcs_empresa}
func_nome = st.selectbox("Selecione o Funcionário:", list(func_map.keys()))
func_id = func_map[func_nome]

if st.button("Gerar Análise"):
    # 3. Processamento dos dados do funcionário
    df_f = df_respostas[df_respostas['funcionario_id'] == func_id].merge(df_perguntas, left_on='pergunta_id', right_on='id')
    
    # Lógica de Pontuação (Ajuste conforme seu cálculo real)
    # Exemplo: Resposta 1 (Discordo), 2 (Parcial), 3 (Concordo)
    def calcular_pontos(row):
        r = row['resposta']
        # Se for Positiva, 3=bom, 1=ruim. Se for Negativa, 1=bom, 3=ruim.
        if row['tipo'] == 'Positiva': return r
        return 4 - r # Inverte para perguntas negativas

    df_f['pontos'] = df_f.apply(calcular_pontos, axis=1)
    
    # 4. Exibição da Análise
    st.subheader(f"Análise Detalhada: {func_nome}")
    st.write("### Risco por Categoria")
    
    resumo = df_f.groupby('categoria')['pontos'].sum().reset_index()
    st.table(resumo.rename(columns={'categoria': 'Categoria', 'pontos': 'Pontos'}))
    
    total = resumo['pontos'].sum()
    categoria_risco = resumo.loc[resumo['pontos'].idxmax(), 'categoria']
    
    st.info(f"💡 **Foco de Atenção:** {categoria_risco}")
    
    st.write(f"### Pontuação Total de Risco: {total}")
    
    # Classificação simples baseada no total
    if total < 20: status = "Baixo Risco"
    elif total < 35: status = "Moderado Risco"
    else: status = "Alto Risco"
    
    st.subheader(f"Classificação: {status}")
