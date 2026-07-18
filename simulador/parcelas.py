"""Identificação de parcelas mensais válidas no histórico do contrato."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import cast

import pandas as pd

from modelos import CriteriosParcelasValidas

COLUNA_PARCELA_VALIDA = "Parcela Válida"
COLUNA_NUMERO_PARCELA = "Número da Parcela"
COLUNA_MOTIVO_PARCELA = "Motivo da Parcela"


def identificar_parcelas_validas(
    reconstruido: pd.DataFrame,
    criterios: CriteriosParcelasValidas | None = None,
) -> pd.DataFrame:
    """Marca a sequência final ancorada como parcelas mensais válidas.

    A âncora é configurável e não altera a classificação conservadora usada na
    calibração. Ela permite identificar parcelas reais mesmo quando o extrato
    possui componentes de prestação ainda não reconciliados.
    """
    criterios_efetivos = criterios or CriteriosParcelasValidas()
    _validar_colunas(reconstruido)
    resultado = reconstruido.copy(deep=True)
    resultado[COLUNA_PARCELA_VALIDA] = False
    resultado[COLUNA_NUMERO_PARCELA] = pd.NA
    resultado[COLUNA_MOTIVO_PARCELA] = "Fora da sequência final ancorada."

    candidatos = resultado[
        resultado["Data"].map(
            lambda data: cast(date, data).day == criterios_efetivos.dia_vencimento
        )
    ]
    if len(candidatos) < criterios_efetivos.quantidade_final:
        raise ValueError("O extrato não possui eventos suficientes para a âncora.")

    indices = list(candidatos.tail(criterios_efetivos.quantidade_final).index)
    sequencia = resultado.loc[indices]
    _validar_sequencia_final(sequencia, criterios_efetivos)

    primeiro_numero = (
        criterios_efetivos.numero_ultima_parcela
        - criterios_efetivos.quantidade_final
        + 1
    )
    for numero, indice in enumerate(indices, start=primeiro_numero):
        resultado.loc[indice, COLUNA_PARCELA_VALIDA] = True
        resultado.loc[indice, COLUNA_NUMERO_PARCELA] = numero
        resultado.loc[indice, COLUNA_MOTIVO_PARCELA] = (
            "Sequência mensal validada pela âncora contratual."
        )

    return resultado


def _validar_colunas(reconstruido: pd.DataFrame) -> None:
    obrigatorias = (
        "Data",
        "Saldo Devedor",
        "Capital",
        "Encargos",
        "Prestação",
        "Valor Pago",
    )
    faltantes = [coluna for coluna in obrigatorias if coluna not in reconstruido]
    if faltantes:
        raise ValueError(
            "Reconstrução não possui as colunas obrigatórias: " + ", ".join(faltantes)
        )


def _validar_sequencia_final(
    sequencia: pd.DataFrame,
    criterios: CriteriosParcelasValidas,
) -> None:
    periodos_anteriores: int | None = None
    for indice, linha in sequencia.iterrows():
        data = cast(date, linha["Data"])
        saldo = cast(Decimal, linha["Saldo Devedor"])
        encargos = cast(Decimal, linha["Encargos"])
        prestacao = cast(Decimal, linha["Prestação"])
        valor_pago = cast(Decimal, linha["Valor Pago"])
        periodo_atual = data.year * 12 + data.month

        if periodos_anteriores is not None and periodo_atual != periodos_anteriores + 1:
            raise ValueError("A sequência final ancorada possui lacuna mensal.")
        if saldo <= 0 or encargos != 0 or prestacao != valor_pago:
            raise ValueError(
                "A sequência final ancorada não possui perfil de parcela regular."
            )
        periodos_anteriores = periodo_atual
