"""Smoke tests da interface Streamlit."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_solicita_arquivo_sem_falhar() -> None:
    app = AppTest.from_file(str(Path(__file__).parents[1] / "dashboard.py")).run()

    assert not app.exception
    assert app.title[0].value == "Simulador de Financiamento BB"
    assert len(app.get("file_uploader")) == 1
    assert "Envie um CSV ou PDF" in app.info[0].value
