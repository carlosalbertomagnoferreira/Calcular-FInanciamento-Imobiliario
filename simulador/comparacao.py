"""Comparação de métricas entre projeções financeiras."""

from decimal import Decimal

import pandas as pd

from modelos import CenarioProjecao, EstrategiaAmortizacao
from modelos.comparacao import ResultadoComparacaoEstrategia, ResumoComparacao
from simulador.amortizacao import criar_agenda_estrategia, projetar_com_amortizacoes
from simulador.projecao import projetar_contrato


def comparar_projecoes(
    projecao_original: pd.DataFrame, projecao_cenario: pd.DataFrame
) -> ResumoComparacao:
    """Compara juros, pagamentos, prazo, prestação e saldo dos cenários."""
    if projecao_original.empty or projecao_cenario.empty:
        raise ValueError("As duas projeções são obrigatórias para comparação.")
    original = projecao_original.iloc[0]
    cenario = projecao_cenario.iloc[0]
    quitacao_original = projecao_original.iloc[-1]["Data"]
    quitacao_cenario = projecao_cenario.iloc[-1]["Data"]
    total_original = _somar(
        projecao_original["Total Pago"]
        if "Total Pago" in projecao_original
        else projecao_original["Prestação"]
    )
    total_cenario = _somar(
        projecao_cenario["Total Pago"]
        if "Total Pago" in projecao_cenario
        else projecao_cenario["Prestação"]
    )
    return ResumoComparacao(
        juros_economizados=_somar(projecao_original["Juros"])
        - _somar(projecao_cenario["Juros"]),
        total_restante_original=total_original,
        total_restante_cenario=total_cenario,
        economia_total=total_original - total_cenario,
        meses_abatidos=len(projecao_original) - len(projecao_cenario),
        data_quitacao_original=quitacao_original,
        data_quitacao_cenario=quitacao_cenario,
        prestacao_original=original["Prestação"],
        prestacao_cenario=cenario["Prestação"],
        diferenca_prestacao=original["Prestação"] - cenario["Prestação"],
        saldo_original=original["Saldo Final"],
        saldo_cenario=cenario["Saldo Final"],
    )


def comparar_estrategias(
    cenario: CenarioProjecao,
    estrategias: list[EstrategiaAmortizacao],
) -> list[ResultadoComparacaoEstrategia]:
    """Compara cada estratégia nomeada com a projeção-base do contrato.

    O desembolso futuro inclui prestações, acessórios e os aportes efetivamente
    aplicados. A lista preserva a ordem recebida para permitir sua apresentação
    direta em tabela pela interface de linha de comando.
    """
    nomes = [estrategia.nome for estrategia in estrategias]
    if len(nomes) != len(set(nomes)):
        raise ValueError("Os nomes das estratégias devem ser únicos.")

    projecao_base = projetar_contrato(cenario)
    resultados: list[ResultadoComparacaoEstrategia] = []
    for estrategia in estrategias:
        agenda = criar_agenda_estrategia(cenario, estrategia)
        projecao_estrategia = projetar_com_amortizacoes(cenario, agenda)
        resumo = comparar_projecoes(projecao_base, projecao_estrategia)
        resultados.append(
            ResultadoComparacaoEstrategia(
                estrategia=estrategia,
                aporte_total=_somar(projecao_estrategia["Amortização Extraordinária"]),
                juros_economizados=resumo.juros_economizados,
                desembolso_futuro=resumo.total_restante_cenario,
                data_quitacao=resumo.data_quitacao_cenario,
                meses_abatidos=resumo.meses_abatidos,
                proxima_prestacao=resumo.prestacao_cenario,
                saldo_devedor=resumo.saldo_cenario,
            )
        )
    return resultados


def _somar(valores: pd.Series) -> Decimal:
    return sum(valores, start=Decimal(0))
