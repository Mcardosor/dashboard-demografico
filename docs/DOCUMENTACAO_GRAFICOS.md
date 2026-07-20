# Documentação dos Gráficos — Dashboard Demográfico

Por que cada gráfico existe, como é calculado e onde está o código.

## 01 · Mapa de Proporção de Idosos por Estado

**Por quê:** primeira leitura visual do envelhecimento populacional — onde a proporção de idosos é mais alta no Brasil.

**Como é calculado:** `src/charts.py::processar_dados()` agrega a população por UF em dois totais: `total` (todas as idades) e `idosos` (idade ≥ 60), então calcula `pct_idosos = idosos / total * 100`. O mapa em si é um `choropleth_mapbox` colorido por essa proporção, casado ao GeoJSON dos estados pela sigla (`featureidkey="properties.sigla"`).

**Código:** `src/charts.py::fig_mapa()`

**Fallback:** se o Mapbox falhar (ex: sem geojson carregado), `app.py` cai para um gráfico de barras horizontal com a mesma métrica, pra nunca deixar a seção vazia.

## 02 · Top estados — % de idosos

**Por quê:** o mapa mostra o padrão geográfico, mas não é fácil ler os valores exatos — essa tabela complementa com o ranking preciso.

**Como é calculado:** ordena `df_idosos` por `pct_idosos` descendente e pega os 15 primeiros (ou menos, se houver menos estados filtrados).

**Código:** `src/utils.py::html_top5()` monta o HTML da tabela; a ordenação acontece em `app.py`.

## 03 · Distribuição por Sexo

**Por quê:** proporção de homens e mulheres na população total (ou só entre os idosos, via toggle).

**Como é calculado:** `src/charts.py::fig_pizza()` agrupa por `sexo` e soma `populacao`. O toggle "Apenas ≥ 60 anos" filtra a base por idade antes de agregar.

**Código:** `src/charts.py::fig_pizza()`

## 04 · Pirâmide Etária

**Por quê:** visão clássica de demografia — a forma da pirâmide (base larga vs. topo largo) indica se a população está envelhecendo ou é predominantemente jovem.

**Como é calculado:** `processar_dados()` cria faixas etárias de 5 em 5 anos (`0-4`, `5-9`, ..., `100+`). O gráfico plota homens como valores negativos e mulheres como positivos, convenção padrão de pirâmide etária, pra ficarem em lados opostos do eixo zero.

**Código:** `src/charts.py::fig_piramide()`

## 05 · Evolução Populacional (2010-2025)

**Por quê:** tendência histórica da população total dos estados selecionados, complementando o retrato de um único ano dado pelos outros gráficos.

**Como é calculado:** `src/data.py::carregar_evolucao()` agrega população total por UF e ano (cacheado como recurso, independente do filtro de ano ativo). `fig_evolucao()` soma só as UFs selecionadas e converte para milhões de habitantes.

**Código:** `src/charts.py::fig_evolucao()`

## 06 · Ranking — Proporção de Idosos por Estado

**Por quê:** mesmo dado do mapa e do Top 15, mas em formato de barra horizontal completo (todos os estados, não só os 15 primeiros) — útil para comparar a distribuição inteira, não só os extremos.

**Como é calculado:** mesma base `df_idosos` do mapa, ordenada ascendente (Plotly desenha barras horizontais de baixo pra cima, então ascendente deixa o maior valor no topo visualmente).

**Código:** `src/charts.py::fig_ranking()`

## KPIs do topo

Os 4 cards (População total, Proporção de idosos, Proporção feminina, Idade média) são calculados em `app.py` sobre `df_filt` (já filtrado pelas UFs selecionadas), com comparação automática ao ano anterior via `src/utils.py::_delta_html()`. Se não houver ano anterior disponível na base, a variação não é exibida.
