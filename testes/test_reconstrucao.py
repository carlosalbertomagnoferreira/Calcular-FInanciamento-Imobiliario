"""Testes da reconstrução histórica auditável."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from modelos import EventoHistorico
from simulador.calculos import calcular_juros_estimados, calcular_taxa_mensal
from simulador.leitor import ler_extrato_csv
from simulador.reconstrucao import reconstruir_historico


def test_converte_taxa_efetiva_anual_em_mensal() -> None:
    taxa_mensal = calcular_taxa_mensal(Decimal("0.05116"))

    assert taxa_mensal == Decimal("0.004166515580587960565108553")


def test_calcula_juros_estimados_com_arredondamento_em_centavos() -> None:
    juros = calcular_juros_estimados(
        Decimal("97250.08"),
        Decimal("0.004166515580587960565108553"),
    )

    assert juros == Decimal("405.19")


def test_rejeita_taxas_e_saldos_negativos() -> None:
    with pytest.raises(ValueError, match="taxa efetiva anual"):
        calcular_taxa_mensal(Decimal("-0.01"))

    with pytest.raises(ValueError, match="saldo devedor"):
        calcular_juros_estimados(Decimal("-1"), Decimal("0.01"))

    with pytest.raises(ValueError, match="taxa mensal"):
        calcular_juros_estimados(Decimal("1"), Decimal("-0.01"))


def test_evento_usa_capital_reportado_como_amortizacao() -> None:
    evento = EventoHistorico(
        data=date(2015, 4, 10),
        saldo_devedor=Decimal("97250.08"),
        correcao_monetaria=Decimal("134.05"),
        saldo_atualizado=Decimal("97800.03"),
        prestacao=Decimal("532.93"),
        capital=Decimal("116.18"),
        juros=Decimal("405.25"),
        acessorios=Decimal("10.65"),
        correcao_prestacao=Decimal("134.05"),
        encargos=Decimal("0.00"),
        valor_pago=Decimal("532.93"),
    )

    assert evento.amortizacao_reportada == Decimal("116.18")
    assert evento.residuo_prestacao == Decimal("0.85")
    assert evento.saldo_teorico_sem_ajustes == Decimal("97267.95")
    assert evento.ajuste_saldo_nao_classificado == Decimal("532.08")


def test_tr_nao_e_definida_quando_o_saldo_devedor_e_zero() -> None:
    evento = EventoHistorico(
        data=date(2014, 8, 10),
        saldo_devedor=Decimal("0"),
        correcao_monetaria=Decimal("58.54"),
        saldo_atualizado=Decimal("86201.59"),
        prestacao=Decimal("226.40"),
        capital=Decimal("0"),
        juros=Decimal("211.79"),
        acessorios=Decimal("14.61"),
        correcao_prestacao=Decimal("58.54"),
        encargos=Decimal("0"),
        valor_pago=Decimal("226.40"),
    )

    assert evento.tr_historica is None


def test_reconstroi_extrato_de_referencia_sem_alterar_a_entrada() -> None:
    caminho = Path(__file__).parents[1] / "extrato.csv"
    extrato = ler_extrato_csv(caminho)
    colunas_antes = tuple(extrato.columns)

    reconstruido = reconstruir_historico(extrato)

    assert len(reconstruido) == 164
    assert tuple(extrato.columns) == colunas_antes
    assert reconstruido.loc[0, "Data"] == date(2014, 4, 25)
    assert reconstruido.loc[0, "Amortização Reportada"] == Decimal("0.00")
    assert reconstruido.loc[0, "Ajuste de Saldo Não Classificado"] == Decimal("10.37")
    assert pd.isna(reconstruido.loc[7, "TR Histórica"])


def test_rejeita_dataframe_sem_colunas_obrigatorias() -> None:
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        reconstruir_historico(pd.DataFrame())
