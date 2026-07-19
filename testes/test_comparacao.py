from datetime import date
from decimal import Decimal

import pandas as pd

from simulador.comparacao import comparar_projecoes


def test_compara_metricas_das_projecoes() -> None:
    original = pd.DataFrame(
        {
            "Data": [date(2026, 8, 10), date(2026, 9, 10)],
            "Juros": [Decimal("10"), Decimal("8")],
            "Prestação": [Decimal("100"), Decimal("100")],
            "Saldo Final": [Decimal("900"), Decimal("0")],
        }
    )
    cenario = pd.DataFrame(
        {
            "Data": [date(2026, 8, 10)],
            "Juros": [Decimal("7")],
            "Prestação": [Decimal("90")],
            "Total Pago": [Decimal("120")],
            "Saldo Final": [Decimal("0")],
        }
    )
    resumo = comparar_projecoes(original, cenario)

    assert resumo.juros_economizados == Decimal("11")
    assert resumo.meses_abatidos == 1
    assert resumo.diferenca_prestacao == Decimal("10")
    assert resumo.data_quitacao_cenario == date(2026, 8, 10)
