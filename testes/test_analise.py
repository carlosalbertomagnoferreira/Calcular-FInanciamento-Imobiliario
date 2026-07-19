"""Testes da orquestração de análise para interfaces."""

from pathlib import Path

from simulador import ler_extrato_csv, preparar_analise


def test_prepara_analise_do_extrato_de_referencia() -> None:
    analise = preparar_analise(
        ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
    )

    assert len(analise.historico) == 164
    assert len(analise.projecao) == 235
    assert analise.resumo.data_quitacao.strftime("%d/%m/%Y") == "10/02/2046"
