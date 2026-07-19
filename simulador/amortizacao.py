"""Aplicação de amortizações extraordinárias à projeção contratual."""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

import pandas as pd

from modelos import AmortizacaoExtraordinaria, CenarioProjecao
from simulador.projecao import (
    _adicionar_meses,
    _arredondar,
    _prestacao_price,
    projetar_contrato,
)


def gerar_amortizacoes_recorrentes(
    valor: Decimal,
    data_inicio: date,
    data_fim: date,
    modo: str,
    frequencia_meses: int,
) -> list[AmortizacaoExtraordinaria]:
    """Gera uma agenda mensal ou anual de amortizações extraordinárias."""
    if frequencia_meses < 1:
        raise ValueError("A frequência deve ter ao menos um mês.")
    agenda: list[AmortizacaoExtraordinaria] = []
    data = data_inicio
    while data <= data_fim:
        agenda.append(AmortizacaoExtraordinaria(data, valor, modo))  # type: ignore[arg-type]
        data = _adicionar_meses(data, frequencia_meses)
    return agenda


def projetar_com_amortizacoes(
    cenario: CenarioProjecao, amortizacoes: Iterable[AmortizacaoExtraordinaria]
) -> pd.DataFrame:
    """Projeta o contrato com amortizações aplicadas após cada prestação regular."""
    agenda = _agrupar_amortizacoes(amortizacoes)
    saldo = cenario.saldo_inicial
    prestacao_prazo_ativa = False
    prestacoes_base = projetar_contrato(cenario)["Prestação Financeira"].tolist()
    registros: list[dict[str, object]] = []
    for indice in range(cenario.parcelas_restantes):
        restantes = cenario.parcelas_restantes - indice
        data = _adicionar_meses(cenario.data_inicio, indice)
        correcao = _arredondar(saldo * cenario.tr_mensal)
        saldo_corrigido = saldo + correcao
        juros = _arredondar(saldo_corrigido * cenario.taxa_mensal)
        prestacao_financeira = (
            prestacoes_base[indice]
            if prestacao_prazo_ativa
            else _prestacao_price(saldo_corrigido, cenario.taxa_mensal, restantes)
        )
        amortizacao_regular = min(prestacao_financeira - juros, saldo_corrigido)
        prestacao_financeira = juros + amortizacao_regular
        saldo_apos_regular = saldo_corrigido - amortizacao_regular
        eventos = agenda.get(data, [])
        extra = min(
            sum((evento.valor for evento in eventos), Decimal(0)), saldo_apos_regular
        )
        saldo_final = saldo_apos_regular - extra
        if any(evento.modo == "prazo" for evento in eventos) and saldo_final > 0:
            prestacao_prazo_ativa = True
        if any(evento.modo == "prestacao" for evento in eventos):
            prestacao_prazo_ativa = False
        registros.append(
            {
                "Número da Parcela": cenario.numero_primeira_parcela + indice,
                "Data": data,
                "Saldo Inicial": saldo,
                "TR Projetada": cenario.tr_mensal,
                "Correção Monetária": correcao,
                "Saldo Corrigido": saldo_corrigido,
                "Taxa Mensal": cenario.taxa_mensal,
                "Juros": juros,
                "Amortização": amortizacao_regular,
                "Amortização Extraordinária": extra,
                "Acessórios": cenario.acessorios_mensais,
                "Prestação Financeira": prestacao_financeira,
                "Prestação": prestacao_financeira + cenario.acessorios_mensais,
                "Total Pago": prestacao_financeira + cenario.acessorios_mensais + extra,
                "Saldo Final": saldo_final,
            }
        )
        saldo = saldo_final
        if saldo == 0:
            break
    return pd.DataFrame.from_records(registros)


def _agrupar_amortizacoes(
    amortizacoes: Iterable[AmortizacaoExtraordinaria],
) -> dict[date, list[AmortizacaoExtraordinaria]]:
    agenda: dict[date, list[AmortizacaoExtraordinaria]] = {}
    for evento in amortizacoes:
        agenda.setdefault(evento.data, []).append(evento)
    return agenda
