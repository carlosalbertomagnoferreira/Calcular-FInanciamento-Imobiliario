"""Testes do extrator PDF com o documento de referência."""

from pathlib import Path

from simulador import converter_pdf_para_csv, extrair_extrato_pdf, ler_extrato_csv
from simulador.leitor import COLUNAS_OBRIGATORIAS


def test_extrai_todas_as_linhas_do_pdf_de_referencia() -> None:
    extrato = extrair_extrato_pdf(Path(__file__).parents[1] / "extrato319405086.pdf")

    assert tuple(extrato.columns) == COLUNAS_OBRIGATORIAS
    assert len(extrato) == 164
    assert extrato.iloc[0]["Data"] == "25/04/2014"
    assert extrato.iloc[-1]["Data"] == "10/07/2026"


def test_converte_pdf_para_csv_validado(tmp_path: Path) -> None:
    pdf = Path(__file__).parents[1] / "extrato319405086.pdf"
    destino = converter_pdf_para_csv(pdf, tmp_path / "extrato_extraido.csv")

    extraido = ler_extrato_csv(destino)
    referencia = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")

    assert destino.exists()
    assert extraido.equals(referencia)
