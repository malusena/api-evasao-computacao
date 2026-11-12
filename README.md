# API e Infraestrutura de Dados: Evasão em Cursos de Computação

Este repositório contém a arquitetura de dados e as APIs desenvolvidas para dar suporte quantitativo à pesquisa de evasão acadêmica nos cursos de Ciência da Computação no Brasil.

O objetivo desta etapa é consumir dados de fontes variadas (a começar pelas planilhas tratadas do Censo da Educação Superior do INEP), guardá-los em um banco PostgreSQL e entregá-los "mastigados" por meio do **Cube**, que funciona como tradutor entre os dados brutos e quem consome:

* **Pesquisadores**: API REST do Cube, com respostas em JSON.
* **Público geral**: Power BI, conectado à API SQL do Cube.

## Arquitetura

```
Fontes (INEP, outras instituições...)
        │  importar_planilhas.py + fontes.yml
        ▼
PostgreSQL  (schema "bruto": uma tabela por fonte, do jeito que veio
             schema "meta":  fontes carregadas e dicionário de dados)
        │
        ▼
Cube  (cube/model: traduz colunas cruas em métricas com nome e significado)
        ├── API REST/JSON  :4000   → pesquisadores, front-end Next
        └── API SQL        :15432  → Power BI
```

Quando uma fonte nova chega ou uma coluna muda de nome, só o importador (`fontes.yml`) e o modelo do Cube mudam. O Power BI e o front-end continuam pedindo as mesmas métricas.

## Base Oficial e Recorte Metodológico

A série histórica do INEP cobre os anos de 2009 a 2024. Os dados originais seguem o recorte metodológico baseado na classificação CINE/CINE Brasil, integrando cursos onde:
* `CO_CINE_AREA_GERAL = 6` (Computação e Tecnologias da Informação e Comunicação)
* ou `CO_CINE_ROTULO = 0714E04` (Engenharia de Computação)

Para o ano de 2017, que adota a classificação OCDE, foi aplicada uma aproximação de compatibilidade descrita na documentação de visão geral.

## Estrutura do Repositório

| Arquivo | Finalidade |
| :--- | :--- |
| `docker-compose.yml` | Sobe o PostgreSQL e o Cube. |
| `.env.example` | Modelo das senhas e configurações (copiar para `.env`). |
| `estrutura_banco.sql` | Cria os schemas `bruto` e `meta`. As tabelas de dados são criadas pelo importador. |
| `fontes.yml` | Lista das fontes de dados a carregar. É aqui que entra uma instituição nova. |
| `importar_planilhas.py` | Carrega cada fonte do `fontes.yml` no schema `bruto` e o dicionário no `meta`. |
| `dicionario/dicionario.csv` | Dicionário de dados (provisório, até receber o do outro grupo). |
| `cube/model/` | Modelo do Cube: métricas, dimensões e visões para o Power BI. |
| `gerar_token_cube.py` | Gera o token de acesso à API REST do Cube. |
| `api.py` | API original em FastAPI (mantida; a API principal agora é a do Cube). |
| `diagrama.png` | Modelagem antiga (schema `dados`), mantida como histórico. |

*Nota: os arquivos CSV originais têm volume elevado e não são versionados neste repositório. O importador baixa os dados direto da fonte.*

## Como Reproduzir

Requisitos: Docker e Python 3.

```bash
cp .env.example .env          # depois edite as senhas
docker compose up -d          # sobe PostgreSQL + Cube
pip install -r requirements.txt
python importar_planilhas.py  # carrega os dados (~30 s)
```

Depois disso:
* Playground do Cube: http://localhost:4000
* API REST: `http://localhost:4000/cubejs-api/v1/load`
* Power BI: servidor `localhost:15432`

## Documentação Completa

Consulte o diretório `/docs`:
* [Visão Geral e Metodologia](docs/01_visao_geral.md)
* [Guia de Execução e Pipeline](docs/02_guia_de_execucao.md)
* [Cube, API REST e Power BI](docs/03_cube_e_power_bi.md)
