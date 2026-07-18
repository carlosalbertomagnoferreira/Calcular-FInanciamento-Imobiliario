"""Relatórios financeiros derivados do histórico e da projeção."""

from decimal import Decimal

import pandas as pd

from modelos import ResumoFinanceiro
from simulador.parcelas import COLUNA_PARCELA_VALIDA


def gerar_resumo_financeiro(
    historico: pd.DataFrame, projecao: pd.DataFrame
) -> ResumoFinanceiro:
    validas = historico.loc[historico[COLUNA_PARCELA_VALIDA]].sort_values("Data")
    if validas.empty or projecao.empty:
        raise ValueError(
            "Histórico válido e projeção são obrigatórios para o relatório."
        )
    ultima = validas.iloc[-1]
    primeira_projetada = projecao.iloc[0]
    ultima_projetada = projecao.iloc[-1]
    return ResumoFinanceiro(
        saldo_atual=ultima["Saldo Atualizado"],
        saldo_final_projetado=ultima_projetada["Saldo Final"],
        total_pago_historico=_somar(validas["Valor Pago"]),
        total_restante_projetado=_somar(projecao["Prestação"]),
        total_juros_historico=_somar(validas["Juros"]),
        total_juros_projetado=_somar(projecao["Juros"]),
        data_quitacao=ultima_projetada["Data"],
        proxima_prestacao=primeira_projetada["Prestação"],
    )


def renderizar_relatorio_markdown(resumo: ResumoFinanceiro) -> str:
    """Renderiza o resumo sem incluir hipóteses de economia ainda indisponíveis."""
    return "\n".join(
        (
            "# Relatório Financeiro",
            "",
            f"- Saldo atual: {_moeda(resumo.saldo_atual)}",
            f"- Saldo final projetado: {_moeda(resumo.saldo_final_projetado)}",
            f"- Total pago histórico: {_moeda(resumo.total_pago_historico)}",
            f"- Total restante projetado: {_moeda(resumo.total_restante_projetado)}",
            f"- Juros históricos: {_moeda(resumo.total_juros_historico)}",
            f"- Juros projetados: {_moeda(resumo.total_juros_projetado)}",
            f"- Próxima prestação: {_moeda(resumo.proxima_prestacao)}",
            f"- Data prevista de quitação: {resumo.data_quitacao:%d/%m/%Y}",
            "",
            "Economia de juros será calculada quando houver cenário de amortização para comparação.",
        )
    )


def renderizar_relatorio_txt(resumo: ResumoFinanceiro) -> str:
    """Renderiza o relatório em texto simples para exportação."""
    return (
        renderizar_relatorio_markdown(resumo)
        .replace("# Relatório Financeiro\n\n", "RELATÓRIO FINANCEIRO\n\n")
        .replace("- ", "")
    )


def _somar(valores: pd.Series) -> Decimal:
    return sum(valores, start=Decimal(0))


def _moeda(valor: Decimal) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
