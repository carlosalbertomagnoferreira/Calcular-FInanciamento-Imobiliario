"""Exportação dos dados produzidos pelo simulador."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd


def exportar_projecao_csv(projecao: pd.DataFrame, destino: str | Path) -> Path:
    """Exporta a projeção em CSV compatível com o formato brasileiro."""
    caminho = Path(destino)
    dados = projecao.copy()
    for coluna in dados.columns:
        dados[coluna] = dados[coluna].map(_formatar_valor)
    dados.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")
    return caminho


def serializar_projecao_csv(projecao: pd.DataFrame) -> bytes:
    """Serializa a projeção para download sem gravar arquivo local."""
    dados = projecao.copy()
    for coluna in dados.columns:
        dados[coluna] = dados[coluna].map(_formatar_valor)
    return dados.to_csv(sep=";", index=False, encoding="utf-8-sig").encode()


def _formatar_valor(valor: object) -> object:
    if isinstance(valor, Decimal):
        return format(valor, "f").replace(".", ",")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return valor
