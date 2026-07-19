"""Orquestração reutilizável da análise básica de um extrato validado."""

from dataclasses import dataclass

import pandas as pd

from modelos import ResumoFinanceiro
from simulador.parcelas import identificar_parcelas_validas
from simulador.projecao import criar_cenario_padrao, projetar_contrato
from simulador.reconstrucao import reconstruir_historico
from simulador.relatorio import gerar_resumo_financeiro


@dataclass(frozen=True, slots=True)
class AnaliseContrato:
    """Dados preparados para apresentação em interfaces como CLI e dashboard."""

    historico: pd.DataFrame
    projecao: pd.DataFrame
    resumo: ResumoFinanceiro


def preparar_analise(extrato: pd.DataFrame) -> AnaliseContrato:
    """Reconstrói o histórico, projeta o contrato e gera o resumo financeiro."""
    historico = identificar_parcelas_validas(reconstruir_historico(extrato))
    projecao = projetar_contrato(criar_cenario_padrao(historico))
    return AnaliseContrato(
        historico=historico,
        projecao=projecao,
        resumo=gerar_resumo_financeiro(historico, projecao),
    )
