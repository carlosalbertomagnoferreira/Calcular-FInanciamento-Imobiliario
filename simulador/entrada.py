"""Entrada segura de extratos enviados por interfaces externas."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from simulador.extrator_pdf import converter_pdf_para_csv
from simulador.leitor import ler_extrato_csv


def ler_extrato_enviado(nome: str, conteudo: bytes) -> pd.DataFrame:
    """Lê um CSV ou PDF enviado sem persistir arquivos fora do diretório temporário."""
    sufixo = Path(nome).suffix.lower()
    if sufixo not in {".csv", ".pdf"}:
        raise ValueError("Envie um arquivo CSV ou PDF.")
    with TemporaryDirectory(prefix="financiamento_bb_") as diretorio:
        origem = Path(diretorio) / f"extrato{sufixo}"
        origem.write_bytes(conteudo)
        if sufixo == ".csv":
            return ler_extrato_csv(origem)
        destino = Path(diretorio) / "extrato_extraido.csv"
        converter_pdf_para_csv(origem, destino)
        return ler_extrato_csv(destino)
