"""Modelos usados na classificação e no resumo da calibração."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ClassificacaoEvento(StrEnum):
    """Classificações possíveis para um evento histórico."""

    ELEGIVEL = "elegivel"
    SALDO_ZERO = "saldo_zero"
    INADIMPLENCIA = "inadimplencia"
    SEM_AMORTIZACAO = "sem_amortizacao"
    AJUSTE_RELEVANTE = "ajuste_relevante"
    COMPONENTE_NAO_IDENTIFICADO = "componente_nao_identificado"


@dataclass(frozen=True, slots=True)
class CriteriosCalibracao:
    """Critérios explícitos para selecionar eventos PRICE regulares."""

    tolerancia_ajuste_saldo: Decimal = Decimal("25.00")
    tolerancia_percentual_residuo_prestacao: Decimal = Decimal("1")
    tolerancia_percentual_juros: Decimal = Decimal("1")
    tolerancia_percentual_prestacao: Decimal = Decimal("1")
    tolerancia_percentual_saldo: Decimal = Decimal("0.5")

    def __post_init__(self) -> None:
        valores = (
            self.tolerancia_ajuste_saldo,
            self.tolerancia_percentual_residuo_prestacao,
            self.tolerancia_percentual_juros,
            self.tolerancia_percentual_prestacao,
            self.tolerancia_percentual_saldo,
        )
        if any(valor < 0 for valor in valores):
            raise ValueError("As tolerâncias de calibração não podem ser negativas.")


@dataclass(frozen=True, slots=True)
class CriteriosParcelasValidas:
    """Âncora contratual para identificar parcelas mensais válidas.

    Para o contrato de referência, os vencimentos ocorrem no dia 10 de cada
    mês; a parcela 360 vence em 10/02/2046 e a parcela 125 em 10/07/2026.
    """

    quantidade_final: int = 125
    numero_ultima_parcela: int = 125
    dia_vencimento: int = 10

    def __post_init__(self) -> None:
        if self.quantidade_final < 1:
            raise ValueError("A quantidade final de parcelas deve ser positiva.")
        if self.numero_ultima_parcela < self.quantidade_final:
            raise ValueError(
                "O número da última parcela é incompatível com a quantidade."
            )
        if not 1 <= self.dia_vencimento <= 31:
            raise ValueError("O dia de vencimento deve estar entre 1 e 31.")


@dataclass(frozen=True, slots=True)
class ResumoCalibracao:
    """Métricas consolidadas da amostra elegível para calibração."""

    total_eventos: int
    eventos_elegiveis: int
    eventos_excluidos: int
    erro_medio_percentual_juros: Decimal
    erro_maximo_percentual_juros: Decimal
    erro_medio_percentual_prestacao: Decimal
    erro_maximo_percentual_prestacao: Decimal
    erro_medio_percentual_saldo: Decimal
    erro_maximo_percentual_saldo: Decimal
    atende_tolerancia_juros: bool
    atende_tolerancia_prestacao: bool
    atende_tolerancia_saldo: bool

    @property
    def atende_todas_as_tolerancias(self) -> bool:
        """Indica se todos os erros máximos atendem às tolerâncias definidas."""
        return (
            self.atende_tolerancia_juros
            and self.atende_tolerancia_prestacao
            and self.atende_tolerancia_saldo
        )
