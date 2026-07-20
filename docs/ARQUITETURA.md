# Arquitetura — Dashboard Demográfico

Visão de ponta a ponta pra quem for rodar, estender ou dar manutenção neste projeto sem ajuda direta de quem construiu.

## Fluxo de dados

```
IBGE (Projeções de População 2010-2025)
        │
        │  (pipeline de tratamento NÃO está neste repositório —
        │   os .parquet em /data já vêm prontos pra uso)
        ▼
data/pop_ibge.parquet ──┐
data/ibge_municipios.parquet ├─► src/data.py::_carregar_base()
data/ibge_ufs.parquet ──┘        (junta os 3 parquets, normaliza sexo/idade)
        │
        ▼
src/data.py (carregar_dados, carregar_evolucao, anos_disponiveis)
        │  cache via @st.cache_data / @st.cache_resource
        ▼
src/charts.py::processar_dados() ──► deriva faixa etária + recorte de idosos por UF
        │
        ▼
app.py ──► monta sidebar/filtros, chama src/charts.py::fig_*() para cada gráfico,
           src/utils.py para HTML de KPIs/tabelas, src/themes.py para CSS e dark mode
        │
        ▼
Streamlit renderiza no navegador
```

**Limitação conhecida:** o pipeline que transforma os dados brutos do IBGE nos 3 `.parquet` de `data/` não está neste repositório. Pra atualizar os dados (ex: quando o IBGE lançar a projeção de 2026), é preciso reconstruir esse pipeline (fora do escopo deste repo) e substituir os arquivos em `data/`, mantendo o mesmo schema consumido por `_carregar_base()` (colunas: `cod_mun`, `ano`, `idade`, `sexo`, `populacao` em `pop_ibge.parquet`; ver `src/data.py` pros nomes exatos das outras duas tabelas).

## Módulos

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Entrada Streamlit — sidebar, filtros, layout, orquestra os módulos abaixo |
| `src/data.py` | Carregamento e cache dos Parquet (única camada que toca disco) |
| `src/charts.py` | Processamento (`processar_dados`) e construção das figuras Plotly |
| `src/utils.py` | Formatação de números, HTML de KPI cards/tabelas, layout comum dos gráficos |
| `src/themes.py` | Paleta de cores light/dark, CSS global, toggle de tema via JS |

Não há camada de API nem banco de dados — tudo roda no processo do Streamlit, lendo Parquet do disco local.

## Ambiente e variáveis

Nenhuma variável de ambiente é necessária — não há credenciais, banco ou serviço externo. `.streamlit/config.toml` fixa `baseUrlPath = "cenarios/demografico"` (precisa bater com a rota do proxy reverso em produção).

## Deploy

- **Imagem:** `docker-compose.yml` builda a imagem a partir do `Dockerfile` (Python 3.11-slim + Streamlit), com `COPY . .` — o código vai embutido na imagem, não em bind mount (só `data/` é bind-mounted, read-only).
- **Container:** `dashboard-demografico`, porta **8501**.
- **Produção (VM):** `/home/matheusrodrigues/dashboard-demografico/`, exposto via nginx em `https://telessaude.unb.br/cenarios/demografico` (proxy_pass pra `localhost:8501`).
- **Rebuild após mudança de código:** como o código é `COPY`, uma alteração em `app.py`/`src/` exige `docker compose up -d --build` (bind mount não é suficiente pra pegar a mudança).

## Limitações conhecidas

- Pipeline de dados brutos (IBGE → Parquet) não versionado neste repo (ver seção Fluxo de dados acima).
- Sem testes automatizados.
- Cobertura de dados: 2010–2025, por UF (não há recorte municipal na visualização, embora `ibge_municipios.parquet` exista na base).
