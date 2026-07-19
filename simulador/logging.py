"""Configuração de logging para a interface de linha de comando."""

import logging

_NIVEIS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def configurar_logging(nivel: str) -> None:
    """Configura logs no stderr sem interferir na saída financeira da CLI."""
    nivel_normalizado = nivel.upper()
    nivel_numerico = _NIVEIS.get(nivel_normalizado)
    if nivel_numerico is None:
        opcoes = ", ".join(_NIVEIS)
        raise ValueError(f"Use um nível de log válido: {opcoes}.")
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger().setLevel(nivel_numerico)
