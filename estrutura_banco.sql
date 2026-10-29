-- estrutura minima do banco
-- as tabelas de dados NAO sao definidas aqui: o importar_planilhas.py cria uma tabela
-- por fonte no schema "bruto" com as colunas que vierem no arquivo.
-- quem traduz essas colunas para metricas e o Cube (pasta cube/model).

CREATE SCHEMA IF NOT EXISTS bruto; -- dados como vieram de cada fonte
CREATE SCHEMA IF NOT EXISTS meta;  -- informacoes sobre os dados


-- registro de cada fonte carregada (preenchido pelo importador)
CREATE TABLE IF NOT EXISTS meta.fontes (
    nome VARCHAR(100) PRIMARY KEY,
    instituicao VARCHAR(255),
    descricao TEXT,
    origem TEXT,
    tabela VARCHAR(100) NOT NULL,
    qt_linhas BIGINT,
    colunas TEXT,
    carregado_em TIMESTAMP DEFAULT now()
);

-- dicionario de dados (fonte + coluna -> significado)
CREATE TABLE IF NOT EXISTS meta.dicionario (
    fonte VARCHAR(100) NOT NULL,
    coluna VARCHAR(100) NOT NULL,
    nome_exibicao VARCHAR(255),
    descricao TEXT,
    CONSTRAINT pk_dicionario PRIMARY KEY (fonte, coluna)
);
