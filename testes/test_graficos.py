from pathlib import Path

from simulador import (
    criar_cenario_padrao,
    criar_graficos,
    exportar_graficos,
    identificar_parcelas_validas,
    ler_extrato_csv,
    projetar_contrato,
    reconstruir_historico,
)


def test_cria_e_exporta_os_seis_graficos(tmp_path: Path) -> None:
    historico = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    projecao = projetar_contrato(criar_cenario_padrao(historico))

    graficos = criar_graficos(historico, projecao)
    arquivos = exportar_graficos(graficos, tmp_path)

    assert set(arquivos) == {
        "saldo_devedor",
        "prestacao",
        "tr",
        "juros",
        "amortizacao",
        "evolucao_contrato",
    }
    assert all(
        caminho.suffix == ".png" and caminho.stat().st_size > 0
        for caminho in arquivos.values()
    )
