"""Modelos para estratégias de amortização e metas financeiras."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from modelos.amortizacao import ModoAmortizacao

FrequenciaAmortizacao = Literal["unica", "mensal", "anual"]


@dataclass(frozen=True, slots=True)
class EstrategiaAmortizacao:
    """Parâmetros reutilizáveis de uma estratégia de amortização."""

    nome: str
    valor: Decimal
    data_inicio: date
    modo: ModoAmortizacao
    frequencia: FrequenciaAmortizacao = "unica"
    data_fim: date | None = None

    def __post_init__(self) -> None:
        if not self.nome.strip() or self.valor < 0:
            raise ValueError("Estratégia deve possuir nome e valor não negativo.")
        if self.frequencia != "unica" and self.data_fim is None:
            raise ValueError("Estratégias recorrentes exigem data final.")


@dataclass(frozen=True, slots=True)
class MetaQuitacao:
    """Meta de data máxima para quitar o contrato."""

    data_alvo: date


@dataclass(frozen=True, slots=True)
class MetaPrestacao:
    """Meta de valor máximo para a primeira prestação posterior ao aporte."""

    valor_maximo: Decimal

    def __post_init__(self) -> None:
        if self.valor_maximo < 0:
            raise ValueError("A prestação-alvo não pode ser negativa.")
