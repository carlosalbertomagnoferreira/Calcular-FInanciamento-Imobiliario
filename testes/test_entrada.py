"""Testes da entrada de arquivos enviados ao dashboard."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from simulador import ler_extrato_enviado

RAIZ_PROJETO = Path(__file__).parents[1]


def test_le_csv_enviado_em_diretorio_temporario() -> None:
    extrato = ler_extrato_enviado(
        "contrato.csv", (RAIZ_PROJETO / "extrato.csv").read_bytes()
    )

    assert len(extrato) == 164


def test_le_pdf_enviado_em_diretorio_temporario(
    pdf_textual_bb_mock: MagicMock,
) -> None:
    extrato = ler_extrato_enviado("contrato.pdf", b"%PDF-1.4\n%%EOF\n")

    assert pdf_textual_bb_mock.call_count == 1
    assert len(extrato) == 164


def test_rejeita_extensao_nao_suportada() -> None:
    with pytest.raises(ValueError, match="CSV ou PDF"):
        ler_extrato_enviado("contrato.txt", b"conteudo")
