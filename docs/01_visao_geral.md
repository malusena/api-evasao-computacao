# Visão Geral da Base Oficial

## Objetivo

Este projeto organiza e disponibiliza os Microdados do Censo da Educação Superior do INEP focados especificamente em cursos de Computação, integrando indicadores institucionais e acadêmicos.

A arquitetura transforma dados tabulares estáticos em uma estrutura relacional (PostgreSQL) dinâmica, facilitando o cruzamento de variáveis de evasão para a pesquisa desenvolvida no IFB.

## Recorte de Computação

Nos anos classificados por CINE ou CINE Brasil (2009-2016, 2018-2024), um curso ingressa na base quando atende a pelo menos uma das regras abaixo:

* `CO_CINE_AREA_GERAL = 6`: Seleciona a área geral de Computação e Tecnologias da Informação e Comunicação (TIC).
* `CO_CINE_ROTULO = 0714E04`: Inclui especificamente a Engenharia de Computação, que metodologicamente foi incorporada ao escopo da pesquisa, embora classificada nativamente na área geral 7.

### A Exceção de 2017 (Aproximação OCDE)

O Censo de 2017 utiliza a classificação OCDE. Para manter a série histórica ininterrupta e aproximar o mesmo universo de análise, foram incluídos cursos onde:
* `CO_OCDE_AREA_ESPECIFICA = 48` (Ex: Ciência da computação, Análise de sistemas)
* ou `CO_OCDE = 5.23E+06` (Proxy histórico para Engenharia de Computação)

Nesses casos, a tabela no banco de dados armazena as *flags* `DS_CLASSIFICACAO_AREA = OCDE` e `DS_NIVEL_COMPARABILIDADE = media_ocde_proxy`, indicando equivalência por aproximação.

## Modelagem de Dados

A arquitetura de dados opera inteiramente dentro do schema `dados`, separando a carga analítica do schema `public` padrão do PostgreSQL. 

A estrutura é dividida em:
1. **Tabela Principal (`planilha_oficial_computacao`)**: Base central recomendada para análises de séries históricas. Possui chave composta primária (`nu_ano_censo`, `co_ies`, `co_curso`) garantindo a integridade referencial.
2. **Tabela Expandida (`planilha_oficial_computacao_expandida`)**: Preserva a granularidade territorial original dos dados. Recomendada exclusivamente para consultas geográficas e dimensionamento espacial, relacionando-se à tabela principal via chave estrangeira.

## Indicadores de Evasão e Desvinculação

As variáveis acadêmicas (`QT_MAT`, `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO`) representam métricas brutas fornecidas pelo INEP. 

**Nota Metodológica:** A antiga razão matemática de *desvinculados/matrículas* não é calculada diretamente pelo banco de dados ou pela API, pois compara um fluxo anual com um estoque e pode produzir valores distorcidos.
