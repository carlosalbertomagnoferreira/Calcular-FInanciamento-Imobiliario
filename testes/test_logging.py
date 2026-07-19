"""Testes da configuração de logging."""

import logging

import pytest

from simulador import configurar_logging


def test_configura_nivel_de_logging() -> None:
    nivel_anterior = logging.getLogger().level
    try:
        configurar_logging("info")
        assert logging.getLogger().level == logging.INFO
    finally:
        logging.getLogger().setLevel(nivel_anterior)


def test_rejeita_nivel_de_logging_invalido() -> None:
    with pytest.raises(ValueError, match="nível de log válido"):
        configurar_logging("verbose")
