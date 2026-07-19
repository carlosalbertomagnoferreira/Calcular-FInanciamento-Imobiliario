from datetime import date
from decimal import Decimal
from pathlib import Path

from modelos import AmortizacaoExtraordinaria
from simulador import (
    criar_cenario_padrao,
    gerar_amortizacoes_recorrentes,
    identificar_parcelas_validas,
    ler_extrato_csv,
    projetar_com_amortizacoes,
    projetar_contrato,
    reconstruir_historico,
)


def _cenario():
    historico = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    return criar_cenario_padrao(historico)


def test_amortizacao_com_reducao_de_prazo_antecipa_quitacao() -> None:
    cenario = _cenario()
    original = projetar_contrato(cenario)
    amortizada = projetar_com_amortizacoes(
        cenario,
        [AmortizacaoExtraordinaria(date(2026, 8, 10), Decimal("10000"), "prazo")],
    )

    assert len(amortizada) < len(original)
    assert amortizada.iloc[-1]["Saldo Final"] == Decimal("0.00")
    assert amortizada["Amortização Extraordinária"].sum() == Decimal("10000")


def test_amortizacao_com_reducao_de_prestacao_mantem_prazo() -> None:
    cenario = _cenario()
    original = projetar_contrato(cenario)
    amortizada = projetar_com_amortizacoes(
        cenario,
        [AmortizacaoExtraordinaria(date(2026, 8, 10), Decimal("10000"), "prestacao")],
    )

    assert len(amortizada) == len(original)
    assert amortizada.iloc[-1]["Data"] == original.iloc[-1]["Data"]
    assert amortizada.iloc[1]["Prestação"] < original.iloc[1]["Prestação"]


def test_gera_agendas_mensal_e_anual() -> None:
    mensal = gerar_amortizacoes_recorrentes(
        Decimal("100"), date(2026, 8, 10), date(2026, 10, 10), "prazo", 1
    )
    anual = gerar_amortizacoes_recorrentes(
        Decimal("100"), date(2026, 8, 10), date(2028, 8, 10), "prestacao", 12
    )

    assert [evento.data for evento in mensal] == [
        date(2026, 8, 10),
        date(2026, 9, 10),
        date(2026, 10, 10),
    ]
    assert len(anual) == 3
