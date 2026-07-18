"""Cálculos financeiros puros usados na reconstrução histórica."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, localcontext

CENTAVO = Decimal("0.01")


def calcular_taxa_mensal(taxa_efetiva_anual: Decimal) -> Decimal:
    """Converte uma taxa efetiva anual em taxa efetiva mensal.

    Args:
        taxa_efetiva_anual: Taxa anual decimal, por exemplo ``0.05116``.

    Returns:
        Taxa efetiva mensal sem arredondamento monetário.

    Raises:
        ValueError: Se a taxa anual for negativa.
    """
    if taxa_efetiva_anual < 0:
        raise ValueError("A taxa efetiva anual não pode ser negativa.")

    with localcontext() as contexto:
        contexto.prec = 28
        return (Decimal(1) + taxa_efetiva_anual) ** (Decimal(1) / Decimal(12)) - 1


def calcular_juros_estimados(saldo_devedor: Decimal, taxa_mensal: Decimal) -> Decimal:
    """Estima juros mensais e arredonda o resultado para centavos.

    O resultado é apenas diagnóstico durante a reconstrução: os juros do
    extrato permanecem o valor histórico autoritativo.
    """
    if saldo_devedor < 0:
        raise ValueError("O saldo devedor não pode ser negativo.")
    if taxa_mensal < 0:
        raise ValueError("A taxa mensal não pode ser negativa.")
    return (saldo_devedor * taxa_mensal).quantize(CENTAVO, rounding=ROUND_HALF_UP)
