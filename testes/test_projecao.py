from datetime import date
from decimal import Decimal
from pathlib import Path

from simulador import (
    identificar_parcelas_validas,
    ler_extrato_csv,
    reconstruir_historico,
)
from simulador.projecao import criar_cenario_padrao, projetar_contrato


def test_projeta_235_parcelas_ate_o_vencimento_final() -> None:
    historico = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    cenario = criar_cenario_padrao(historico)
    projecao = projetar_contrato(cenario)
    assert len(projecao) == 235
    assert projecao.iloc[0]["Número da Parcela"] == 126
    assert projecao.iloc[0]["Data"] == date(2026, 8, 10)
    assert projecao.iloc[-1]["Número da Parcela"] == 360
    assert projecao.iloc[-1]["Data"] == date(2046, 2, 10)
    assert projecao.iloc[-1]["Saldo Final"] == Decimal("0.00")


def test_permite_tr_personalizada_zero() -> None:
    historico = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    projecao = projetar_contrato(
        criar_cenario_padrao(historico, tr_mensal=Decimal("0"))
    )
    assert all(valor == Decimal("0.00") for valor in projecao["Correção Monetária"])
