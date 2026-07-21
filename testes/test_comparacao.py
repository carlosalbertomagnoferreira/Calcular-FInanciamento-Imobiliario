from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from modelos import CenarioProjecao, EstrategiaAmortizacao
from simulador.comparacao import (
    comparar_estrategias,
    comparar_parcelas,
    comparar_projecoes,
)


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


def test_compara_multiplas_estrategias_com_metricas_nomeadas() -> None:
    cenario = CenarioProjecao(
        saldo_inicial=Decimal("1000"),
        data_inicio=date(2026, 8, 10),
        numero_primeira_parcela=126,
        parcelas_restantes=3,
        taxa_mensal=Decimal("0.01"),
        tr_mensal=Decimal("0"),
        acessorios_mensais=Decimal("10"),
    )
    estrategias = [
        EstrategiaAmortizacao(
            nome="Aporte único",
            valor=Decimal("200"),
            data_inicio=date(2026, 8, 10),
            modo="prazo",
        ),
        EstrategiaAmortizacao(
            nome="Aporte mensal",
            valor=Decimal("100"),
            data_inicio=date(2026, 8, 10),
            data_fim=date(2026, 9, 10),
            modo="prestacao",
            frequencia="mensal",
        ),
    ]

    resultados = comparar_estrategias(cenario, estrategias)

    assert [resultado.estrategia.nome for resultado in resultados] == [
        "Aporte único",
        "Aporte mensal",
    ]
    assert resultados[0].aporte_total == Decimal("200")
    assert resultados[1].aporte_total == Decimal("200")
    assert resultados[0].juros_economizados > 0
    assert resultados[0].desembolso_futuro > resultados[0].aporte_total
    assert resultados[0].data_quitacao <= date(2026, 10, 10)
    assert resultados[0].proxima_prestacao > 0
    assert resultados[0].saldo_devedor >= 0


def test_rejeita_estrategias_com_mesmo_nome() -> None:
    cenario = CenarioProjecao(
        saldo_inicial=Decimal("1000"),
        data_inicio=date(2026, 8, 10),
        numero_primeira_parcela=126,
        parcelas_restantes=3,
        taxa_mensal=Decimal("0.01"),
        tr_mensal=Decimal("0"),
        acessorios_mensais=Decimal("0"),
    )
    estrategia = EstrategiaAmortizacao(
        nome="Mesmo nome",
        valor=Decimal("100"),
        data_inicio=date(2026, 8, 10),
        modo="prazo",
    )

    with pytest.raises(ValueError, match="nomes das estratégias"):
        comparar_estrategias(cenario, [estrategia, estrategia])


def test_cria_comparacao_compacta_parcela_a_parcela() -> None:
    base = pd.DataFrame(
        {
            "Número da Parcela": [126, 127],
            "Data": [date(2026, 8, 10), date(2026, 9, 10)],
            "Saldo Corrigido": [Decimal("1000"), Decimal("700")],
            "Prestação": [Decimal("400"), Decimal("400")],
            "Saldo Final": [Decimal("700"), Decimal("300")],
        }
    )
    simulada = pd.DataFrame(
        {
            "Número da Parcela": [126, 127],
            "Data": [date(2026, 8, 10), date(2026, 9, 10)],
            "Saldo Corrigido": [Decimal("1000"), Decimal("500")],
            "Prestação": [Decimal("400"), Decimal("300")],
            "Saldo Final": [Decimal("500"), Decimal("200")],
        }
    )

    comparativo = comparar_parcelas(base, simulada)

    assert tuple(comparativo.columns) == (
        "Número da Parcela",
        "Data",
        "Saldo Corrigido",
        "Prestação Total",
        "Saldo Final",
        "Economia na Prestação",
        "Redução do Saldo",
    )
    assert comparativo.iloc[1]["Prestação Total"] == Decimal("300")
    assert comparativo.iloc[1]["Economia na Prestação"] == Decimal("100")
    assert comparativo.iloc[1]["Redução do Saldo"] == Decimal("100")


def test_rejeita_parcela_simulada_sem_correspondencia_na_base() -> None:
    base = pd.DataFrame(
        {
            "Número da Parcela": [126],
            "Data": [date(2026, 8, 10)],
            "Saldo Corrigido": [Decimal("1000")],
            "Prestação": [Decimal("400")],
            "Saldo Final": [Decimal("700")],
        }
    )
    simulada = base.assign(**{"Número da Parcela": [127]})

    with pytest.raises(ValueError, match="parcela 127"):
        comparar_parcelas(base, simulada)


def test_rejeita_projecao_compacta_sem_colunas_obrigatorias() -> None:
    with pytest.raises(ValueError, match="projeção base.*Saldo Corrigido"):
        comparar_parcelas(
            pd.DataFrame({"Número da Parcela": [126]}),
            pd.DataFrame({"Número da Parcela": [126]}),
        )
