"""Leitura e normalização do extrato CSV do Banco do Brasil."""

from __future__ import annotations

import logging
import re
from csv import Error as CSVError
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import cast

import pandas as pd

from simulador.excecoes import (
    ArquivoExtratoNaoEncontradoError,
    CampoObrigatorioVazioError,
    ColunasObrigatoriasAusentesError,
    DataInvalidaError,
    LeituraCSVError,
    RegistroDuplicadoError,
    ValorInvalidoError,
)

LOGGER = logging.getLogger(__name__)

COLUNAS_OBRIGATORIAS = (
    "Data",
    "Saldo Devedor",
    "Correção Monetária",
    "Saldo Atualizado",
    "Prestação",
    "Juros",
    "Acessórios",
    "Correção Prestação",
    "Encargos",
    "Valor Pago",
    "Capital",
)

COLUNAS_MONETARIAS = tuple(
    coluna for coluna in COLUNAS_OBRIGATORIAS if coluna != "Data"
)
_NUMERO_COM_MILHAR = re.compile(r"^\d{1,3}(?:\.\d{3})+$")


def ler_extrato_csv(caminho: str | Path) -> pd.DataFrame:
    """Lê um extrato CSV e retorna uma cópia normalizada de seus dados.

    A leitura nunca grava nem altera o arquivo de origem. Datas são convertidas
    para ``datetime64`` e valores monetários para :class:`decimal.Decimal`.

    Args:
        caminho: Caminho para o CSV do extrato.

    Returns:
        DataFrame com os dados validados e normalizados.

    Raises:
        ArquivoExtratoNaoEncontradoError: Se o arquivo não existir.
        LeituraCSVError: Se o conteúdo não puder ser interpretado como CSV.
        ColunasObrigatoriasAusentesError: Se faltar alguma coluna do contrato.
        CampoObrigatorioVazioError: Se houver campo obrigatório vazio.
        DataInvalidaError: Se houver uma data inválida.
        ValorInvalidoError: Se houver valor monetário inválido ou negativo.
        RegistroDuplicadoError: Se houver linhas completamente duplicadas.
    """
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ArquivoExtratoNaoEncontradoError(
            f"Arquivo de extrato não encontrado: {arquivo}"
        )

    try:
        extrato = pd.read_csv(
            arquivo,
            sep=None,
            engine="python",
            dtype=str,
            encoding="utf-8-sig",
            keep_default_na=False,
        )
    except (
        OSError,
        CSVError,
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ) as erro:
        raise LeituraCSVError(f"Não foi possível ler o CSV: {arquivo}") from erro

    extrato.columns = [
        str(coluna).strip().removeprefix("\ufeff") for coluna in extrato.columns
    ]
    _validar_colunas(extrato)
    _validar_campos_vazios(extrato)
    _validar_duplicidades(extrato)

    resultado = cast(
        pd.DataFrame,
        extrato.loc[:, list(COLUNAS_OBRIGATORIAS)].copy(deep=True),
    )
    resultado["Data"] = _normalizar_datas(resultado["Data"])
    for coluna in COLUNAS_MONETARIAS:
        resultado[coluna] = resultado[coluna].map(_normalizar_valor_monetario)

    LOGGER.info("Extrato CSV carregado: %s registros", len(resultado))
    return resultado


def _validar_colunas(extrato: pd.DataFrame) -> None:
    faltantes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in extrato.columns
    ]
    if faltantes:
        nomes = ", ".join(faltantes)
        raise ColunasObrigatoriasAusentesError(
            f"Colunas obrigatórias ausentes: {nomes}"
        )


def _validar_campos_vazios(extrato: pd.DataFrame) -> None:
    for coluna in COLUNAS_OBRIGATORIAS:
        vazios = extrato[coluna].astype(str).str.strip().eq("")
        if vazios.any():
            linhas = _linhas_humanas(vazios)
            raise CampoObrigatorioVazioError(
                f"A coluna '{coluna}' possui campos vazios nas linhas: {linhas}"
            )


def _validar_duplicidades(extrato: pd.DataFrame) -> None:
    duplicados = extrato.loc[:, COLUNAS_OBRIGATORIAS].duplicated(keep=False)
    if duplicados.any():
        linhas = _linhas_humanas(duplicados)
        raise RegistroDuplicadoError(f"Registros duplicados nas linhas: {linhas}")


def _normalizar_datas(valores: pd.Series) -> pd.Series:
    datas = pd.to_datetime(valores, format="%d/%m/%Y", errors="coerce")
    if datas.isna().any():
        linhas = _linhas_humanas(datas.isna())
        raise DataInvalidaError(f"Datas inválidas nas linhas: {linhas}")
    return datas


def _normalizar_valor_monetario(valor: object) -> Decimal:
    texto = str(valor).strip()
    texto_normalizado = _normalizar_separadores(texto)
    try:
        numero = Decimal(texto_normalizado)
    except InvalidOperation as erro:
        raise ValorInvalidoError(f"Valor monetário inválido: {texto!r}") from erro

    if numero < 0:
        raise ValorInvalidoError(
            f"Valores monetários não podem ser negativos: {texto!r}"
        )
    return numero


def _normalizar_separadores(texto: str) -> str:
    if "," in texto:
        return texto.replace(".", "").replace(",", ".")
    if _NUMERO_COM_MILHAR.fullmatch(texto):
        return texto.replace(".", "")
    return texto


def _linhas_humanas(mascara: pd.Series) -> str:
    return ", ".join(str(indice + 2) for indice in mascara[mascara].index)
