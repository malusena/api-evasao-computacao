# API original em FastAPI. continua funcionando, mas a API principal para os
# pesquisadores agora e a do Cube (ver docs/03_cube_e_power_bi.md)
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from config import criar_engine


# inicializa a API
app = FastAPI(
    title="API - Evasão em Ciência da Computação",
    description="API para análise de dados do Censo da Educação Superior"
)

# conexão com o banco (configurada no .env)
engine = criar_engine()

@app.get("/")
def raiz():
    return {"mensagem": "API da pesquisa rodando com sucesso!"}

@app.get("/estatisticas/{ano}")
def obter_estatisticas_por_ano(ano: int):
    # desvinculados e um fluxo anual, nao uma taxa de evasao (ver docs/01_visao_geral.md)
    query = text("""
        SELECT 
            nu_ano_censo AS ano,
            SUM(qt_mat) AS total_matriculas,
            SUM(qt_sit_desvinculado) AS total_desvinculados,
            SUM(qt_conc) AS total_concluintes
        FROM bruto.inep_computacao
        WHERE nu_ano_censo = :ano
        GROUP BY nu_ano_censo;
    """)
    
    with engine.connect() as conn:
        resultado = conn.execute(query, {"ano": ano}).mappings().first()
        
    if resultado:
        return dict(resultado)
        
    raise HTTPException(status_code=404, detail="Nenhum dado encontrado para o ano informado. Tente um ano entre 2009 e 2024.")
