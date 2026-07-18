"""Testes da classificação e do resumo de calibração."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from modelos import ClassificacaoEvento, CriteriosCalibracao
from simulador.calibracao import (
    COLUNA_CLASSIFICACAO,
    calibrar_historico,
    classificar_eventos_calibracao,
    gerar_resumo_calibracao,
)
from simulador.leitor import ler_extrato_csv
from simulador.reconstrucao import reconstruir_historico


def test_classifica_eventos_de_referencia_sem_alterar_reconstrucao() -> None:
    extrato = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
    reconstruido = reconstruir_historico(extrato)
    colunas_antes = tuple(reconstruido.columns)

    classificados = classificar_eventos_calibracao(reconstruido)

    assert tuple(reconstruido.columns) == colunas_antes
    assert len(classificados) == 164
    assert (
        classificados.loc[7, COLUNA_CLASSIFICACAO]
        == ClassificacaoEvento.SALDO_ZERO.value
    )
    assert (
        classificados[COLUNA_CLASSIFICACAO] == ClassificacaoEvento.ELEGIVEL.value
    ).sum() == 6


def test_prioriza_inadimplencia_sobre_ausencia_de_amortizacao() -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("0"),
                "Encargos": Decimal("1"),
                "Ajuste de Saldo Não Classificado": Decimal("0"),
                "Resíduo da Prestação": Decimal("0"),
                "Prestação": Decimal("100"),
            }
        ]
    )

    classificados = classificar_eventos_calibracao(reconstruido)

    assert (
        classificados.loc[0, COLUNA_CLASSIFICACAO]
        == ClassificacaoEvento.INADIMPLENCIA.value
    )


def test_usa_tolerancia_configuravel_para_ajuste_de_saldo() -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("10"),
                "Encargos": Decimal("0"),
                "Ajuste de Saldo Não Classificado": Decimal("30"),
                "Resíduo da Prestação": Decimal("0"),
                "Prestação": Decimal("100"),
            }
        ]
    )

    criterios = CriteriosCalibracao(tolerancia_ajuste_saldo=Decimal("30"))
    classificados = classificar_eventos_calibracao(reconstruido, criterios)

    assert (
        classificados.loc[0, COLUNA_CLASSIFICACAO] == ClassificacaoEvento.ELEGIVEL.value
    )


def test_classifica_residuo_relevante_como_componente_nao_identificado() -> None:
    reconstruido = pd.DataFrame(
        [
            {
                "Saldo Devedor": Decimal("100"),
                "Capital": Decimal("10"),
                "Encargos": Decimal("0"),
                "Ajuste de Saldo Não Classificado": Decimal("0"),
                "Resíduo da Prestação": Decimal("2"),
                "Prestação": Decimal("100"),
            }
        ]
    )

    classificados = classificar_eventos_calibracao(reconstruido)

    assert (
        classificados.loc[0, COLUNA_CLASSIFICACAO]
        == ClassificacaoEvento.COMPONENTE_NAO_IDENTIFICADO.value
    )


def test_resumo_calcula_erros_e_aplica_tolerancias() -> None:
    classificados = pd.DataFrame(
        [
            {
                COLUNA_CLASSIFICACAO: ClassificacaoEvento.ELEGIVEL.value,
                "Diferença de Juros": Decimal("1"),
                "Juros": Decimal("100"),
                "Resíduo da Prestação": Decimal("0.50"),
                "Prestação": Decimal("100"),
                "Ajuste de Saldo Não Classificado": Decimal("0.25"),
                "Saldo Atualizado": Decimal("100"),
            },
            {
                COLUNA_CLASSIFICACAO: ClassificacaoEvento.AJUSTE_RELEVANTE.value,
                "Diferença de Juros": Decimal("99"),
                "Juros": Decimal("100"),
                "Resíduo da Prestação": Decimal("99"),
                "Prestação": Decimal("100"),
                "Ajuste de Saldo Não Classificado": Decimal("99"),
                "Saldo Atualizado": Decimal("100"),
            },
        ]
    )

    resumo = gerar_resumo_calibracao(classificados)

    assert resumo.eventos_elegiveis == 1
    assert resumo.eventos_excluidos == 1
    assert resumo.erro_maximo_percentual_juros == Decimal("1")
    assert resumo.erro_maximo_percentual_prestacao == Decimal("0.500")
    assert resumo.erro_maximo_percentual_saldo == Decimal("0.2500")
    assert resumo.atende_tolerancia_juros
    assert resumo.atende_todas_as_tolerancias


def test_rejeita_resumo_sem_eventos_elegiveis() -> None:
    classificados = pd.DataFrame(
        [{COLUNA_CLASSIFICACAO: ClassificacaoEvento.SALDO_ZERO.value}]
    )

    with pytest.raises(ValueError, match="Não há eventos elegíveis"):
        gerar_resumo_calibracao(classificados)


def test_rejeita_resumo_sem_classificacao() -> None:
    with pytest.raises(ValueError, match="Classifique os eventos"):
        gerar_resumo_calibracao(pd.DataFrame())


def test_rejeita_reconstrucao_sem_colunas_para_classificacao() -> None:
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        classificar_eventos_calibracao(pd.DataFrame())


def test_rejeita_referencia_zero_no_erro_percentual() -> None:
    classificados = pd.DataFrame(
        [
            {
                COLUNA_CLASSIFICACAO: ClassificacaoEvento.ELEGIVEL.value,
                "Diferença de Juros": Decimal("0"),
                "Juros": Decimal("0"),
                "Resíduo da Prestação": Decimal("0"),
                "Prestação": Decimal("100"),
                "Ajuste de Saldo Não Classificado": Decimal("0"),
                "Saldo Atualizado": Decimal("100"),
            }
        ]
    )

    with pytest.raises(ValueError, match="referência para cálculo percentual"):
        gerar_resumo_calibracao(classificados)


def test_rejeita_tolerancia_negativa() -> None:
    with pytest.raises(ValueError, match="não podem ser negativas"):
        CriteriosCalibracao(tolerancia_ajuste_saldo=Decimal("-0.01"))


def test_calibra_historico_de_referencia() -> None:
    extrato = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")

    classificados, resumo = calibrar_historico(extrato)

    assert len(classificados) == 164
    assert resumo.eventos_elegiveis == 6
    assert resumo.eventos_excluidos == 158
