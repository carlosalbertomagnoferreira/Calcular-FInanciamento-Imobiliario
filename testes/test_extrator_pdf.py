"""Testes do extrator PDF sem armazenar documentos bancários reais."""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from simulador import converter_pdf_para_csv, extrair_extrato_pdf, ler_extrato_csv
from simulador.leitor import COLUNAS_OBRIGATORIAS


def test_extrai_todas_as_linhas_do_pdf_textual_simulado(
    pdf_textual_bb_mock: MagicMock,
    pdf_textual_temporario: Path,
) -> None:
    extrato = extrair_extrato_pdf(pdf_textual_temporario)

    pdf_textual_bb_mock.assert_called_once_with(pdf_textual_temporario)
    assert tuple(extrato.columns) == COLUNAS_OBRIGATORIAS
    assert len(extrato) == 164
    assert extrato.iloc[0]["Data"] == "25/04/2014"
    assert extrato.iloc[-1]["Data"] == "10/07/2026"


def test_converte_pdf_para_csv_validado(
    tmp_path: Path,
    pdf_textual_bb_mock: MagicMock,
    pdf_textual_temporario: Path,
) -> None:
    destino = converter_pdf_para_csv(
        pdf_textual_temporario, tmp_path / "extrato_extraido.csv"
    )

    extraido = ler_extrato_csv(destino)
    referencia = ler_extrato_csv(Path(__file__).parents[1] / "extrato.csv")

    assert destino.exists()
    assert extraido.equals(referencia)


def test_integracao_com_pdf_fornecido_localmente() -> None:
    """Valida opcionalmente um PDF real indicado fora do repositório."""
    caminho_configurado = os.getenv("EXTRATO_PDF_TESTE")
    if caminho_configurado is None:
        pytest.skip("Defina EXTRATO_PDF_TESTE para executar a integração real.")
    assert caminho_configurado is not None

    extrato = extrair_extrato_pdf(Path(caminho_configurado))

    assert tuple(extrato.columns) == COLUNAS_OBRIGATORIAS
    assert not extrato.empty
