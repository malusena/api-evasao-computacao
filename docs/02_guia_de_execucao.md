# Guia de Execução e Pipeline

Este documento detalha os passos para replicar a infraestrutura de dados e as APIs, garantindo a reprodutibilidade da pesquisa.

## 1. Configuração

Copie o arquivo de exemplo e troque as senhas:

```bash
cp .env.example .env
```

O `.env` não é versionado. Ele é lido pelo Docker Compose e pelos scripts Python.

Por padrão, o PostgreSQL fica na porta `5433` do computador, para não conflitar com um PostgreSQL já instalado na `5432`.

## 2. Banco de Dados e Cube (Docker)

```bash
docker compose up -d
```

Esse comando sobe dois serviços:
* **postgres**: na primeira execução, roda o `estrutura_banco.sql`, que cria os schemas `bruto` e `meta`.
* **cube**: lê o modelo da pasta `cube/model` e expõe a API REST (porta `4000`) e a API SQL para o Power BI (porta `15432`).

Para recriar o banco do zero (apaga os dados):

```bash
docker compose down -v
```

## 3. Ambiente Python

```bash
python -m venv .venv

# Ativação (Windows)
.venv\Scripts\activate
# Ativação (Linux/Mac)
source .venv/bin/activate

pip install -r requirements.txt
```

## 4. Carga de Dados (ETL)

```bash
python importar_planilhas.py                  # todas as fontes
python importar_planilhas.py inep_computacao  # só uma fonte
```

Para cada fonte listada no `fontes.yml`, o script:
1. baixa o arquivo (URL ou caminho local, CSV ou Excel);
2. padroniza os nomes das colunas (minúsculo, sem espaços);
3. converte para número as colunas indicadas em `numericas`;
4. confere se a `chave` não tem linhas repetidas;
5. recria a tabela em `bruto.<tabela>` com as colunas que vieram no arquivo, mais chave primária e índices;
6. registra a carga em `meta.fontes`.

No fim, o script carrega o `dicionario/dicionario.csv` em `meta.dicionario`.

A carga pode ser repetida quantas vezes for preciso: cada execução substitui os dados da fonte.

### Adicionando uma fonte nova

1. Acrescente um bloco no `fontes.yml` (há um exemplo comentado).
2. Rode `python importar_planilhas.py <nome_da_fonte>`.
3. Descreva as colunas no `dicionario/dicionario.csv`.
4. No Cube, acrescente a fonte ao cubo `indicadores` (`cube/model/cubes/indicadores.yml`) e, se precisar de métricas específicas, crie um cubo próprio. Veja [Cube, API REST e Power BI](03_cube_e_power_bi.md).

## 5. API FastAPI (legado)

A API original continua disponível:

```bash
uvicorn api:app --reload
```

Documentação interativa: `http://127.0.0.1:8000/docs`. O endpoint `/estatisticas/{ano}` retorna matrículas, desvinculados e concluintes do ano.

Para novas consultas, use a API do Cube, que não exige escrever SQL nem alterar código.
