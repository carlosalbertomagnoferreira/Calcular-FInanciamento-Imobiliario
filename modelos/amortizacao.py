"""Modelos de domínio para amortizações extraordinárias."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

ModoAmortizacao = Literal["prazo", "prestacao"]


@dataclass(frozen=True, slots=True)
class AmortizacaoExtraordinaria:
    """Valor adicional pago após a prestação regular de uma data."""

    data: date
    valor: Decimal
    modo: ModoAmortizacao

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("A amortização extraordinária deve ser positiva.")
        if self.modo not in {"prazo", "prestacao"}:
            raise ValueError("O modo deve ser 'prazo' ou 'prestacao'.")
