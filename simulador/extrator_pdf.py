"""Extração determinística do extrato PDF do Banco do Brasil."""

import re
from pathlib import Path

import pandas as pd
import pdfplumber

from simulador.excecoes import (
    ArquivoPDFNaoEncontradoError,
    ExtracaoPDFError,
)
from simulador.leitor import COLUNAS_OBRIGATORIAS, ler_extrato_csv

_VALOR = r"\d{1,3}(?:\.\d{3})*,\d{2}"
_LINHA_EVENTO = re.compile(
    rf"^(?P<data>\d{{2}}/\d{{2}}/\d{{4}})(?P<valores>(?:\s+{_VALOR}){{10}})$"
)


def extrair_extrato_pdf(caminho: str | Path) -> pd.DataFrame:
    """Extrai as linhas financeiras do PDF para o layout canônico do CSV."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ArquivoPDFNaoEncontradoError(f"Arquivo PDF não encontrado: {arquivo}")
    registros: list[list[str]] = []
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            for linha in (pagina.extract_text() or "").splitlines():
                evento = _LINHA_EVENTO.fullmatch(linha.strip())
                if evento is not None:
                    valores_pdf = evento["valores"].split()
                    registros.append(
                        [
                            evento["data"],
                            *valores_pdf[:4],
                            valores_pdf[5],
                            valores_pdf[6],
                            valores_pdf[7],
                            valores_pdf[8],
                            valores_pdf[9],
                            valores_pdf[4],
                        ]
                    )
    if not registros:
        raise ExtracaoPDFError("Nenhuma linha financeira foi encontrada no PDF.")
    return pd.DataFrame(registros, columns=COLUNAS_OBRIGATORIAS)


def converter_pdf_para_csv(pdf: str | Path, csv: str | Path) -> Path:
    """Extrai o PDF, exporta CSV separado e o valida pelo leitor canônico."""
    destino = Path(csv)
    extrato = extrair_extrato_pdf(pdf)
    try:
        extrato.to_csv(destino, sep=";", index=False, encoding="utf-8-sig")
    except OSError as erro:
        raise ExtracaoPDFError(f"Não foi possível gravar o CSV: {destino}") from erro
    try:
        ler_extrato_csv(destino)
    except ValueError as erro:
        raise ExtracaoPDFError(
            "O CSV extraído não passou na validação do extrato."
        ) from erro
    return destino
