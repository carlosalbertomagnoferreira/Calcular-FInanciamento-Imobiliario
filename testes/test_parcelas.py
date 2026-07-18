"""Testes da identificação de parcelas válidas ancorada no contrato."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from modelos import CriteriosParcelasValidas
from simulador.leitor import ler_extrato_csv
from simulador.parcelas import (
    COLUNA_NUMERO_PARCELA,
    COLUNA_PARCELA_VALIDA,
    identificar_parcelas_validas,
)
from simulador.reconstrucao import reconstruir_historico


def test_identifica_125_parcelas_validas_do_extrato_de_referencia() -> None:
    extrato = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
    reconstruido = reconstruir_historico(extrato)

    parcelas = identificar_parcelas_validas(reconstruido)

    validas = parcelas[parcelas[COLUNA_PARCELA_VALIDA]]
    assert len(validas) == 125
    assert validas.iloc[0][COLUNA_NUMERO_PARCELA] == 1
    assert validas.iloc[-1][COLUNA_NUMERO_PARCELA] == 125
    assert validas.iloc[0]["Data"].isoformat() == "2016-03-10"
    assert validas.iloc[-1]["Data"].isoformat() == "2026-07-10"


def test_mantem_parcelas_de_carencia_com_capital_zero_como_validas() -> None:
    extrato = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
    parcelas = identificar_parcelas_validas(reconstruir_historico(extrato))

    carencia = parcelas[
        parcelas["Data"].map(lambda data: data.isoformat()) == "2020-06-10"
    ].iloc[0]

    assert carencia[COLUNA_PARCELA_VALIDA]
    assert carencia[COLUNA_NUMERO_PARCELA] == 52


def test_ancora_do_contrato_usa_vencimento_no_dia_10() -> None:
    assert CriteriosParcelasValidas().dia_vencimento == 10


def test_rejeita_ancora_com_lacuna_mensal() -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Data": pd.Timestamp("2026-05-10").date(),
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("1"),
                "Encargos": Decimal("0"),
                "Prestação": Decimal("10"),
                "Valor Pago": Decimal("10"),
            },
            {
                "Data": pd.Timestamp("2026-07-10").date(),
                "Saldo Devedor": Decimal("99"),
                "Capital": Decimal("1"),
                "Encargos": Decimal("0"),
                "Prestação": Decimal("10"),
                "Valor Pago": Decimal("10"),
            },
        ]
    )
    criterios = CriteriosParcelasValidas(quantidade_final=2, numero_ultima_parcela=2)

    with pytest.raises(ValueError, match="lacuna mensal"):
        identificar_parcelas_validas(reconstruido, criterios)


def test_rejeita_configuracao_de_ancora_invalida() -> None:
    with pytest.raises(ValueError, match="incompatível"):
        CriteriosParcelasValidas(quantidade_final=2, numero_ultima_parcela=1)

    with pytest.raises(ValueError, match="deve ser positiva"):
        CriteriosParcelasValidas(quantidade_final=0)

    with pytest.raises(ValueError, match="entre 1 e 31"):
        CriteriosParcelasValidas(dia_vencimento=32)


def test_rejeita_ancora_com_eventos_insuficientes_ou_colunas_ausentes() -> None:
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        identificar_parcelas_validas(pd.DataFrame())

    reconstruido = pd.DataFrame(
        [
            {
                "Data": pd.Timestamp("2026-07-10").date(),
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("1"),
                "Encargos": Decimal("0"),
                "Prestação": Decimal("10"),
                "Valor Pago": Decimal("10"),
            }
        ]
    )
    criterios = CriteriosParcelasValidas(quantidade_final=2, numero_ultima_parcela=2)

    with pytest.raises(ValueError, match="eventos suficientes"):
        identificar_parcelas_validas(reconstruido, criterios)


@pytest.mark.parametrize(
    ("data", "capital", "valor_pago", "mensagem"),
    [
        ("2026-07-10", Decimal("1"), Decimal("9"), "perfil de parcela regular"),
    ],
)
def test_rejeita_ancora_com_perfil_irregular(
    data: str,
    capital: Decimal,
    valor_pago: Decimal,
    mensagem: str,
) -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Data": pd.Timestamp(data).date(),
                "Saldo Devedor": Decimal("100"),
                "Capital": capital,
                "Encargos": Decimal("0"),
                "Prestação": Decimal("10"),
                "Valor Pago": valor_pago,
            }
        ]
    )
    criterios = CriteriosParcelasValidas(quantidade_final=1, numero_ultima_parcela=1)

    with pytest.raises(ValueError, match=mensagem):
        identificar_parcelas_validas(reconstruido, criterios)


def test_ignora_evento_fora_do_dia_de_vencimento() -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Data": pd.Timestamp("2026-07-11").date(),
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("1"),
                "Encargos": Decimal("0"),
                "Prestação": Decimal("10"),
                "Valor Pago": Decimal("10"),
            }
        ]
    )
    criterios = CriteriosParcelasValidas(quantidade_final=1, numero_ultima_parcela=1)

    with pytest.raises(ValueError, match="eventos suficientes"):
        identificar_parcelas_validas(reconstruido, criterios)
