# Guia de Execução e Pipeline

Este documento detalha os passos exatos para replicar a infraestrutura de dados e a API localmente, garantindo a reprodutibilidade da pesquisa.

## 1. Ambiente Virtual e Dependências

Recomenda-se isolar a execução do projeto em um ambiente virtual Python para evitar conflitos de versão. Na raiz do repositório, execute:

```bash
# Criação do ambiente virtual
python -m venv .venv

# Ativação (Windows)
.venv\Scripts\activate
# Ativação (Linux/Mac)
source .venv/bin/activate

# Instalação dos pacotes
pip install pandas sqlalchemy psycopg2-binary fastapi uvicorn
```

## 2. Preparação do Banco de Dados (PostgreSQL)

O armazenamento utiliza o PostgreSQL. Os dados não ficam versionados no repositório.

1. Inicie seu serviço local do PostgreSQL (porta padrão `5432`).
2. Crie um banco de dados denominado `pesquisa_evasao`.
3. Através de um cliente SQL (ex: DBeaver), abra e execute o arquivo `estrutura_banco.sql`. Este comando DDL limpará instâncias anteriores, criará o schema `dados` e estruturará as tabelas e índices necessários.

## 3. Carga de Dados (ETL)

Com o banco preparado, a ingestão das planilhas processadas é feita de forma automatizada pelo script de carga, que faz o download da fonte remota, realiza tipagem via Pandas em memória e insere no banco via SQLAlchemy.

```bash
.venv/Scripts/python importar_planilhas.py
```
*O processo roda de forma silenciosa. Aguarde a finalização no terminal.*

## 4. Inicialização da API

O consumo dos dados estruturados é feito através de uma API RESTful. Para iniciar o servidor de desenvolvimento:

```bash
.venv/Scripts/uvicorn api:app --reload
```

### Consultas e Validação

Com a API em execução, acesse a documentação interativa (Swagger UI) pelo navegador no endereço:
`http://127.0.0.1:8000/docs`

O painel permite a execução direta de *endpoints* de teste (GET), possibilitando a validação das métricas (ingressantes, matrículas, trancamentos, etc.) filtradas por ano, instituição ou curso, retornando payloads no padrão JSON.
