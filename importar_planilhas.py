import pandas as pd
from sqlalchemy import create_engine


engine = create_engine('postgresql://postgres:admin@localhost:5432/pesquisa_evasao')

colunas_banco_principal = [
    "nu_ano_censo", "co_ies", "no_ies", "sg_ies", "co_curso",
    "co_cine_area_geral", "no_cine_area_geral", "co_cine_rotulo", "no_cine_rotulo",
    "co_ocde_area_especifica", "co_ocde", "ds_classificacao_area", "ds_nivel_comparabilidade",
    "qt_ufs_distintas", "sg_uf_lista",
    "qt_vg_total", "qt_inscrito_total", "qt_ing", "qt_mat", "qt_conc",
    "qt_sit_trancada", "qt_sit_desvinculado", "qt_sit_transferido", "qt_sit_falecido"
]

colunas_banco_expandida = [
    "nu_ano_censo", "co_ies", "co_curso", "tp_dimensao", "sg_uf", "no_municipio",
    "qt_vg_total", "qt_inscrito_total", "qt_ing", "qt_mat", "qt_conc",
    "qt_sit_trancada", "qt_sit_desvinculado", "qt_sit_transferido", "qt_sit_falecido"
]

metricas = [
    "qt_vg_total", "qt_inscrito_total", "qt_ing", "qt_mat", "qt_conc",
    "qt_sit_trancada", "qt_sit_desvinculado", "qt_sit_transferido", "qt_sit_falecido"
]

url_principal = "https://raw.githubusercontent.com/efdourado/evasao-computacao/main/data/processed/oficial/planilha_oficial_computacao.csv"

# download da principal
df = pd.read_csv(url_principal, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
df.columns = [col.lower() for col in df.columns]

for metrica in metricas:
    if metrica in df.columns:
        df[metrica] = pd.to_numeric(df[metrica], errors="coerce")

# filtro
colunas_filtradas = [c for c in colunas_banco_principal if c in df.columns]
df = df[colunas_filtradas]
df.to_sql('planilha_oficial_computacao', engine, schema='dados', if_exists='append', index=False)

url_expandida = "https://raw.githubusercontent.com/efdourado/evasao-computacao/main/data/processed/oficial/planilha_oficial_computacao_expandida.csv"

df_expandida = pd.read_csv(url_expandida, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
df_expandida.columns = [col.lower() for col in df_expandida.columns]

for metrica in metricas:
    if metrica in df_expandida.columns:
        df_expandida[metrica] = pd.to_numeric(df_expandida[metrica], errors="coerce")

# filtro da expandida
colunas_filtradas_exp = [c for c in colunas_banco_expandida if c in df_expandida.columns]
df_expandida = df_expandida[colunas_filtradas_exp]

df_expandida.to_sql('planilha_oficial_computacao_expandida', engine, schema='dados', if_exists='append', index=False)

print("Concluido com exito\n")