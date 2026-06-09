import json
import os

import pandas as pd
import streamlit as st

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@st.cache_data(show_spinner=False)
def carregar_geojson() -> dict:
    path = os.path.join(_DATA_DIR, "brazil-states.geojson")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _carregar_base() -> pd.DataFrame:
    pop = pd.read_parquet(os.path.join(_DATA_DIR, "pop_ibge.parquet"))
    mun = pd.read_parquet(os.path.join(_DATA_DIR, "ibge_municipios.parquet"))
    ufs = pd.read_parquet(os.path.join(_DATA_DIR, "ibge_ufs.parquet"))

    pop["cod_mun"] = pop["cod_mun"].astype("int64")
    pop = (
        pop
        .merge(mun.rename(columns={"id": "cod_mun"}), on="cod_mun")
        .merge(ufs.rename(columns={"id": "ibge_uf_id"})[["ibge_uf_id", "sigla"]], on="ibge_uf_id")
    )
    pop["idade"] = pop["idade"].astype(int)
    pop["sexo"]  = pop["sexo"].map({"1": "M", "2": "F"})
    return pop[["sigla", "ano", "idade", "sexo", "populacao"]].rename(columns={"sigla": "uf"})


@st.cache_data(show_spinner=False)
def anos_disponiveis() -> list:
    return sorted(_carregar_base()["ano"].unique().tolist(), reverse=True)


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
    return _carregar_base().groupby(["uf", "ano"], as_index=False)["populacao"].sum()
