# Cube, API REST e Power BI

O Cube é a camada que fica entre o banco e quem consome os dados. Ele funciona como **tradutor**: o banco guarda cada fonte do jeito que ela veio, e o Cube diz o que cada coluna significa e como calcular cada métrica.

Por isso, quando uma fonte muda, só o modelo do Cube muda. O Power BI e o front-end (Next) continuam pedindo as mesmas métricas.

## Conceitos

| Termo | O que é | Exemplo |
| :--- | :--- | :--- |
| **Cubo** | Uma tabela (ou consulta SQL) com significado. | `inep_cursos` |
| **Medida** (*measure*) | Um número agregado. | `matriculas` (soma), `media_matriculas_por_curso` (média) |
| **Dimensão** (*dimension*) | Um campo para agrupar ou filtrar. | `ano`, `rede`, `uf` |
| **Visão** (*view*) | Um recorte pronto para um público, juntando cubos. | `painel_publico` |

O modelo fica em `cube/model`:

| Arquivo | Conteúdo |
| :--- | :--- |
| `cubes/inep_cursos.yml` | Base principal do INEP (ano/IES/curso). |
| `cubes/inep_localidade.yml` | Base do INEP por município/polo, ligada à principal. |
| `cubes/indicadores.yml` | Junta todas as fontes num vocabulário único. É aqui que entra uma instituição nova. |
| `cubes/metadados.yml` | Expõe o dicionário de dados e a lista de fontes carregadas. |
| `views/painel_publico.yml` | Visões simplificadas para o Power BI. |

Com o modo de desenvolvimento ligado, o Cube recarrega os arquivos sozinho ao serem salvos.

## Playground

Acesse http://localhost:4000 para montar consultas clicando: escolha medidas e dimensões e veja o resultado, o JSON da consulta e o SQL gerado. É o jeito mais rápido de testar o modelo.

## API REST (pesquisadores)

Toda chamada precisa de um token, gerado com o `CUBEJS_API_SECRET` do `.env`:

```bash
python gerar_token_cube.py        # vale 30 dias
python gerar_token_cube.py 365    # vale 1 ano
```

O pesquisador manda uma consulta em JSON e recebe o resultado pronto, sem escrever SQL.

**Exemplo:** matrículas, desvinculados e média de matrículas por curso, por ano.

```bash
curl -G http://localhost:4000/cubejs-api/v1/load \
  -H "Authorization: SEU_TOKEN" \
  --data-urlencode 'query={
    "measures": ["inep_cursos.matriculas", "inep_cursos.desvinculados", "inep_cursos.media_matriculas_por_curso"],
    "dimensions": ["inep_cursos.ano"],
    "order": {"inep_cursos.ano": "desc"}
  }'
```

Resposta (resumida):

```json
{"data": [
  {"inep_cursos.ano": "2024", "inep_cursos.matriculas": "860791",
   "inep_cursos.desvinculados": "315838", "inep_cursos.media_matriculas_por_curso": "221.05"}
]}
```

**Exemplo:** matrículas por UF na rede pública em 2024.

```json
{
  "measures": ["inep_localidade.matriculas"],
  "dimensions": ["inep_localidade.uf"],
  "filters": [
    {"member": "inep_localidade.ano", "operator": "equals", "values": ["2024"]},
    {"member": "inep_cursos.rede", "operator": "equals", "values": ["Pública"]}
  ]
}
```

**Exemplo:** o que significa uma coluna (dicionário).

```json
{"dimensions": ["dicionario.fonte", "dicionario.coluna", "dicionario.descricao"]}
```

Outros endereços úteis:
* `GET /cubejs-api/v1/meta`: lista todos os cubos, medidas e dimensões, com títulos e descrições. Serve como catálogo do que pode ser consultado.
* `fontes` (cubo): quais fontes estão carregadas e quando.

### Uso no front-end (Next)

O Next consulta o Cube da mesma forma, com `fetch` ou com o pacote `@cubejs-client/core`:

```js
import cube from "@cubejs-client/core";

const api = cube(process.env.CUBE_TOKEN, {
  apiUrl: "http://localhost:4000/cubejs-api/v1",
});

const resultado = await api.load({
  measures: ["indicadores.matriculas"],
  dimensions: ["indicadores.ano"],
});
console.log(resultado.tablePivot());
```

O token deve ficar no servidor (Server Components / API Routes do Next), nunca exposto no navegador.

## Power BI (público geral)

O Cube expõe uma API SQL compatível com PostgreSQL. O Power BI conecta nela como se fosse um banco comum e enxerga cada cubo e visão como uma tabela.

1. No Power BI Desktop: **Obter dados → Banco de dados PostgreSQL**.
2. **Servidor:** `localhost:15432` (ou o endereço do servidor). **Banco de dados:** `pesquisa_evasao`.
3. **Modo:** *Importar* (recomendado) ou *DirectQuery*.
4. **Credenciais:** aba *Banco de dados*, com `CUBEJS_SQL_USER` e `CUBEJS_SQL_PASSWORD` do `.env`.
5. Se aparecer um aviso de que a conexão não é criptografada, aceite conectar sem criptografia. A API SQL do Cube não usa SSL; em produção, isso deve ficar atrás de uma rede interna ou VPN.
6. Selecione as tabelas `painel_publico` e/ou `painel_publico_uf`.

No modo *Importar*, o Power BI traz as linhas e faz as somas sozinho.

O limite de linhas do Cube foi aumentado para 1 milhão no `docker-compose.yml`. O padrão é 50 mil, e a visão por município tem cerca de 315 mil linhas, então sem esse ajuste o Power BI importaria só parte dos dados sem avisar.

## Adicionando uma instituição nova

Exemplo: uma instituição que só manda matrícula.

1. **Carregar**: acrescente a fonte no `fontes.yml` e rode `python importar_planilhas.py <nome>`. A tabela `bruto.<tabela>` é criada com as colunas que vieram.
2. **Traduzir**: no `cube/model/cubes/indicadores.yml`, acrescente um `UNION ALL SELECT ...` que renomeia as colunas da fonte para os nomes comuns. O que a fonte não tem entra como `NULL` (há um exemplo comentado no arquivo).
3. **Descrever**: acrescente as colunas ao `dicionario/dicionario.csv`.

Pronto: a métrica `indicadores.matriculas` passa a trazer a nova fonte, e `indicadores.ingressantes` aparece vazia para ela. Nada no Power BI ou no Next precisa mudar.

> O INEP já contém as instituições que mandarem dados próprios. Ao somar `indicadores`, filtre ou agrupe por `fonte` para não contar a mesma matrícula duas vezes.

## Pendências

* **Dicionário do outro grupo**: o `dicionario/dicionario.csv` atual é provisório. Quando o dicionário oficial chegar, ele substitui esse arquivo (ajustando o formato, se precisar), e as descrições também entram nos `title`/`description` do modelo.
* **Average score**: a métrica pedida ainda não existe em nenhuma fonte. O lugar dela está marcado com `TODO` em `indicadores.yml`.
* **Novas fontes**: aguardando os dados das outras instituições.
* **Produção**: desligar `CUBEJS_DEV_MODE`, trocar todas as senhas e definir onde o servidor vai rodar.
