"""Carrega cada fonte do fontes.yml no schema "bruto" do banco.

Uso:
    python importar_planilhas.py                # todas as fontes
    python importar_planilhas.py inep_computacao  # so uma
"""
import csv
import fnmatch
import io
import sys
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import text

from config import criar_engine


PASTA = Path(__file__).parent


def inserir_com_copy(tabela, conn, colunas, linhas):
    # usa o COPY do postgres, bem mais rapido que INSERT para planilhas grandes
    buffer = io.StringIO()
    csv.writer(buffer).writerows(linhas)
    buffer.seek(0)
    nomes = ", ".join(f'"{c}"' for c in colunas)
    with conn.connection.cursor() as cursor:
        cursor.copy_expert(f'COPY {tabela.schema}."{tabela.name}" ({nomes}) FROM STDIN WITH CSV', buffer)


def ler_arquivo(fonte):
    origem = fonte["origem"]
    if origem.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(origem, dtype=str)
    else:
        df = pd.read_csv(
            origem,
            sep=fonte.get("separador", ";"),
            encoding=fonte.get("encoding", "utf-8-sig"),
            dtype=str,
            low_memory=False,
        )
    # nomes de coluna padronizados: minusculo, sem espacos
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def converter_numericas(df, padroes):
    for coluna in df.columns:
        if any(fnmatch.fnmatch(coluna, p) for p in padroes):
            valores = pd.to_numeric(df[coluna], errors="coerce")
            # "45.0" vira 45 quando a coluna inteira for de inteiros
            if (valores.dropna() % 1 == 0).all():
                valores = valores.astype("Int64")
            df[coluna] = valores
    return df


def carregar_fonte(engine, fonte):
    tabela = fonte["tabela"]
    print(f"[{fonte['nome']}] lendo {fonte['origem']}")
    df = ler_arquivo(fonte)
    df = converter_numericas(df, fonte.get("numericas", []))

    chave = fonte.get("chave")
    if chave:
        faltando = [c for c in chave if c not in df.columns]
        if faltando:
            raise ValueError(f"colunas da chave nao existem no arquivo: {faltando}")
        repetidas = df.duplicated(subset=chave).sum()
        if repetidas:
            raise ValueError(f"{repetidas} linhas repetidas para a chave {chave}")
    else:
        chave = ["id_linha"]
        df.insert(0, "id_linha", range(1, len(df) + 1))

    # replace: a tabela e recriada com as colunas que vieram, sem estrutura fixa
    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS bruto."{tabela}" CASCADE'))
        df.to_sql(tabela, conn, schema="bruto", index=False, method=inserir_com_copy)

        colunas_chave = ", ".join(f'"{c}"' for c in chave)
        conn.execute(text(f'ALTER TABLE bruto."{tabela}" ADD PRIMARY KEY ({colunas_chave})'))
        for coluna in fonte.get("indices", []):
            if coluna in df.columns:
                conn.execute(text(f'CREATE INDEX ON bruto."{tabela}" ("{coluna}")'))

        conn.execute(
            text("""
                INSERT INTO meta.fontes (nome, instituicao, descricao, origem, tabela, qt_linhas, colunas, carregado_em)
                VALUES (:nome, :instituicao, :descricao, :origem, :tabela, :qt_linhas, :colunas, now())
                ON CONFLICT (nome) DO UPDATE SET
                    instituicao = EXCLUDED.instituicao, descricao = EXCLUDED.descricao,
                    origem = EXCLUDED.origem, tabela = EXCLUDED.tabela, qt_linhas = EXCLUDED.qt_linhas,
                    colunas = EXCLUDED.colunas, carregado_em = now()
            """),
            {
                "nome": fonte["nome"],
                "instituicao": fonte.get("instituicao"),
                "descricao": fonte.get("descricao"),
                "origem": fonte["origem"],
                "tabela": tabela,
                "qt_linhas": len(df),
                "colunas": ", ".join(df.columns),
            },
        )
    print(f"[{fonte['nome']}] {len(df)} linhas em bruto.{tabela}")


def carregar_dicionario(engine, caminho):
    df = pd.read_csv(PASTA / caminho, sep=";", encoding="utf-8-sig", dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE meta.dicionario"))
        df.to_sql("dicionario", conn, schema="meta", if_exists="append", index=False)
    print(f"[dicionario] {len(df)} colunas descritas")


def main():
    with open(PASTA / "fontes.yml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    escolhidas = sys.argv[1:]
    fontes = [f for f in config["fontes"] if not escolhidas or f["nome"] in escolhidas]

    engine = criar_engine()
    for fonte in fontes:
        carregar_fonte(engine, fonte)
    if config.get("dicionario"):
        carregar_dicionario(engine, config["dicionario"])

    print("Concluido com exito\n")


if __name__ == "__main__":
    main()
