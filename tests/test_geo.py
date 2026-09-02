"""Invariantes da malha pré-processada.

`data/ufs.geojson` é artefato de build, gerado por
`scripts/preparar_geometria.py` e versionado. Estes testes prendem o que o
runtime supõe dele, para que uma regeração com parâmetro errado não passe
despercebida.

Tudo aqui é JSON puro, de propósito: geopandas e topojson são dependências de
build e não estão na imagem que roda o painel.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data import carregar_geojson

_DATA = Path(__file__).resolve().parent.parent / "data"

#: As 26 UFs mais o Distrito Federal.
TOTAL_UFS = 27

#: Teto de vértices. Hoje são 4.469, vindos de 85.585 na malha bruta. O teto
#: tem folga para um reajuste de tolerância, mas não para voltar à malha crua.
TETO_VERTICES = 6_000

#: Teto do arquivo em disco, em KB. Hoje são 105.
TETO_KB = 200

#: Casas decimais que `preparar_geometria.CASAS` mantém.
CASAS = 5


def _vertices(geometria: dict) -> int:
    def andar(c):
        if isinstance(c[0], (int, float)):
            return 1
        return sum(andar(x) for x in c)
    return andar(geometria["coordinates"])


def _coordenadas(geometria: dict):
    def andar(c):
        if isinstance(c[0], (int, float)):
            yield from c
            return
        for x in c:
            yield from andar(x)
    return andar(geometria["coordinates"])


@pytest.fixture(scope="module")
def malha() -> dict:
    return carregar_geojson.__wrapped__()


def test_traz_as_27_ufs(malha):
    siglas = {f["properties"]["sigla"] for f in malha["features"]}
    assert len(siglas) == TOTAL_UFS
    assert "DF" in siglas and "PE" in siglas


def test_so_a_propriedade_sigla(malha):
    """O mapa casa por `sigla`. `cartodb_id`, `created_at` e companhia
    viajavam por feição sem serem lidas por ninguém."""
    for f in malha["features"]:
        assert set(f["properties"]) == {"sigla"}


def test_vertices_sob_o_teto(malha):
    total = sum(_vertices(f["geometry"]) for f in malha["features"])
    assert total <= TETO_VERTICES, f"{total:,} vértices"


def test_arquivo_sob_o_teto():
    kb = (_DATA / "ufs.geojson").stat().st_size / 1024
    assert kb <= TETO_KB, f"{kb:.0f} KB"


def test_coordenadas_arredondadas(malha):
    """Precisão além de `CASAS` é payload que não chega à tela."""
    for f in malha["features"]:
        for valor in _coordenadas(f["geometry"]):
            assert round(valor, CASAS) == valor, f["properties"]["sigla"]


def test_serializa_sem_indentacao():
    """Um terço do GeoJSON original era recuo. O artefato sai compacto."""
    texto = (_DATA / "ufs.geojson").read_text(encoding="utf-8")
    assert "\n" not in texto
    assert ", " not in texto


def test_origem_continua_versionada():
    """O `brazil-states.geojson` cru não é lido em execução, mas é a entrada
    de `preparar_geometria`. Perder o original impediria regerar a malha."""
    assert (_DATA / "brazil-states.geojson").exists()


def test_geometrias_fechadas(malha):
    """Todo anel de polígono precisa fechar — o primeiro ponto igual ao
    último. O arredondamento das coordenadas mexe nos dois extremos e poderia
    romper isso."""
    for f in malha["features"]:
        coords = f["geometry"]["coordinates"]
        poligonos = coords if f["geometry"]["type"] == "MultiPolygon" else [coords]
        for poligono in poligonos:
            for anel in poligono:
                assert anel[0] == anel[-1], f["properties"]["sigla"]


def test_dentro_do_bounding_box_do_brasil(malha):
    """O limite leste é -32,3 e não -33 porque **Fernando de Noronha é de
    Pernambuco** — o arquipélago fica a ~350 km da costa e é o ponto mais a
    leste da malha. É o mesmo fato que obriga `mapa._limites` a descartar
    ilhas antes de enquadrar."""
    for f in malha["features"]:
        pontos = list(_coordenadas(f["geometry"]))
        lons, lats = pontos[0::2], pontos[1::2]
        assert -74.5 < min(lons) and max(lons) < -32.0, f["properties"]["sigla"]
        assert -34.5 < min(lats) and max(lats) < 6.0, f["properties"]["sigla"]


def test_pernambuco_traz_fernando_de_noronha(malha):
    """Guarda explícita: se uma regeração perder o arquipélago, o teste acima
    passaria por acaso e `mapa._limites` deixaria de ser exercitado."""
    pe = next(f for f in malha["features"] if f["properties"]["sigla"] == "PE")
    lons = list(_coordenadas(pe["geometry"]))[0::2]
    assert max(lons) > -33.0


def test_json_valido_e_do_tipo_esperado():
    dados = json.loads((_DATA / "ufs.geojson").read_text(encoding="utf-8"))
    assert dados["type"] == "FeatureCollection"
    assert len(dados["features"]) == TOTAL_UFS
