from datetime import date
from decimal import Decimal
from pathlib import Path

from simulador import (
    identificar_parcelas_validas,
    ler_extrato_csv,
    reconstruir_historico,
)
from simulador.projecao import criar_cenario_padrao, projetar_contrato
from simulador.exportacao import exportar_projecao_csv


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


def test_cenario_padrao_usa_media_das_ultimas_12_trs() -> None:
    historico = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    trs = [
        tr
        for tr in historico.loc[historico["Parcela Válida"], "TR Histórica"]
        if tr is not None
    ]

    cenario = criar_cenario_padrao(historico)

    assert cenario.tr_mensal == sum(trs[-12:], Decimal(0)) / 12


def test_exporta_projecao_em_csv_brasileiro(tmp_path: Path) -> None:
    projecao = projetar_contrato(
        criar_cenario_padrao(
            identificar_parcelas_validas(
                reconstruir_historico(
                    ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
                )
            )
        )
    )
    caminho = exportar_projecao_csv(projecao, tmp_path / "projecao.csv")

    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()

    assert caminho.exists()
    assert linhas[0].startswith("Número da Parcela;Data;Saldo Inicial")
    assert linhas[1].startswith("126;10/08/2026;88094,99")
