"""Resumo de comparação entre dois cenários de projeção."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


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
