"""Modelos de domínio do simulador."""

from modelos.calibracao import (
    ClassificacaoEvento,
    CriteriosCalibracao,
    CriteriosParcelasValidas,
    ResumoCalibracao,
)
from modelos.comparacao import ResumoComparacao
from modelos.evento_historico import EventoHistorico
from modelos.projecao import CenarioProjecao
from modelos.planejamento import (
    EstrategiaAmortizacao,
    FrequenciaAmortizacao,
    MetaPrestacao,
    MetaQuitacao,
)
from modelos.relatorio import ResumoFinanceiro

__all__ = [
    "ClassificacaoEvento",
    "AmortizacaoExtraordinaria",
    "CriteriosCalibracao",
    "CriteriosParcelasValidas",
    "CenarioProjecao",
    "EventoHistorico",
    "EstrategiaAmortizacao",
    "FrequenciaAmortizacao",
    "MetaPrestacao",
    "MetaQuitacao",
    "ModoAmortizacao",
    "ResumoCalibracao",
    "ResumoComparacao",
    "ResumoFinanceiro",
]
from modelos.amortizacao import AmortizacaoExtraordinaria, ModoAmortizacao
