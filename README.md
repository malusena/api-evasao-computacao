# API e Infraestrutura de Dados: Evasão em Cursos de Computação

Este repositório contém a arquitetura de dados local e a API RESTful desenvolvidas para dar suporte quantitativo à pesquisa de evasão acadêmica nos cursos de Ciência da Computação no Brasil.

O objetivo desta etapa técnica é consumir as planilhas finais tratadas do Censo da Educação Superior (INEP), estruturá-las em um banco de dados relacional e disponibilizar os indicadores acadêmicos via API para análise.

## Base Oficial e Recorte Metodológico

A série histórica consumida pela API cobre os anos de 2009 a 2024. Os dados originais seguem o recorte metodológico baseado na classificação CINE/CINE Brasil, integrando cursos onde:
* `CO_CINE_AREA_GERAL = 6` (Computação e Tecnologias da Informação e Comunicação)
* ou `CO_CINE_ROTULO = 0714E04` (Engenharia de Computação)

Para o ano de 2017, que adota a classificação OCDE, foi aplicada uma aproximação de compatibilidade descrita na documentação de visão geral.

## Estrutura do Repositório

Os arquivos que compõem o pipeline de extração, armazenamento e disponibilização ficam na raiz do repositório:

| Arquivo | Finalidade |
| :--- | :--- |
| `estrutura_banco.sql` | Arquitetura DDL do banco; cria o esquema `dados`, tabelas e índices. |
| `importar_planilhas.py` | Pipeline de extração e carga (ETL); baixa os microdados em CSV e popula o PostgreSQL. |
| `api.py` | Backend em FastAPI que expõe os indicadores de evasão para consulta. |
| `diagrama.png` | Modelagem visual de Entidade-Relacionamento do banco de dados local. |

*Nota: Os arquivos originais em formato CSV possuem volumes elevados e não são versionados neste repositório. O script em Python realiza o consumo remoto dinamicamente.*

## Como Reproduzir

Com o ambiente virtual configurado e o PostgreSQL rodando localmente com o banco `pesquisa_evasao` devidamente estruturado via script SQL:

```bash
# 1. Popular o banco de dados
.venv/Scripts/python importar_planilhas.py

# 2. Iniciar o servidor da API
.venv/Scripts/uvicorn api:app --reload
```

## Documentação Completa

Para aprofundamento técnico e metodológico, consulte o diretório `/docs`:
* [Visão Geral e Metodologia](docs/01_visao_geral.md)
* [Guia de Execução e Pipeline](docs/02_guia_de_execucao.md)
