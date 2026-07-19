"""Testes da interface de linha de comando."""

from pathlib import Path

from typer.testing import CliRunner

from main import app

RAIZ_PROJETO = Path(__file__).parents[1]
runner = CliRunner()


def test_planejar_meta_de_prestacao_exibe_resultado() -> None:
    resultado = runner.invoke(
        app,
        [
            "planejar",
            "--meta-prestacao",
            "600",
            "--data",
            "2026-08-10",
            "--modo",
            "prestacao",
            "--csv",
            str(RAIZ_PROJETO / "extrato.csv"),
        ],
    )

    assert resultado.exit_code == 0
    assert "PLANEJAMENTO — META DE PRESTAÇÃO" in resultado.output
    assert "Meta de prestação: R$ 600.00." in resultado.output
    assert "Prestação sem amortização:" in resultado.output
    assert "Prestação obtida:" in resultado.output


def test_planejar_exige_apenas_uma_meta() -> None:
    resultado = runner.invoke(
        app,
        [
            "planejar",
            "--meta-quitacao",
            "2045-02-10",
            "--meta-prestacao",
            "600",
        ],
    )

    assert resultado.exit_code != 0
    assert "exatamente uma meta" in resultado.output
