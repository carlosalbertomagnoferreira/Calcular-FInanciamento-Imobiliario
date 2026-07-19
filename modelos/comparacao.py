"""Resumo de comparação entre dois cenários de projeção."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from modelos.planejamento import EstrategiaAmortizacao


@dataclass(frozen=True, slots=True)
class ResumoComparacao:
    """Métricas financeiras entre a projeção-base e um cenário alternativo."""

    juros_economizados: Decimal
    total_restante_original: Decimal
    total_restante_cenario: Decimal
    economia_total: Decimal
    meses_abatidos: int
    data_quitacao_original: date
    data_quitacao_cenario: date
    prestacao_original: Decimal
    prestacao_cenario: Decimal
    diferenca_prestacao: Decimal
    saldo_original: Decimal
    saldo_cenario: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoComparacaoEstrategia:
    """Resultado nomeado de uma estratégia comparada ao cenário-base."""

    estrategia: EstrategiaAmortizacao
    aporte_total: Decimal
    juros_economizados: Decimal
    desembolso_futuro: Decimal
    data_quitacao: date
    meses_abatidos: int
    proxima_prestacao: Decimal
    saldo_devedor: Decimal
