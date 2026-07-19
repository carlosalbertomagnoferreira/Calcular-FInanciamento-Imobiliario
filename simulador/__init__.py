"""Componentes do simulador de financiamento imobiliário."""

from simulador.calibracao import calibrar_historico
from simulador.comparacao import comparar_estrategias, comparar_projecoes
from simulador.amortizacao import (
    gerar_amortizacoes_recorrentes,
    criar_agenda_estrategia,
    normalizar_data_amortizacao,
    projetar_com_amortizacoes,
)
from simulador.exportacao import exportar_projecao_csv
from simulador.graficos import criar_graficos, exportar_graficos
from simulador.leitor import ler_extrato_csv
from simulador.parcelas import identificar_parcelas_validas
from simulador.projecao import criar_cenario_padrao, projetar_contrato
from simulador.planejamento import (
    PrestacaoPosteriorAporte,
    ResultadoMetaQuitacao,
    ResultadoMetaPrestacao,
    encontrar_aporte_minimo_quitacao,
    encontrar_aporte_minimo_prestacao,
    obter_prestacao_posterior_ao_aporte,
)
from simulador.relatorio import (
    gerar_resumo_financeiro,
    renderizar_relatorio_markdown,
    renderizar_relatorio_txt,
)
from simulador.reconstrucao import reconstruir_historico

__all__ = [
    "calibrar_historico",
    "comparar_projecoes",
    "comparar_estrategias",
    "gerar_amortizacoes_recorrentes",
    "criar_agenda_estrategia",
    "normalizar_data_amortizacao",
    "exportar_projecao_csv",
    "criar_graficos",
    "exportar_graficos",
    "identificar_parcelas_validas",
    "ler_extrato_csv",
    "criar_cenario_padrao",
    "encontrar_aporte_minimo_quitacao",
    "encontrar_aporte_minimo_prestacao",
    "obter_prestacao_posterior_ao_aporte",
    "projetar_contrato",
    "projetar_com_amortizacoes",
    "ResultadoMetaQuitacao",
    "ResultadoMetaPrestacao",
    "PrestacaoPosteriorAporte",
    "gerar_resumo_financeiro",
    "renderizar_relatorio_markdown",
    "renderizar_relatorio_txt",
    "reconstruir_historico",
]
