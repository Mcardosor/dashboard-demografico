import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .utils import COLOR_M, COLOR_F, H_MEDIUM, H_LARGE, _apply_layout


def processar_dados(df: pd.DataFrame):
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


def fig_mapa(df_idosos: pd.DataFrame, t: dict, geojson: dict) -> go.Figure:
    is_light    = t.get("toggle_icon") == "🌙"
    map_style   = "open-street-map" if is_light else "carto-darkmatter"
    color_scale = "Blues" if is_light else "YlOrRd"

    fig = px.choropleth_mapbox(
        df_idosos,
        geojson=geojson,
        locations="uf",
        featureidkey="properties.sigla",
        color="pct_idosos",
        color_continuous_scale=color_scale,
        range_color=(0, df_idosos["pct_idosos"].max()),
        mapbox_style=map_style,
        zoom=3.4,
        center={"lat": -16.0, "lon": -50.0},
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
    from .utils import _fmt
    df_pie = df[df["idade"] >= 60].copy() if apenas_idosos else df.copy()
    agg = df_pie.groupby("sexo")["populacao"].sum().reset_index()
    agg["label"] = agg["sexo"].map({"M": "Masculino", "F": "Feminino"})
    total = agg["populacao"].sum()

    fig = px.pie(
        agg, names="label", values="populacao", color="label",
        color_discrete_map={"Masculino": COLOR_M, "Feminino": COLOR_F},
        hole=0.55,
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{percent:.1%}",
        textfont=dict(size=14, color="#ffffff"),
        insidetextorientation="horizontal",
        hovertemplate="<b>%{label}</b><br>%{value:,} pessoas<br>%{percent:.1%}<extra></extra>",
        marker_line_color=t["bg"],
        marker_line_width=3,
        pull=[0.03, 0.03],
    )
    _apply_layout(fig, t, H_MEDIUM)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.08,
            xanchor="center", x=0.5,
            font=dict(size=13, color=t["text"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(
            text=f"<b>{_fmt(total)}</b><br><span style='font-size:11px'>{('idosos' if apenas_idosos else 'pessoas')}</span>",
            x=0.5, y=0.5, font=dict(size=18, color=t["text_title"]),
            showarrow=False, align="center",
        )],
    )
    return fig


def fig_piramide(df: pd.DataFrame, t: dict) -> go.Figure:
    FAIXAS = [
        "0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39",
        "40-44","45-49","50-54","55-59","60-64","65-69","70-74","75-79",
        "80-84","85-89","90-94","95-99","100+",
    ]
    agg = df.groupby(["faixa_etaria", "sexo"], observed=False)["populacao"].sum().reset_index()
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
            title=dict(text="← Masculino  |  Feminino →", font=dict(color=t["text"])),
            tickmode="array",
            tickvals=list(range(-int(max_val * 1.1), int(max_val * 1.1) + 1, tick_step)),
            ticktext=[f"{abs(v):,}" for v in range(-int(max_val * 1.1), int(max_val * 1.1) + 1, tick_step)],
            range=[-max_val * 1.15, max_val * 1.15],
            zeroline=True, zerolinecolor=t["border"], zerolinewidth=2,
            tickfont=dict(color=t["text_muted"]),
        ),
        yaxis=dict(title="", tickfont=dict(size=10, color=t["text"])),
        showlegend=False,
        margin=dict(l=10, r=20, t=30, b=40),
    )
    return fig


def fig_ranking(df_idosos: pd.DataFrame, t: dict) -> go.Figure:
    df_r = df_idosos.sort_values("pct_idosos", ascending=True)
    color_scale = "Blues" if t.get("toggle_icon") == "🌙" else "YlOrRd"
    fig = px.bar(
        df_r, x="pct_idosos", y="uf", orientation="h",
        color="pct_idosos", color_continuous_scale=color_scale,
        text="pct_idosos", labels={"pct_idosos": "% Idosos", "uf": "Estado"},
    )
    _apply_layout(fig, t, max(300, len(df_r) * 22))
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=80, t=20, b=10),
        xaxis=dict(title=dict(text="Proporção de idosos (%)", font=dict(color=t["text"])), tickfont=dict(color=t["text_muted"])),
        yaxis=dict(title="", tickfont=dict(color=t["text"])),
    )
    fig.update_traces(
        texttemplate="%{text:.2f}%", textposition="outside",
        cliponaxis=False,
        marker_line_color=t["bar_line"], marker_line_width=1,
        hovertemplate="<b>%{y}</b><br>% Idosos: %{x:.2f}%<extra></extra>",
    )
    return fig


def fig_evolucao(df_evo: pd.DataFrame, ufs: list, t: dict) -> go.Figure:
    df_f  = df_evo[df_evo["uf"].isin(ufs)].copy()
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
    from .utils import H_MEDIUM
    _apply_layout(fig, t, H_MEDIUM)
    fig.update_layout(
        xaxis=dict(title="", tickmode="linear", dtick=1, tickfont=dict(color=t["text_muted"])),
        yaxis=dict(title=dict(text="Milhões de habitantes", font=dict(color=t["text"])), tickfont=dict(color=t["text_muted"])),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    return fig
