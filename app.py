"""
app.py — Dashboard Demográfico | Dados Populacionais por UF
Dados reais IBGE via PostgreSQL (cenarios_ai).
"""

import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
#  GEOJSON
# ══════════════════════════════════════════════════════════════════════════════
_GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "brazil-states.geojson")
with open(_GEOJSON_PATH, encoding="utf-8") as _f:
    GEOJSON = json.load(_f)

PLOTLY_CFG = {"displayModeBar": False, "scrollZoom": False}
H_SMALL, H_MEDIUM, H_LARGE = 320, 420, 520
COLOR_M, COLOR_F = "#58a6ff", "#f778ba"

# ══════════════════════════════════════════════════════════════════════════════
#  TEMAS
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "bg":          "#0d1117",
        "bg_card":     "rgba(22,27,34,.92)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#c9d1d9",
        "text_title":  "#f0f6fc",
        "text_muted":  "#8b949e",
        "border":      "#30363d",
        "border_hero": "#30363d",
        "grid":        "#21262d",
        "accent":      "#58a6ff",
        "success":     "#7ee787",
        "hero_bg":     "linear-gradient(135deg,#161b22 0%,#0d1117 60%,#112240 100%)",
        "map_line":    "#30363d",
        "bar_line":    "#0d1117",
        "footer":      "#484f58",
        "toggle_icon": "☀️",
        "toggle_label":"Modo claro",
    },
    "light": {
        "bg":          "#f6f8fa",
        "bg_card":     "rgba(255,255,255,.95)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#24292f",
        "text_title":  "#1f2328",
        "text_muted":  "#57606a",
        "border":      "#d0d7de",
        "border_hero": "#d0d7de",
        "grid":        "#eaecef",
        "accent":      "#0969da",
        "success":     "#1a7f37",
        "hero_bg":     "linear-gradient(135deg,#ffffff 0%,#f6f8fa 60%,#dce8f8 100%)",
        "map_line":    "#d0d7de",
        "bar_line":    "#f6f8fa",
        "footer":      "#8c959f",
        "toggle_icon": "🌙",
        "toggle_label":"Modo escuro",
    },
}


def _css(t: dict) -> str:
    return f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', sans-serif; }}
  .stApp {{ background: {t['bg']}; color: {t['text']}; }}

  .hero {{
    background: {t['hero_bg']};
    border: 1px solid {t['border_hero']};
    border-radius: 14px;
    padding: 32px 36px 28px;
    margin-bottom: 28px;
  }}
  .hero-title {{
    font-size: 2rem; font-weight: 700; color: {t['text_title']};
    display: flex; align-items: center; gap: 12px; margin: 0 0 8px;
  }}
  .hero-emoji {{ font-size: 2.2rem; }}
  .hero-subtitle {{ color: {t['text_muted']}; font-size: .97rem; max-width: 720px; margin: 0 0 18px; }}
  .hero-badges {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .hero-badge {{
    background: rgba(128,128,128,.1); border: 1px solid {t['border']};
    border-radius: 20px; padding: 4px 14px; font-size: .78rem;
    color: {t['text_muted']}; display: flex; align-items: center; gap: 6px;
  }}
  .hero-badge.accent {{ background: rgba(88,166,255,.12); border-color: {t['accent']}44; color: {t['accent']}; }}
  .hero-badge.success {{ background: rgba(46,160,67,.12); border-color: {t['success']}44; color: {t['success']}; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:currentColor; display:inline-block; }}

  .kpi-card {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 18px 20px 14px;
    transition: border-color .2s, box-shadow .2s;
  }}
  .kpi-card:hover {{ border-color: {t['accent']}; box-shadow: 0 0 0 3px {t['accent']}22; }}
  .kpi-icon  {{ font-size: 1.6rem; margin-bottom: 4px; }}
  .kpi-title {{ color: {t['text_muted']}; font-size: .78rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }}
  .kpi-value {{ color: {t['text_title']}; font-size: 1.9rem; font-weight: 700; line-height: 1.2; margin: 4px 0; }}
  .kpi-sub   {{ color: {t['text_muted']}; font-size: .78rem; }}
  .kpi-delta-pos {{ color: {t['success']}; font-size: .78rem; font-weight: 600; }}
  .kpi-delta-neg {{ color: #f85149; font-size: .78rem; font-weight: 600; }}
  .kpi-delta-neu {{ color: {t['text_muted']}; font-size: .78rem; }}

  h2, h3 {{ color: {t['text_title']} !important; }}
  hr {{ border-color: {t['grid']} !important; }}
  .stDataFrame {{ border-color: {t['border']} !important; }}
</style>
"""


def _fmt(n: float) -> str:
    """Formata número grande de forma compacta: 213.4M, 16.6M, 1.2K."""
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:.0f}"


def _delta_html(val: float, prev: float, unit: str = "", invert: bool = False) -> str:
    if prev == 0:
        return ""
    diff = val - prev
    pct  = diff / prev * 100
    arrow = "▲" if diff >= 0 else "▼"
    cls = "kpi-delta-pos" if (diff >= 0) != invert else "kpi-delta-neg"
    if diff == 0:
        cls = "kpi-delta-neu"
    return f'<span class="{cls}">{arrow} {abs(pct):.1f}%{unit} vs ano anterior</span>'


# ══════════════════════════════════════════════════════════════════════════════
#  DADOS — leitura local de Parquet (sem banco)
# ══════════════════════════════════════════════════════════════════════════════
_DIR = os.path.dirname(__file__)


@st.cache_data(show_spinner=False)
def _carregar_base() -> pd.DataFrame:
    pop  = pd.read_parquet(os.path.join(_DIR, "pop_ibge.parquet"))
    mun  = pd.read_parquet(os.path.join(_DIR, "ibge_municipios.parquet"))
    ufs  = pd.read_parquet(os.path.join(_DIR, "ibge_ufs.parquet"))

    pop["cod_mun"] = pop["cod_mun"].astype("int64")
    pop = (
        pop
        .merge(mun.rename(columns={"id": "cod_mun"}), on="cod_mun")
        .merge(ufs.rename(columns={"id": "ibge_uf_id"})[["ibge_uf_id", "sigla"]], on="ibge_uf_id")
    )
    pop["idade"]    = pop["idade"].astype(int)
    pop["sexo"]     = pop["sexo"].map({"1": "M", "2": "F"})
    return pop[["sigla", "ano", "idade", "sexo", "populacao"]].rename(columns={"sigla": "uf"})


@st.cache_data(show_spinner=False)
def anos_disponiveis() -> list[int]:
    df = _carregar_base()
    return sorted(df["ano"].unique().tolist(), reverse=True)


@st.cache_data(show_spinner="Carregando dados populacionais…")
def carregar_dados(ano: int) -> pd.DataFrame:
    df = _carregar_base()
    return (
        df[df["ano"] == ano]
        .groupby(["uf", "idade", "sexo"], as_index=False)["populacao"]
        .sum()
    )


@st.cache_data(show_spinner=False)
def carregar_evolucao() -> pd.DataFrame:
    df = _carregar_base()
    return df.groupby(["uf", "ano"], as_index=False)["populacao"].sum()


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESSAMENTO
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def processar_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    bins   = list(range(0, 101, 5)) + [200]
    labels = [f"{i}-{i+4}" for i in range(0, 100, 5)] + ["100+"]

    df_proc = df.copy()
    df_proc["faixa_etaria"] = pd.cut(df_proc["idade"], bins=bins, labels=labels, right=False)

    total_uf  = df_proc.groupby("uf")["populacao"].sum().rename("total")
    idosos_uf = (
        df_proc[df_proc["idade"] >= 60]
        .groupby("uf")["populacao"].sum()
        .rename("idosos")
    )
    df_idosos = pd.concat([total_uf, idosos_uf], axis=1).fillna(0).reset_index()
    df_idosos["pct_idosos"] = (df_idosos["idosos"] / df_idosos["total"] * 100).round(2)

    return df_proc, df_idosos


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS DE LAYOUT (theme-aware)
# ══════════════════════════════════════════════════════════════════════════════
def _apply_layout(fig: go.Figure, t: dict, height: int = H_MEDIUM) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=t["bg_plot"],
        plot_bgcolor=t["bg_plot"],
        font_color=t["text"],
        font_size=12,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor=t["bg_card"], bordercolor=t["border"], borderwidth=1),
    )
    fig.update_xaxes(gridcolor=t["grid"], linecolor=t["border"], zerolinecolor=t["border"])
    fig.update_yaxes(gridcolor=t["grid"], linecolor=t["border"], zerolinecolor=t["border"])
    return fig


def kpi_card(title: str, value: str, subtitle: str, icon: str, delta_html: str = "") -> str:
    return f"""
    <div class="kpi-card">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{subtitle}</div>
      {f'<div style="margin-top:6px">{delta_html}</div>' if delta_html else ''}
    </div>"""


# ══════════════════════════════════════════════════════════════════════════════
#  VISUALIZAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
def fig_mapa(df_idosos: pd.DataFrame, t: dict) -> go.Figure:
    is_light = t["bg"] == "#f6f8fa"
    map_style     = "carto-positron" if is_light else "carto-darkmatter"
    color_scale   = "Blues"          if is_light else "YlOrRd"

    fig = px.choropleth_mapbox(
        df_idosos,
        geojson=GEOJSON,
        locations="uf",
        featureidkey="properties.sigla",
        color="pct_idosos",
        color_continuous_scale=color_scale,
        range_color=(df_idosos["pct_idosos"].min(), df_idosos["pct_idosos"].max()),
        mapbox_style=map_style,
        zoom=2.8,
        center={"lat": -12.0, "lon": -52.0},
        opacity=0.75,
        labels={"pct_idosos": "% Idosos", "uf": "UF"},
        custom_data=["uf", "pct_idosos", "idosos", "total"],
    )
    fig.update_layout(
        height=H_LARGE,
        paper_bgcolor=t["bg_plot"],
        font_color=t["text"],
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(text="% Idosos", font=dict(color=t["text"])),
            tickfont=dict(color=t["text_muted"]),
            bgcolor=t["bg_card"],
            bordercolor=t["border"],
            x=1.0, thickness=14,
        ),
    )
    fig.update_traces(
        marker_line_color=t["map_line"],
        marker_line_width=0.6,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "% Idosos: %{customdata[1]:.2f}%<br>"
            "Idosos: %{customdata[2]:,.0f}<br>"
            "Total: %{customdata[3]:,.0f}<extra></extra>"
        ),
    )
    return fig


def fig_pizza(df: pd.DataFrame, t: dict, apenas_idosos: bool = False) -> go.Figure:
    df_pie = df[df["idade"] >= 60].copy() if apenas_idosos else df.copy()
    agg = df_pie.groupby("sexo")["populacao"].sum().reset_index()
    agg["label"] = agg["sexo"].map({"M": "Masculino", "F": "Feminino"})

    fig = px.pie(
        agg, names="label", values="populacao", color="label",
        color_discrete_map={"Masculino": COLOR_M, "Feminino": COLOR_F},
        hole=0.42,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:,}<br>%{percent}<extra></extra>",
        marker_line_color=t["bg"],
        marker_line_width=2,
        pull=[0.03, 0.03],
    )
    _apply_layout(fig, t, H_MEDIUM)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
    )
    return fig


def fig_piramide(df: pd.DataFrame, t: dict) -> go.Figure:
    FAIXAS = [
        "0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39",
        "40-44","45-49","50-54","55-59","60-64","65-69","70-74","75-79",
        "80-84","85-89","90-94","95-99","100+",
    ]
    agg = df.groupby(["faixa_etaria", "sexo"])["populacao"].sum().reset_index()
    agg["faixa_etaria"] = agg["faixa_etaria"].astype(str)
    agg = agg[agg["faixa_etaria"].isin(FAIXAS)]

    masc = agg[agg["sexo"] == "M"].set_index("faixa_etaria")["populacao"].reindex(FAIXAS, fill_value=0)
    fem  = agg[agg["sexo"] == "F"].set_index("faixa_etaria")["populacao"].reindex(FAIXAS, fill_value=0)
    max_val   = max(masc.max(), fem.max())
    tick_step = max(1, int(max_val // 5))

    fig = go.Figure([
        go.Bar(
            y=FAIXAS, x=-masc.values, name="Masculino", orientation="h",
            marker_color=COLOR_M, marker_line_color=t["bar_line"], marker_line_width=0.6,
            hovertemplate="<b>%{y}</b><br>Masculino: %{customdata:,}<extra></extra>",
            customdata=masc.values,
        ),
        go.Bar(
            y=FAIXAS, x=fem.values, name="Feminino", orientation="h",
            marker_color=COLOR_F, marker_line_color=t["bar_line"], marker_line_width=0.6,
            hovertemplate="<b>%{y}</b><br>Feminino: %{x:,}<extra></extra>",
        ),
    ])
    _apply_layout(fig, t, H_LARGE)
    fig.update_layout(
        barmode="relative", bargap=0.08,
        xaxis=dict(
            title="← Masculino  |  Feminino →",
            tickmode="array",
            tickvals=list(range(-int(max_val * 1.1), int(max_val * 1.1) + 1, tick_step)),
            ticktext=[f"{abs(v):,}" for v in range(-int(max_val * 1.1), int(max_val * 1.1) + 1, tick_step)],
            range=[-max_val * 1.15, max_val * 1.15],
            zeroline=True, zerolinecolor=t["border"], zerolinewidth=2,
        ),
        yaxis=dict(title="", tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(l=10, r=20, t=30, b=60),
    )
    return fig


def fig_ranking(df_idosos: pd.DataFrame, t: dict) -> go.Figure:
    df_r = df_idosos.sort_values("pct_idosos", ascending=True)
    color_scale = "Blues_r" if t["bg"] == "#f6f8fa" else "YlOrRd"
    fig = px.bar(
        df_r, x="pct_idosos", y="uf", orientation="h",
        color="pct_idosos", color_continuous_scale=color_scale,
        text="pct_idosos", labels={"pct_idosos": "% Idosos", "uf": "Estado"},
    )
    _apply_layout(fig, t, max(300, len(df_r) * 22))
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=80, t=20, b=10),
        xaxis=dict(title="Proporção de idosos (%)"),
        yaxis=dict(title=""),
    )
    fig.update_traces(
        texttemplate="%{text:.2f}%", textposition="outside",
        cliponaxis=False,
        marker_line_color=t["bar_line"], marker_line_width=1,
        hovertemplate="<b>%{y}</b><br>% Idosos: %{x:.2f}%<extra></extra>",
    )
    return fig


def fig_evolucao(df_evo: pd.DataFrame, ufs: list[str], t: dict) -> go.Figure:
    df_f = df_evo[df_evo["uf"].isin(ufs)].copy()
    df_tot = df_f.groupby("ano")["populacao"].sum().reset_index()
    df_tot["populacao_M"] = df_tot["populacao"] / 1_000_000

    fig = px.line(
        df_tot, x="ano", y="populacao_M",
        labels={"ano": "Ano", "populacao_M": "População (milhões)"},
        markers=True,
        color_discrete_sequence=[t["accent"]],
    )
    fig.update_traces(
        line_width=2.5,
        marker=dict(size=7, color=t["accent"]),
        hovertemplate="<b>%{x}</b><br>%{y:.2f}M habitantes<extra></extra>",
    )
    _apply_layout(fig, t, H_MEDIUM)
    fig.update_layout(
        xaxis=dict(title="", tickmode="linear", dtick=1),
        yaxis=dict(title="Milhões de habitantes"),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Dashboard Demográfico | UF", page_icon="🗺️", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
#  CARREGAMENTO
# ══════════════════════════════════════════════════════════════════════════════
df_raw             = carregar_dados(ano_sel)
df_proc, df_idosos = processar_dados(df_raw)
df_evo             = carregar_evolucao()

df_ant = carregar_dados(ano_ant) if ano_ant else None
df_proc_ant, df_idosos_ant = processar_dados(df_ant) if df_ant is not None else (None, None)

pop_total = int(df_proc["populacao"].sum())
n_ufs     = df_proc["uf"].nunique()

with st.sidebar:
    ufs_disponiveis = sorted(df_proc["uf"].unique().tolist())
    ufs_sel = st.multiselect(
        "Estados (UF):",
        options=ufs_disponiveis,
        default=ufs_disponiveis,
    )
    if not ufs_sel:
        ufs_sel = ufs_disponiveis

    filtrar_idosos_pizza = st.checkbox("Sexo apenas para ≥ 60 anos", value=False)

    st.markdown("---")
    st.caption(f"📊 **{pop_total:,}** hab. · **{n_ufs}** estados\nFonte: IBGE · {ano_sel}")

# ══════════════════════════════════════════════════════════════════════════════
#  MÉTRICAS FILTRADAS
# ══════════════════════════════════════════════════════════════════════════════
df_filt    = df_proc[df_proc["uf"].isin(ufs_sel)]
df_id_filt = df_idosos[df_idosos["uf"].isin(ufs_sel)]

pop_filt      = int(df_filt["populacao"].sum())
pct_fem_filt  = (df_filt[df_filt["sexo"] == "F"]["populacao"].sum() / pop_filt * 100) if pop_filt else 0
pct_idog_filt = (df_filt[df_filt["idade"] >= 60]["populacao"].sum() / pop_filt * 100) if pop_filt else 0
idade_med_filt = ((df_filt["idade"] * df_filt["populacao"]).sum() / pop_filt) if pop_filt else 0

# Deltas vs ano anterior
if df_proc_ant is not None:
    df_filt_ant   = df_proc_ant[df_proc_ant["uf"].isin(ufs_sel)]
    pop_ant       = int(df_filt_ant["populacao"].sum())
    pct_idog_ant  = (df_filt_ant[df_filt_ant["idade"] >= 60]["populacao"].sum() / pop_ant * 100) if pop_ant else 0
    pct_fem_ant   = (df_filt_ant[df_filt_ant["sexo"] == "F"]["populacao"].sum() / pop_ant * 100) if pop_ant else 0
    idade_ant     = ((df_filt_ant["idade"] * df_filt_ant["populacao"]).sum() / pop_ant) if pop_ant else 0
else:
    pop_ant = pct_idog_ant = pct_fem_ant = idade_ant = 0

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
#  KPIs
# ══════════════════════════════════════════════════════════════════════════════
kpi_data = [
    ("👥", "População total",     _fmt(pop_filt),              f"{len(ufs_sel)} estado(s)",
     _delta_html(pop_filt, pop_ant)),
    ("👴", "Proporção de idosos", f"{pct_idog_filt:.1f}%",     "≥ 60 anos",
     _delta_html(pct_idog_filt, pct_idog_ant)),
    ("♀️", "Proporção feminina",  f"{pct_fem_filt:.1f}%",      "sobre o total",
     _delta_html(pct_fem_filt, pct_fem_ant)),
    ("📅", "Idade média",         f"{idade_med_filt:.1f} anos","média ponderada",
     _delta_html(idade_med_filt, idade_ant)),
]

cols = st.columns(4)
for col, (icon, title, value, sub, delta) in zip(cols, kpi_data):
    with col:
        st.markdown(kpi_card(title, value, sub, icon, delta), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  MAPA + PIZZA
# ══════════════════════════════════════════════════════════════════════════════
col_mapa, col_pizza = st.columns([3, 2], gap="large")

with col_mapa:
    st.subheader("🗺️ Proporção de Idosos por Estado")
    st.caption("Percentual da população com **60 anos ou mais** em cada estado.")
    try:
        st.plotly_chart(fig_mapa(df_id_filt, t), use_container_width=True, config=PLOTLY_CFG)
    except Exception:
        fig_bar = px.bar(
            df_id_filt.sort_values("pct_idosos"),
            x="pct_idosos", y="uf", orientation="h",
            color="pct_idosos", color_continuous_scale="YlOrRd",
            labels={"pct_idosos": "% Idosos", "uf": "Estado"},
        )
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

# ══════════════════════════════════════════════════════════════════════════════
#  PIRÂMIDE ETÁRIA
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📊 Pirâmide Etária — Distribuição por Faixa (5 em 5 anos) e Sexo")
st.caption(
    "Eixo esquerdo → masculino (azul). Eixo direito → feminino (rosa). "
    "Base larga = população jovem; topo largo = população envelhecida."
)
st.plotly_chart(fig_piramide(df_filt, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  EVOLUÇÃO HISTÓRICA
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📈 Evolução Populacional — 2010 a 2025")
st.caption(
    "Total de habitantes nos estados selecionados ao longo dos anos. "
    "Use o filtro de UFs na sidebar para comparar regiões."
)
st.plotly_chart(fig_evolucao(df_evo, ufs_sel, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  RANKING
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🏆 Ranking de Estados — Proporção de Idosos")
st.caption("Estados ordenados pela proporção de pessoas com 60+ anos sobre o total.")
st.plotly_chart(fig_ranking(df_id_filt, t), use_container_width=True, config=PLOTLY_CFG)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div style='text-align:center;padding:18px 0 8px;color:{t['footer']};font-size:.78rem'>"
    f"Dashboard Demográfico · Fonte: IBGE {ano_sel} · cenarios_ai"
    f"</div>",
    unsafe_allow_html=True,
)
