"""Classificação e métricas de calibração do histórico financeiro."""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pandas as pd

from modelos import ClassificacaoEvento, CriteriosCalibracao, ResumoCalibracao
from simulador.reconstrucao import reconstruir_historico
from simulador.parcelas import identificar_parcelas_validas

COLUNA_CLASSIFICACAO = "Classificação de Calibração"
COLUNA_MOTIVO = "Motivo da Classificação"


def classificar_eventos_calibracao(
    reconstruido: pd.DataFrame,
    criterios: CriteriosCalibracao | None = None,
) -> pd.DataFrame:
    """Classifica eventos entre elegíveis e não elegíveis para calibração.

    Eventos com saldo zero, inadimplência, sem amortização, ajuste de saldo
    relevante ou componente de prestação não identificado permanecem no
    histórico, mas não entram nas métricas de uma parcela PRICE regular.
    """
    criterios_efetivos = criterios or CriteriosCalibracao()
    _validar_colunas_reconstrucao(reconstruido)

    resultado = reconstruido.copy(deep=True)
    classificacoes = resultado.apply(
        lambda linha: _classificar_evento(linha, criterios_efetivos),
        axis="columns",
    )
    resultado[COLUNA_CLASSIFICACAO] = [
        classificacao.value for classificacao, _ in classificacoes
    ]
    resultado[COLUNA_MOTIVO] = [motivo for _, motivo in classificacoes]
    return resultado


def gerar_resumo_calibracao(
    classificados: pd.DataFrame,
    criterios: CriteriosCalibracao | None = None,
) -> ResumoCalibracao:
    """Calcula as métricas de erro somente sobre eventos elegíveis."""
    criterios_efetivos = criterios or CriteriosCalibracao()
    if COLUNA_CLASSIFICACAO not in classificados:
        raise ValueError("Classifique os eventos antes de gerar o resumo.")

    elegiveis = classificados.loc[
        classificados[COLUNA_CLASSIFICACAO] == ClassificacaoEvento.ELEGIVEL.value
    ]
    if elegiveis.empty:
        raise ValueError("Não há eventos elegíveis para calibração.")

    erros_juros = _erros_percentuais(
        elegiveis["Diferença de Juros"],
        elegiveis["Juros"],
    )
    erros_prestacao = _erros_percentuais(
        elegiveis["Resíduo da Prestação"],
        elegiveis["Prestação"],
    )
    erros_saldo = _erros_percentuais(
        elegiveis["Ajuste de Saldo Não Classificado"],
        elegiveis["Saldo Atualizado"],
    )

    maximo_juros = max(erros_juros)
    maximo_prestacao = max(erros_prestacao)
    maximo_saldo = max(erros_saldo)
    return ResumoCalibracao(
        total_eventos=len(classificados),
        eventos_elegiveis=len(elegiveis),
        eventos_excluidos=len(classificados) - len(elegiveis),
        erro_medio_percentual_juros=_media(erros_juros),
        erro_maximo_percentual_juros=maximo_juros,
        erro_medio_percentual_prestacao=_media(erros_prestacao),
        erro_maximo_percentual_prestacao=maximo_prestacao,
        erro_medio_percentual_saldo=_media(erros_saldo),
        erro_maximo_percentual_saldo=maximo_saldo,
        atende_tolerancia_juros=maximo_juros
        <= criterios_efetivos.tolerancia_percentual_juros,
        atende_tolerancia_prestacao=maximo_prestacao
        <= criterios_efetivos.tolerancia_percentual_prestacao,
        atende_tolerancia_saldo=maximo_saldo
        <= criterios_efetivos.tolerancia_percentual_saldo,
    )


def calibrar_historico(
    extrato: pd.DataFrame,
    criterios: CriteriosCalibracao | None = None,
) -> tuple[pd.DataFrame, ResumoCalibracao]:
    """Reconstrói, classifica e resume o histórico sem alterar sua entrada."""
    criterios_efetivos = criterios or CriteriosCalibracao()
    reconstruido = reconstruir_historico(extrato)
    parcelas = identificar_parcelas_validas(reconstruido)
    classificados = classificar_eventos_calibracao(parcelas, criterios_efetivos)
    return classificados, gerar_resumo_calibracao(classificados, criterios_efetivos)


def _validar_colunas_reconstrucao(reconstruido: pd.DataFrame) -> None:
    obrigatorias = (
        "Saldo Devedor",
        "Capital",
        "Encargos",
        "Ajuste de Saldo Não Classificado",
        "Resíduo da Prestação",
        "Prestação",
    )
    faltantes = [coluna for coluna in obrigatorias if coluna not in reconstruido]
    if faltantes:
        raise ValueError(
            "Reconstrução não possui as colunas obrigatórias: " + ", ".join(faltantes)
        )


def _classificar_evento(
    linha: pd.Series,
    criterios: CriteriosCalibracao,
) -> tuple[ClassificacaoEvento, str]:
    saldo_devedor = cast(Decimal, linha["Saldo Devedor"])
    capital = cast(Decimal, linha["Capital"])
    encargos = cast(Decimal, linha["Encargos"])
    ajuste_saldo = cast(Decimal, linha["Ajuste de Saldo Não Classificado"])
    residuo_prestacao = cast(Decimal, linha["Resíduo da Prestação"])
    prestacao = cast(Decimal, linha["Prestação"])

    if saldo_devedor == 0:
        return ClassificacaoEvento.SALDO_ZERO, "Saldo devedor igual a zero."
    if encargos > 0:
        return ClassificacaoEvento.INADIMPLENCIA, "Encargos de inadimplência presentes."
    if capital == 0:
        return ClassificacaoEvento.SEM_AMORTIZACAO, "Capital reportado igual a zero."
    if abs(ajuste_saldo) > criterios.tolerancia_ajuste_saldo:
        return (
            ClassificacaoEvento.AJUSTE_RELEVANTE,
            "Ajuste de saldo excede a tolerância configurada.",
        )
    if (
        abs(residuo_prestacao) / prestacao * Decimal("100")
        > criterios.tolerancia_percentual_residuo_prestacao
    ):
        return (
            ClassificacaoEvento.COMPONENTE_NAO_IDENTIFICADO,
            "Resíduo da prestação excede a tolerância configurada.",
        )
    return ClassificacaoEvento.ELEGIVEL, "Evento compatível com parcela PRICE regular."


def _erros_percentuais(diferencas: pd.Series, referencias: pd.Series) -> list[Decimal]:
    erros: list[Decimal] = []
    for diferenca, referencia in zip(diferencas, referencias, strict=True):
        valor_referencia = cast(Decimal, referencia)
        if valor_referencia <= 0:
            raise ValueError("A referência para cálculo percentual deve ser positiva.")
        erros.append(abs(cast(Decimal, diferenca)) / valor_referencia * Decimal("100"))
    return erros


def _media(valores: list[Decimal]) -> Decimal:
    return sum(valores, start=Decimal(0)) / len(valores)
