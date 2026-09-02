"""Pré-processa a malha das UFs uma vez, em disco.

O painel enviava ao navegador o `brazil-states.geojson` cru: 3,4 MB em disco,
85.585 vértices para 27 estados, coordenadas com 6 casas decimais e seis
propriedades por feição das quais o mapa usa uma. Num mapa do Brasil de
~600 px de largura isso é detalhe que nunca chega à tela e que o payload paga
por inteiro, a cada rerun.

Três ganhos independentes, todos aplicados aqui:

- **simplificação** — menos vértices, com a tolerância relativa à largura do
  bounding box, como no sinan
- **precisão** — 6 casas decimais (11 cm) caem para 5 (1,1 m)
- **propriedades** — sobra `sigla`, que é a chave do join

Uso (as dependências são só de build, não entram no runtime)::

    docker run --rm -v "$PWD:/app" -w /app demografico:geo \\
        python -m scripts.preparar_geometria

Saída: `data/ufs.geojson`, que é o que `src.data.carregar_geojson` lê.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import topojson as tp

_DATA = Path(__file__).resolve().parent.parent / "data"
ORIGEM = _DATA / "brazil-states.geojson"
SAIDA = _DATA / "ufs.geojson"

#: Divisor da largura do bbox. 1200 é o valor que o sinan usa nas camadas de
#: região (contra 900 para municípios), herdado do dashboard em R.
#:
#: A tolerância é **relativa** de propósito: assim ela se ajusta sozinha à
#: extensão da camada, sem número mágico. No Brasil, cujo bbox tem ~39,2° de
#: largura, dá 0,033° — cerca de meio pixel num mapa de 600 px.
DIVISOR = 1200

#: Casas decimais mantidas. A malha traz seis, que são 11 cm. Cinco são 1,1 m,
#: e um pixel deste mapa vale dezenas de quilômetros — as duas últimas casas
#: são exatidão que não chega à tela.
CASAS = 5

#: CRS métrico para conferir o erro de área (Brasil Polyconic).
CRS_AREA = 5880


def _arredondar(o):
    """Arredonda recursivamente as coordenadas de uma geometria GeoJSON."""
    if isinstance(o, float):
        return round(o, CASAS)
    if isinstance(o, (list, tuple)):
        return [_arredondar(x) for x in o]
    if isinstance(o, dict):
        return {k: _arredondar(v) for k, v in o.items()}
    return o


def simplificar(geo: gpd.GeoDataFrame, divisor: int = DIVISOR):
    """Simplifica preservando as fronteiras compartilhadas.

    O `simplify` do shapely trata cada polígono isoladamente, então dois
    estados vizinhos simplificam a divisa comum de formas diferentes e o
    mosaico se rompe — o coroplético ganha fiapos brancos entre as UFs e
    bordas dobradas. É o defeito que o sinan mediu e documentou.

    Aqui a simplificação é topológica: as arestas compartilhadas viram arcos e
    são simplificadas uma única vez, então a divisa entre BA e MG é
    literalmente a mesma linha nos dois polígonos.

    Returns:
        tuple[gpd.GeoDataFrame, float]: malha simplificada e o erro de área em
            percentual.
    """
    xmin, _, xmax, _ = geo.total_bounds
    tolerancia = (xmax - xmin) / divisor

    area_antes = geo.to_crs(CRS_AREA).area.sum()

    # `shared_coords=True`, ao contrário do sinan. Medido nas duas formas
    # sobre esta malha: com `False` a simplificação **introduz** 99,74 km²
    # de sobreposição entre estados numa malha que vinha com zero, pelo
    # mesmo número de vértices (4.455 contra 4.469) e o mesmo erro de
    # área. Com `True` a pior sobreposição fica em zero. O sinan trabalha
    # sobre malha municipal, onde a escolha se paga de outro jeito.
    topologia = tp.Topology(geo, prequantize=False, shared_coords=True)
    saida = topologia.toposimplify(tolerancia).to_gdf()
    saida = saida.set_crs(geo.crs, allow_override=True)
    saida = saida[list(geo.columns)]

    # A simplificação topológica não garante validade; conserta o que quebrou.
    invalidas = ~saida.geometry.is_valid
    if invalidas.any():
        saida.loc[invalidas, "geometry"] = saida.loc[invalidas, "geometry"].buffer(0)

    area_depois = saida.to_crs(CRS_AREA).area.sum()
    erro = abs(area_depois - area_antes) / area_antes * 100 if area_antes else 0.0
    return saida, erro


def _vertices(geometria: dict) -> int:
    """Conta os pares de coordenadas de uma geometria GeoJSON."""
    def andar(c):
        if isinstance(c[0], (int, float)):
            return 1
        return sum(andar(x) for x in c)
    return andar(geometria["coordinates"])


def _sobreposicao_km2(geo: gpd.GeoDataFrame) -> float:
    """Pior sobreposição entre dois estados, em km².

    Serve de guarda: simplificar por polígono faria este número explodir, e é
    exatamente o sintoma que a simplificação topológica evita.
    """
    metrico = geo.to_crs(CRS_AREA)
    pior = 0.0
    for i in range(len(metrico)):
        for j in range(i + 1, len(metrico)):
            a, b = metrico.geometry.iloc[i], metrico.geometry.iloc[j]
            if a.intersects(b):
                pior = max(pior, a.intersection(b).area / 1e6)
    return pior


def main() -> None:
    bruto = gpd.read_file(ORIGEM)
    bruto = bruto[["sigla", "geometry"]]

    antes_bytes = ORIGEM.stat().st_size
    antes_vertices = sum(
        _vertices(f["geometry"]) for f in json.loads(bruto.to_json())["features"]
    )

    simples, erro = simplificar(bruto)

    colecao = json.loads(simples.to_json())
    colecao = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"sigla": f["properties"]["sigla"]},
                "geometry": _arredondar(f["geometry"]),
            }
            for f in colecao["features"]
        ],
    }

    SAIDA.write_text(
        json.dumps(colecao, separators=(",", ":")),
        encoding="utf-8",
    )

    depois_vertices = sum(_vertices(f["geometry"]) for f in colecao["features"])
    depois_bytes = SAIDA.stat().st_size

    print(f"{'':<22}{'antes':>14}{'depois':>14}")
    print(f"{'arquivo':<22}{antes_bytes/1e6:>13.2f}M{depois_bytes/1e6:>13.2f}M")
    print(f"{'vértices':<22}{antes_vertices:>14,}{depois_vertices:>14,}")
    print(f"{'feições':<22}{len(bruto):>14}{len(colecao['features']):>14}")
    print()
    print(f"erro de área:          {erro:.3f}%")
    print(f"pior sobreposição:     {_sobreposicao_km2(simples):.2f} km²")
    print(f"\nescrito em {SAIDA}")


if __name__ == "__main__":
    main()
