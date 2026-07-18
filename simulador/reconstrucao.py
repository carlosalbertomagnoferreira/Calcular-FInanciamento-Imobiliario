"""Reconstrução auditável dos eventos históricos do contrato."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import cast

import pandas as pd

from modelos import EventoHistorico
from simulador.calculos import calcular_juros_estimados, calcular_taxa_mensal
from simulador.leitor import COLUNAS_OBRIGATORIAS

TAXA_EFETIVA_ANUAL_PADRAO = Decimal("0.05116")


def reconstruir_historico(
    extrato: pd.DataFrame,
    taxa_efetiva_anual: Decimal = TAXA_EFETIVA_ANUAL_PADRAO,
) -> pd.DataFrame:
    """Enriquece o extrato com cálculos e diagnósticos históricos.

    Os saldos e componentes reportados pelo extrato são preservados como fonte
    autoritativa. A função não força uma recorrência PRICE quando há ajustes
    não classificados no histórico.

    Args:
        extrato: DataFrame normalizado por :func:`ler_extrato_csv`.
        taxa_efetiva_anual: Taxa anual efetiva decimal do contrato.

    Returns:
        Novo DataFrame com os valores do extrato e colunas de diagnóstico.
    """
    _validar_extrato_normalizado(extrato)
    taxa_mensal = calcular_taxa_mensal(taxa_efetiva_anual)
    eventos = tuple(_criar_evento(linha) for _, linha in extrato.iterrows())

    registros = [_criar_registro(evento, taxa_mensal) for evento in eventos]
    return pd.DataFrame.from_records(registros)


def _validar_extrato_normalizado(extrato: pd.DataFrame) -> None:
    faltantes = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in extrato]
    if faltantes:
        nomes = ", ".join(faltantes)
        raise ValueError(f"Extrato não possui as colunas obrigatórias: {nomes}")


def _criar_evento(linha: pd.Series) -> EventoHistorico:
    data = cast(pd.Timestamp | datetime, linha["Data"])
    return EventoHistorico(
        data=data.date(),
        saldo_devedor=cast(Decimal, linha["Saldo Devedor"]),
        correcao_monetaria=cast(Decimal, linha["Correção Monetária"]),
        saldo_atualizado=cast(Decimal, linha["Saldo Atualizado"]),
        prestacao=cast(Decimal, linha["Prestação"]),
        capital=cast(Decimal, linha["Capital"]),
        juros=cast(Decimal, linha["Juros"]),
        acessorios=cast(Decimal, linha["Acessórios"]),
        correcao_prestacao=cast(Decimal, linha["Correção Prestação"]),
        encargos=cast(Decimal, linha["Encargos"]),
        valor_pago=cast(Decimal, linha["Valor Pago"]),
    )


def _criar_registro(evento: EventoHistorico, taxa_mensal: Decimal) -> dict[str, object]:
    juros_estimados = calcular_juros_estimados(evento.saldo_devedor, taxa_mensal)
    return {
        "Data": evento.data,
        "Saldo Devedor": evento.saldo_devedor,
        "Correção Monetária": evento.correcao_monetaria,
        "Saldo Atualizado": evento.saldo_atualizado,
        "Prestação": evento.prestacao,
        "Capital": evento.capital,
        "Juros": evento.juros,
        "Acessórios": evento.acessorios,
        "Correção Prestação": evento.correcao_prestacao,
        "Encargos": evento.encargos,
        "Valor Pago": evento.valor_pago,
        "Taxa Mensal Calculada": taxa_mensal,
        "TR Histórica": evento.tr_historica,
        "Amortização Reportada": evento.amortizacao_reportada,
        "Componentes Conhecidos da Prestação": evento.componentes_conhecidos_prestacao,
        "Resíduo da Prestação": evento.residuo_prestacao,
        "Saldo Teórico sem Ajustes": evento.saldo_teorico_sem_ajustes,
        "Ajuste de Saldo Não Classificado": evento.ajuste_saldo_nao_classificado,
        "Juros Estimados": juros_estimados,
        "Diferença de Juros": evento.juros - juros_estimados,
    }
