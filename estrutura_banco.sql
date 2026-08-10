DROP SCHEMA IF EXISTS dados CASCADE; -- limpa qualquer tentativa que deu erro antes, nao mexer!!
CREATE SCHEMA dados;


CREATE TABLE dados.planilha_oficial_computacao (
    nu_ano_censo SMALLINT NOT NULL,
    co_ies VARCHAR(50) NOT NULL,
    no_ies VARCHAR(255),
    sg_ies VARCHAR(50), 
    co_curso VARCHAR(50) NOT NULL,
    
    co_cine_area_geral VARCHAR(50),
    no_cine_area_geral VARCHAR(255),
    co_cine_rotulo VARCHAR(50),
    no_cine_rotulo VARCHAR(255),
    co_ocde_area_especifica VARCHAR(50),
    co_ocde VARCHAR(50),
    ds_classificacao_area VARCHAR(100),
    ds_nivel_comparabilidade VARCHAR(100),
    
    qt_ufs_distintas SMALLINT,
    sg_uf_lista VARCHAR(255),
    
    qt_vg_total INT,
    qt_inscrito_total INT,
    qt_ing INT,
    qt_mat INT,
    qt_conc INT,
    qt_sit_trancada INT,
    qt_sit_desvinculado INT,
    qt_sit_transferido INT,
    qt_sit_falecido INT,
    
    CONSTRAINT pk_planilha_oficial PRIMARY KEY (nu_ano_censo, co_ies, co_curso)
);

CREATE TABLE dados.planilha_oficial_computacao_expandida (
    id_expandida BIGSERIAL PRIMARY KEY,
    nu_ano_censo SMALLINT NOT NULL,
    co_ies VARCHAR(50) NOT NULL,
    co_curso VARCHAR(50) NOT NULL,
    tp_dimensao VARCHAR(100),
    sg_uf VARCHAR(2),
    no_municipio VARCHAR(255),
    
    qt_vg_total INT,
    qt_inscrito_total INT,
    qt_ing INT,
    qt_mat INT,
    qt_conc INT,
    qt_sit_trancada INT,
    qt_sit_desvinculado INT,
    qt_sit_transferido INT,
    qt_sit_falecido INT,
    
    CONSTRAINT fk_curso_principal FOREIGN KEY (nu_ano_censo, co_ies, co_curso)
        REFERENCES dados.planilha_oficial_computacao (nu_ano_censo, co_ies, co_curso)
        ON DELETE CASCADE
);

CREATE INDEX idx_ano_censo ON dados.planilha_oficial_computacao(nu_ano_censo);
CREATE INDEX idx_cod_ies ON dados.planilha_oficial_computacao(co_ies);
CREATE INDEX idx_rotulo_cine ON dados.planilha_oficial_computacao(co_cine_rotulo);
CREATE INDEX idx_expandida_uf ON dados.planilha_oficial_computacao_expandida(sg_uf);