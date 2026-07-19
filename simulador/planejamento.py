"""Cálculos de aporte mínimo para metas financeiras."""

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

import pandas as pd

from modelos import CenarioProjecao, EstrategiaAmortizacao, MetaQuitacao
from simulador.amortizacao import criar_agenda_estrategia, projetar_com_amortizacoes
from simulador.projecao import projetar_contrato

CENTAVO = Decimal("0.01")
_LIMITE_BUSCA_CENTAVOS = 10**18


@dataclass(frozen=True, slots=True)
class ResultadoMetaQuitacao:
    """Resultado da busca do menor aporte que atende a uma meta de quitação."""

    estrategia: EstrategiaAmortizacao
    projecao: pd.DataFrame
    meta_ja_cumprida: bool

    @property
    def valor_minimo(self) -> Decimal:
        """Valor de cada aporte da estratégia encontrada."""
        return self.estrategia.valor

    @property
    def data_quitacao(self) -> date:
        """Data de quitação obtida pela estratégia."""
        return _data_quitacao(self.projecao)


def encontrar_aporte_minimo_quitacao(
    cenario: CenarioProjecao,
    meta: MetaQuitacao,
    estrategia: EstrategiaAmortizacao,
) -> ResultadoMetaQuitacao:
    """Encontra, por busca binária em centavos, o aporte mínimo para a meta.

    ``estrategia`` define data, modo e frequência. Seu valor é substituído pelo
    menor valor encontrado, de modo que o mesmo contrato atende estratégias
    únicas, mensais e anuais.
    """
    projecao_base = projetar_contrato(cenario)
    if _data_quitacao(projecao_base) <= meta.data_alvo:
        return ResultadoMetaQuitacao(
            estrategia=replace(estrategia, valor=Decimal("0.00")),
            projecao=projecao_base,
            meta_ja_cumprida=True,
        )

    if meta.data_alvo < cenario.data_inicio:
        raise ValueError("A data-alvo de quitação é anterior ao início da projeção.")

    inicio_estrategia = estrategia.data_inicio.replace(day=cenario.data_inicio.day)
    if inicio_estrategia > meta.data_alvo:
        raise ValueError(
            "A data inicial da estratégia é posterior à data-alvo de quitação."
        )

    limite_superior = 1
    while not _atinge_meta(cenario, meta, estrategia, limite_superior):
        limite_superior *= 2
        if limite_superior > _LIMITE_BUSCA_CENTAVOS:
            raise ValueError("Não foi possível encontrar um aporte viável para a meta.")

    limite_inferior = 0
    while limite_inferior + 1 < limite_superior:
        meio = (limite_inferior + limite_superior) // 2
        if _atinge_meta(cenario, meta, estrategia, meio):
            limite_superior = meio
        else:
            limite_inferior = meio

    estrategia_minima = replace(
        estrategia,
        valor=(Decimal(limite_superior) * CENTAVO).quantize(CENTAVO),
    )
    projecao = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia_minima)
    )
    return ResultadoMetaQuitacao(
        estrategia=estrategia_minima,
        projecao=projecao,
        meta_ja_cumprida=False,
    )


def _atinge_meta(
    cenario: CenarioProjecao,
    meta: MetaQuitacao,
    estrategia: EstrategiaAmortizacao,
    valor_centavos: int,
) -> bool:
    candidata = replace(
        estrategia, valor=(Decimal(valor_centavos) * CENTAVO).quantize(CENTAVO)
    )
    projecao = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, candidata)
    )
    return _data_quitacao(projecao) <= meta.data_alvo


def _data_quitacao(projecao: pd.DataFrame) -> date:
    """Obtém a data da última prestação da projeção."""
    if projecao.empty:
        raise ValueError("A projeção não possui parcelas para avaliar a quitação.")
    data = projecao.iloc[-1]["Data"]
    if not isinstance(data, date):
        raise TypeError("A projeção possui uma data de quitação inválida.")
    return data
