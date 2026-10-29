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

O banco foi pensado para receber dados de várias instituições, cada uma com um conjunto diferente de informações (uma pode mandar só matrícula, outra matrícula e outros dados). Por isso, nenhuma estrutura de colunas fica fixa no banco:

1. **Schema `bruto`**: uma tabela por fonte, com as colunas exatamente como vieram no arquivo. As tabelas são criadas pelo `importar_planilhas.py` a partir do `fontes.yml`. Hoje existem:
   * `bruto.inep_computacao`: base principal do INEP, um registro por ano/IES/curso, com chave primária (`nu_ano_censo`, `co_ies`, `co_curso`). Recomendada para séries históricas.
   * `bruto.inep_computacao_localidade`: a mesma base aberta por município/polo EaD. As métricas são repartidas entre as linhas, então a soma por UF bate com o total nacional. Recomendada para consultas geográficas.
2. **Schema `meta`**: `meta.fontes` registra cada fonte carregada (origem, quantidade de linhas, colunas, data da carga) e `meta.dicionario` guarda o significado de cada coluna.
3. **Cube** (`cube/model`): é a camada que dá nome e significado aos dados. Cada fonte tem um cubo próprio, e o cubo `indicadores` junta todas as fontes num vocabulário único (`matriculas`, `ingressantes`, `concluintes`...). Métricas que uma fonte não fornece aparecem como vazias (null).

## Indicadores de Evasão e Desvinculação

As variáveis acadêmicas (`QT_MAT`, `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO`) representam métricas brutas fornecidas pelo INEP. 

**Nota Metodológica:** A antiga razão matemática de *desvinculados/matrículas* não é calculada diretamente pelo banco de dados, pela API ou pelo Cube, pois compara um fluxo anual com um estoque e pode produzir valores distorcidos.
