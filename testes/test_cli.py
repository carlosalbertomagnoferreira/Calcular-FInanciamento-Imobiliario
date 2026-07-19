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


def test_extrair_pdf_gera_csv_validado(tmp_path: Path) -> None:
    destino = tmp_path / "extrato_extraido.csv"
    resultado = runner.invoke(
        app,
        [
            "extrair-pdf",
            "--pdf",
            str(RAIZ_PROJETO / "extrato319405086.pdf"),
            "--saida",
            str(destino),
        ],
    )

    assert resultado.exit_code == 0
    assert "PDF extraído e validado: 164 eventos." in resultado.output
    assert destino.exists()


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


def test_comandos_de_consulta_e_exportacao(tmp_path: Path) -> None:
    csv_projecao = tmp_path / "projecao.csv"
    diretorio_graficos = tmp_path / "graficos"
    comandos = [
        (
            ["validar", "--csv", str(RAIZ_PROJETO / "extrato.csv")],
            "Parcelas válidas: 125",
        ),
        (
            [
                "projetar",
                "--csv",
                str(RAIZ_PROJETO / "extrato.csv"),
                "--saida",
                str(csv_projecao),
            ],
            "Projeção exportada para:",
        ),
        (
            [
                "relatorio",
                "--csv",
                str(RAIZ_PROJETO / "extrato.csv"),
                "--formato",
                "txt",
            ],
            "RELATÓRIO FINANCEIRO",
        ),
        (
            [
                "graficos",
                "--csv",
                str(RAIZ_PROJETO / "extrato.csv"),
                "--diretorio",
                str(diretorio_graficos),
            ],
            "Gráficos gerados em:",
        ),
    ]

    for argumentos, texto_esperado in comandos:
        resultado = runner.invoke(app, argumentos)
        assert resultado.exit_code == 0
        assert texto_esperado in resultado.output

    assert csv_projecao.exists()
    assert len(list(diretorio_graficos.glob("*.png"))) == 6


def test_amortizar_e_comparar_cenarios() -> None:
    amortizar = runner.invoke(
        app,
        [
            "amortizar",
            "--valor",
            "100",
            "--data",
            "2026-08-10",
            "--modo",
            "parcelas",
            "--csv",
            str(RAIZ_PROJETO / "extrato.csv"),
        ],
    )
    comparar = runner.invoke(
        app,
        [
            "comparar",
            "--estrategia",
            "Única:100:2026-08-10:prazo",
            "--estrategia",
            "Mensal:50:2026-08-10:prestacao:mensal:2026-10-10",
            "--csv",
            str(RAIZ_PROJETO / "extrato.csv"),
        ],
    )

    assert amortizar.exit_code == 0
    assert "Próximas cinco prestações:" in amortizar.output
    assert comparar.exit_code == 0
    assert "COMPARAÇÃO DE ESTRATÉGIAS" in comparar.output
    assert "Única" in comparar.output
    assert "Mensal" in comparar.output
