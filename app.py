import streamlit as st

from src.themes import THEMES, _css
from src.data import anos_disponiveis, carregar_dados, carregar_evolucao, carregar_geojson
from src.charts import processar_dados, fig_mapa, fig_pizza, fig_piramide, fig_ranking, fig_evolucao
from src.utils import PLOTLY_CFG, _fmt, _delta_html, kpi_card

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard Demográfico | UF", page_icon="🗺️", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

GEOJSON = carregar_geojson()

# ── Sidebar ───────────────────────────────────────────────────────────────────
_anos = anos_disponiveis()

with st.sidebar:
    st.markdown("## 🎛️ Filtros")
    st.markdown("---")

    if st.button(
        f"{THEMES[st.session_state.theme]['toggle_icon']}  {THEMES[st.session_state.theme]['toggle_label']}",
        use_container_width=True,
    ):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("---")

    ano_sel = st.selectbox(
        "Ano de referência:",
        options=_anos,
        index=0,
        help="2025 é o padrão. Anos disponíveis: 2010–2025.",
    )
    ano_ant = _anos[_anos.index(ano_sel) + 1] if _anos.index(ano_sel) + 1 < len(_anos) else None

t = THEMES[st.session_state.theme]
st.markdown(_css(t), unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
df_raw             = carregar_dados(ano_sel)
df_proc, df_idosos = processar_dados(df_raw)
df_evo             = carregar_evolucao()

df_ant                       = carregar_dados(ano_ant) if ano_ant else None
df_proc_ant, df_idosos_ant   = processar_dados(df_ant) if df_ant is not None else (None, None)

pop_total = int(df_proc["populacao"].sum())
n_ufs     = df_proc["uf"].nunique()

with st.sidebar:
    ufs_disponiveis = sorted(df_proc["uf"].unique().tolist())
    ufs_sel = st.multiselect("Estados (UF):", options=ufs_disponiveis, default=ufs_disponiveis)
    if not ufs_sel:
        ufs_sel = ufs_disponiveis

    filtrar_idosos_pizza = st.checkbox("Sexo apenas para ≥ 60 anos", value=False)

    st.markdown("---")
    st.caption(f"📊 **{pop_total:,}** hab. · **{n_ufs}** estados\nFonte: IBGE · {ano_sel}")

# ── Métricas filtradas ────────────────────────────────────────────────────────
df_filt    = df_proc[df_proc["uf"].isin(ufs_sel)]
df_id_filt = df_idosos[df_idosos["uf"].isin(ufs_sel)]

pop_filt       = int(df_filt["populacao"].sum())
pct_fem_filt   = (df_filt[df_filt["sexo"] == "F"]["populacao"].sum() / pop_filt * 100) if pop_filt else 0
pct_idog_filt  = (df_filt[df_filt["idade"] >= 60]["populacao"].sum() / pop_filt * 100) if pop_filt else 0
idade_med_filt = ((df_filt["idade"] * df_filt["populacao"]).sum() / pop_filt) if pop_filt else 0

if df_proc_ant is not None:
    df_filt_ant  = df_proc_ant[df_proc_ant["uf"].isin(ufs_sel)]
    pop_ant      = int(df_filt_ant["populacao"].sum())
    pct_idog_ant = (df_filt_ant[df_filt_ant["idade"] >= 60]["populacao"].sum() / pop_ant * 100) if pop_ant else 0
    pct_fem_ant  = (df_filt_ant[df_filt_ant["sexo"] == "F"]["populacao"].sum() / pop_ant * 100) if pop_ant else 0
    idade_ant    = ((df_filt_ant["idade"] * df_filt_ant["populacao"]).sum() / pop_ant) if pop_ant else 0
else:
    pop_ant = pct_idog_ant = pct_fem_ant = idade_ant = 0

# ── Hero ──────────────────────────────────────────────────────────────────────
_label_ufs = (
    "Todos os estados" if len(ufs_sel) == n_ufs
    else f"{len(ufs_sel)} estado{'s' if len(ufs_sel)>1 else ''} selecionado{'s' if len(ufs_sel)>1 else ''}"
)

st.markdown(f"""
<div class="hero">
  <h1 class="hero-title">
    <span class="hero-emoji">🗺️</span>
    <span>Dashboard Demográfico — Brasil por UF</span>
  </h1>
  <p class="hero-subtitle">
    Análise demográfica com distribuição etária, proporção de idosos,
    pirâmide populacional e evolução histórica — recorte por estado.
  </p>
  <div class="hero-badges">
    <span class="hero-badge accent"><span class="dot"></span>{_label_ufs}</span>
    <span class="hero-badge success"><span class="dot"></span>{_fmt(pop_filt)} pessoas</span>
    <span class="hero-badge"><span class="dot"></span>Fonte: IBGE</span>
    <span class="hero-badge"><span class="dot"></span>Ano {ano_sel}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
kpi_data = [
    ("👥", "População total",     _fmt(pop_filt),             f"{len(ufs_sel)} estado(s)",  _delta_html(pop_filt, pop_ant)),
    ("👴", "Proporção de idosos", f"{pct_idog_filt:.1f}%",    "≥ 60 anos",                  _delta_html(pct_idog_filt, pct_idog_ant)),
    ("♀️", "Proporção feminina",  f"{pct_fem_filt:.1f}%",     "sobre o total",              _delta_html(pct_fem_filt, pct_fem_ant)),
    ("📅", "Idade média",         f"{idade_med_filt:.1f} anos","média ponderada",            _delta_html(idade_med_filt, idade_ant)),
]

cols = st.columns(4)
for col, (icon, title, value, sub, delta) in zip(cols, kpi_data):
    with col:
        st.markdown(kpi_card(title, value, sub, icon, delta), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Mapa + Pizza ──────────────────────────────────────────────────────────────
col_mapa, col_pizza = st.columns([3, 2], gap="large")

with col_mapa:
    st.subheader("🗺️ Proporção de Idosos por Estado")
    st.caption("Percentual da população com **60 anos ou mais** em cada estado.")
    try:
        st.plotly_chart(fig_mapa(df_id_filt, t, GEOJSON), use_container_width=True, config=PLOTLY_CFG)
    except Exception:
        import plotly.express as px
        from src.utils import H_LARGE
        fig_bar = px.bar(
            df_id_filt.sort_values("pct_idosos"),
            x="pct_idosos", y="uf", orientation="h",
            color="pct_idosos", color_continuous_scale="YlOrRd",
            labels={"pct_idosos": "% Idosos", "uf": "Estado"},
        )
        from src.charts import _apply_layout
        _apply_layout(fig_bar, t, H_LARGE)
        fig_bar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CFG)

with col_pizza:
    _titulo_pizza = (
        "🍕 Distribuição por Sexo — Idosos (≥ 60)" if filtrar_idosos_pizza
        else "🍕 Distribuição por Sexo — Total"
    )
    st.subheader(_titulo_pizza)
    st.caption(
        "Filtro ativo: apenas maiores de 60 anos." if filtrar_idosos_pizza
        else "Exibindo toda a população selecionada."
    )
    st.plotly_chart(fig_pizza(df_filt, t, filtrar_idosos_pizza), use_container_width=True, config=PLOTLY_CFG)

    st.markdown("**Top 5 estados — % de idosos:**")
    top5 = (
        df_id_filt[["uf", "pct_idosos", "idosos", "total"]]
        .sort_values("pct_idosos", ascending=False).head(5)
        .rename(columns={"uf":"UF","pct_idosos":"% Idosos","idosos":"Idosos","total":"Total"})
        .reset_index(drop=True)
    )
    top5.index = range(1, 6)
    top5["% Idosos"] = top5["% Idosos"].map("{:.2f}%".format)
    top5["Idosos"]   = top5["Idosos"].map("{:,.0f}".format)
    top5["Total"]    = top5["Total"].map("{:,.0f}".format)
    st.dataframe(top5, use_container_width=True, height=210)

st.divider()

# ── Pirâmide etária ───────────────────────────────────────────────────────────
st.subheader("📊 Pirâmide Etária — Distribuição por Faixa (5 em 5 anos) e Sexo")
st.caption(
    "Eixo esquerdo → masculino (azul). Eixo direito → feminino (rosa). "
    "Base larga = população jovem; topo largo = população envelhecida."
)
st.plotly_chart(fig_piramide(df_filt, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ── Evolução histórica ────────────────────────────────────────────────────────
st.subheader("📈 Evolução Populacional — 2010 a 2025")
st.caption(
    "Total de habitantes nos estados selecionados ao longo dos anos. "
    "Use o filtro de UFs na sidebar para comparar regiões."
)
st.plotly_chart(fig_evolucao(df_evo, ufs_sel, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ── Ranking ───────────────────────────────────────────────────────────────────
st.subheader("🏆 Ranking de Estados — Proporção de Idosos")
st.caption("Estados ordenados pela proporção de pessoas com 60+ anos sobre o total.")
st.plotly_chart(fig_ranking(df_id_filt, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;padding:18px 0 8px;color:{t['footer']};font-size:.78rem'>"
    f"Dashboard Demográfico · Fonte: IBGE {ano_sel} · cenarios_ai"
    f"</div>",
    unsafe_allow_html=True,
)
