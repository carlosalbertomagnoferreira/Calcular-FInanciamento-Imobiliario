"""Componentes do simulador de financiamento imobiliário."""

from simulador.calibracao import calibrar_historico
from simulador.exportacao import exportar_projecao_csv
from simulador.leitor import ler_extrato_csv
from simulador.parcelas import identificar_parcelas_validas
from simulador.projecao import criar_cenario_padrao, projetar_contrato
from simulador.relatorio import (
    gerar_resumo_financeiro,
    renderizar_relatorio_markdown,
    renderizar_relatorio_txt,
)
from simulador.reconstrucao import reconstruir_historico

__all__ = [
    "calibrar_historico",
    "exportar_projecao_csv",
    "identificar_parcelas_validas",
    "ler_extrato_csv",
    "criar_cenario_padrao",
    "projetar_contrato",
    "gerar_resumo_financeiro",
    "renderizar_relatorio_markdown",
    "renderizar_relatorio_txt",
    "reconstruir_historico",
]
