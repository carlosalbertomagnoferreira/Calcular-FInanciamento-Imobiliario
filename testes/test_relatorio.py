from pathlib import Path
from decimal import Decimal

from simulador import (
    criar_cenario_padrao,
    gerar_resumo_financeiro,
    identificar_parcelas_validas,
    ler_extrato_csv,
    projetar_contrato,
    reconstruir_historico,
    renderizar_relatorio_markdown,
    renderizar_relatorio_txt,
)


def test_gera_resumo_financeiro_da_projecao() -> None:
    h = identificar_parcelas_validas(
        reconstruir_historico(
            ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")
        )
    )
    resumo = gerar_resumo_financeiro(h, projetar_contrato(criar_cenario_padrao(h)))
    assert resumo.saldo_atual > 0
    assert resumo.saldo_final_projetado == 0
    assert resumo.data_ultima_parcela_paga.isoformat() == "2026-07-10"
    assert resumo.valor_ultima_parcela_paga == Decimal("602.78")
    assert resumo.data_proxima_parcela.isoformat() == "2026-08-10"
    assert resumo.data_quitacao.isoformat() == "2046-02-10"
    assert resumo.total_restante_projetado > 0
    assert "10/02/2046" in renderizar_relatorio_markdown(resumo)
    assert "RELATÓRIO FINANCEIRO" in renderizar_relatorio_txt(resumo)
