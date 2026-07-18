"""Testes do leitor e validador de extrato CSV."""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from pathlib import Path

import pandas as pd
import pytest

from simulador.excecoes import (
    ArquivoExtratoNaoEncontradoError,
    CampoObrigatorioVazioError,
    ColunasObrigatoriasAusentesError,
    DataInvalidaError,
    LeituraCSVError,
    RegistroDuplicadoError,
    ValorInvalidoError,
)
from simulador.leitor import COLUNAS_OBRIGATORIAS, ler_extrato_csv


def _linha_valida() -> dict[str, str]:
    return {
        "Data": "25/04/2014",
        "Saldo Devedor": "96.676,80",
        "Correção Monetária": "10,37",
        "Saldo Atualizado": "96.687,17",
        "Prestação": "10,37",
        "Juros": "0,00",
        "Acessórios": "10,37",
        "Correção Prestação": "0,00",
        "Encargos": "0,00",
        "Valor Pago": "10,37",
        "Capital": "0,00",
    }


def _criar_csv(tmp_path: Path, linhas: list[dict[str, str]]) -> Path:
    caminho = tmp_path / "extrato.csv"
    pd.DataFrame(linhas).to_csv(
        caminho,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    return caminho


def test_le_normaliza_datas_e_valores_brasileiros(tmp_path: Path) -> None:
    caminho = _criar_csv(tmp_path, [_linha_valida()])

    extrato = ler_extrato_csv(caminho)

    assert extrato.loc[0, "Data"] == pd.Timestamp("2014-04-25")
    assert extrato.loc[0, "Saldo Devedor"] == Decimal("96676.80")
    assert extrato.loc[0, "Valor Pago"] == Decimal("10.37")


def test_normaliza_separador_de_milhar_sem_casas_decimais(tmp_path: Path) -> None:
    linha = _linha_valida()
    linha["Saldo Devedor"] = "1.234"
    caminho = _criar_csv(tmp_path, [linha])

    extrato = ler_extrato_csv(caminho)

    assert extrato.loc[0, "Saldo Devedor"] == Decimal("1234")


def test_rejeita_arquivo_ausente(tmp_path: Path) -> None:
    with pytest.raises(ArquivoExtratoNaoEncontradoError):
        ler_extrato_csv(tmp_path / "ausente.csv")


def test_rejeita_csv_vazio(tmp_path: Path) -> None:
    caminho = tmp_path / "vazio.csv"
    caminho.touch()

    with pytest.raises(LeituraCSVError):
        ler_extrato_csv(caminho)


def test_rejeita_colunas_obrigatorias_ausentes(tmp_path: Path) -> None:
    linha = _linha_valida()
    del linha["Capital"]
    caminho = _criar_csv(tmp_path, [linha])

    with pytest.raises(ColunasObrigatoriasAusentesError, match="Capital"):
        ler_extrato_csv(caminho)


@pytest.mark.parametrize(
    ("campo", "valor", "erro"),
    [
        ("Data", "2014-04-25", DataInvalidaError),
        ("Prestação", "dez reais", ValorInvalidoError),
        ("Juros", "-0,01", ValorInvalidoError),
        ("Encargos", "", CampoObrigatorioVazioError),
    ],
)
def test_rejeita_dados_invalidos(
    tmp_path: Path,
    campo: str,
    valor: str,
    erro: type[Exception],
) -> None:
    linha = _linha_valida()
    linha[campo] = valor
    caminho = _criar_csv(tmp_path, [linha])

    with pytest.raises(erro):
        ler_extrato_csv(caminho)


def test_rejeita_registros_completamente_duplicados(tmp_path: Path) -> None:
    linha = _linha_valida()
    caminho = _criar_csv(tmp_path, [linha, linha])

    with pytest.raises(RegistroDuplicadoError):
        ler_extrato_csv(caminho)


def test_leitura_do_csv_de_referencia_nao_o_altera() -> None:
    caminho = Path(__file__).parents[1] / "extrato.csv"
    conteudo_antes = sha256(caminho.read_bytes()).hexdigest()

    extrato = ler_extrato_csv(caminho)

    assert len(extrato) == 164
    assert tuple(extrato.columns) == COLUNAS_OBRIGATORIAS
    assert sha256(caminho.read_bytes()).hexdigest() == conteudo_antes
