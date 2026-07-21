"""Fixtures compartilhadas sem armazenar PDFs bancários no repositório."""

import csv
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

RAIZ_PROJETO = Path(__file__).parents[1]
ORDEM_VISUAL_PDF = (
    "Data",
    "Saldo Devedor",
    "Correção Monetária",
    "Saldo Atualizado",
    "Prestação",
    "Capital",
    "Juros",
    "Acessórios",
    "Correção Prestação",
    "Encargos",
    "Valor Pago",
)


@pytest.fixture
def pdf_textual_bb_mock(mocker: MockerFixture) -> MagicMock:
    """Simula as linhas de um PDF textual a partir do CSV anonimizado."""
    with (RAIZ_PROJETO / "extrato.csv").open(
        encoding="utf-8-sig", newline=""
    ) as arquivo_csv:
        registros = list(csv.DictReader(arquivo_csv, delimiter=";"))
    texto = "\n".join(
        " ".join(registro[coluna] for coluna in ORDEM_VISUAL_PDF)
        for registro in registros
    )
    pagina = mocker.Mock()
    pagina.extract_text.return_value = texto
    documento = mocker.MagicMock()
    documento.__enter__.return_value.pages = [pagina]
    return mocker.patch(
        "simulador.extrator_pdf.pdfplumber.open", return_value=documento
    )


@pytest.fixture
def pdf_textual_temporario(tmp_path: Path) -> Path:
    """Cria um marcador PDF temporário, nunca persistido no repositório."""
    caminho = tmp_path / "extrato_fornecido.pdf"
    caminho.write_bytes(b"%PDF-1.4\n%%EOF\n")
    return caminho
