from fastapi import FastAPI
from sqlalchemy import create_engine, text


# inicializa a API
app = FastAPI(
    title="API - Evasão em Ciência da Computação",
    description="API para análise de dados do Censo da Educação Superior"
)

# conexão com o banco local
engine = create_engine('postgresql://postgres:admin@localhost:5432/pesquisa_evasao')

@app.get("/")
def raiz():
    return {"mensagem": "API da pesquisa rodando com sucesso!"}

@app.get("/estatisticas/{ano}")
def obter_estatisticas_por_ano(ano: int):
    # consulta SQL que vai direto na tabela principal
    query = text("""
        SELECT 
            nu_ano_censo AS ano,
            SUM(qt_mat) AS total_matriculas,
            SUM(qt_sit_desvinculado) AS total_evasao,
            SUM(qt_conc) AS total_concluintes
        FROM dados.planilha_oficial_computacao
        WHERE nu_ano_censo = :ano
        GROUP BY nu_ano_censo;
    """)
    
    with engine.connect() as conn:
        resultado = conn.execute(query, {"ano": ano}).mappings().first()
        
    if resultado:
        return dict(resultado)
        
    return {"erro": "Nenhum dado encontrado para o ano informado. Tente um ano entre 2009 e 2024."}