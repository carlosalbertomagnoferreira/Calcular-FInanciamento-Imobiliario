"""Cenário necessário para projetar as parcelas futuras."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CenarioProjecao:
    """Parâmetros explícitos de um cenário de projeção."""

    saldo_inicial: Decimal
    data_inicio: date
    numero_primeira_parcela: int
    parcelas_restantes: int
    taxa_mensal: Decimal
    tr_mensal: Decimal
    acessorios_mensais: Decimal

    def __post_init__(self) -> None:
        if self.saldo_inicial < 0 or self.taxa_mensal < 0 or self.tr_mensal < 0:
            raise ValueError("Saldo e taxas da projeção não podem ser negativos.")
        if self.acessorios_mensais < 0 or self.parcelas_restantes < 1:
            raise ValueError("Acessórios e parcelas restantes devem ser válidos.")
