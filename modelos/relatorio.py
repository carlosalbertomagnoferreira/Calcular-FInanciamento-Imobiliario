from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ResumoFinanceiro:
    saldo_atual: Decimal
    saldo_final_projetado: Decimal
    total_pago_historico: Decimal
    total_restante_projetado: Decimal
    total_juros_historico: Decimal
    total_juros_projetado: Decimal
    data_quitacao: date
    proxima_prestacao: Decimal
