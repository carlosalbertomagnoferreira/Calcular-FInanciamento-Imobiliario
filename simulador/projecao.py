"""Projeção de parcelas futuras a partir do histórico validado."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

from modelos import CenarioProjecao
from simulador.calculos import calcular_taxa_mensal
from simulador.parcelas import COLUNA_NUMERO_PARCELA, COLUNA_PARCELA_VALIDA

CENTAVO = Decimal("0.01")


def criar_cenario_padrao(
    historico: pd.DataFrame,
    parcelas_restantes: int = 235,
    tr_mensal: Decimal | None = None,
) -> CenarioProjecao:
    """Cria o cenário padrão com a última parcela válida e a TR média histórica."""
    validas = historico.loc[historico[COLUNA_PARCELA_VALIDA]].sort_values("Data")
    if validas.empty:
        raise ValueError("Não há parcelas válidas para iniciar a projeção.")
    ultima = validas.iloc[-1]
    tr_observadas = [tr for tr in validas["TR Histórica"] if tr is not None]
    if not tr_observadas and tr_mensal is None:
        raise ValueError("Não há TR histórica para criar o cenário padrão.")

    data_ultima = ultima["Data"]
    return CenarioProjecao(
        saldo_inicial=ultima["Saldo Atualizado"],
        data_inicio=_adicionar_meses(data_ultima, 1),
        numero_primeira_parcela=int(ultima[COLUNA_NUMERO_PARCELA]) + 1,
        parcelas_restantes=parcelas_restantes,
        taxa_mensal=calcular_taxa_mensal(Decimal("0.05116")),
        tr_mensal=(
            tr_mensal
            if tr_mensal is not None
            else sum(tr_observadas, Decimal(0)) / len(tr_observadas)
        ),
        acessorios_mensais=ultima["Acessórios"],
    )


def projetar_contrato(cenario: CenarioProjecao) -> pd.DataFrame:
    """Projeta parcelas PRICE com recálculo mensal após a correção pela TR."""
    saldo = cenario.saldo_inicial
    registros: list[dict[str, object]] = []
    for indice in range(cenario.parcelas_restantes):
        restantes = cenario.parcelas_restantes - indice
        data = _adicionar_meses(cenario.data_inicio, indice)
        correcao = _arredondar(saldo * cenario.tr_mensal)
        saldo_corrigido = saldo + correcao
        juros = _arredondar(saldo_corrigido * cenario.taxa_mensal)
        if restantes == 1:
            amortizacao = saldo_corrigido
            prestacao_financeira = juros + amortizacao
        else:
            prestacao_financeira = _prestacao_price(
                saldo_corrigido, cenario.taxa_mensal, restantes
            )
            amortizacao = prestacao_financeira - juros
        saldo_final = saldo_corrigido - amortizacao
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
                "Amortização": amortizacao,
                "Acessórios": cenario.acessorios_mensais,
                "Prestação Financeira": prestacao_financeira,
                "Prestação": prestacao_financeira + cenario.acessorios_mensais,
                "Saldo Final": saldo_final,
            }
        )
        saldo = saldo_final
    return pd.DataFrame.from_records(registros)


def _prestacao_price(saldo: Decimal, taxa: Decimal, parcelas: int) -> Decimal:
    if taxa == 0:
        return _arredondar(saldo / parcelas)
    fator = (Decimal(1) + taxa) ** parcelas
    return _arredondar(saldo * taxa * fator / (fator - Decimal(1)))


def _arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def _adicionar_meses(data: date, meses: int) -> date:
    total = data.year * 12 + data.month - 1 + meses
    return date(total // 12, total % 12 + 1, data.day)
