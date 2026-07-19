"""Cálculos de aporte mínimo para metas financeiras."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

import pandas as pd

from modelos import (
    CenarioProjecao,
    EstrategiaAmortizacao,
    MetaPrestacao,
    MetaQuitacao,
)
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


@dataclass(frozen=True, slots=True)
class PrestacaoPosteriorAporte:
    """Prestação usada para avaliar uma meta após o primeiro aporte.

    ``data`` é ``None`` quando o aporte quita o contrato antes que exista uma
    próxima prestação; nesse caso, ``valor`` é zero.
    """

    data: date | None
    valor: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoMetaPrestacao:
    """Resultado da busca do menor aporte para uma prestação-alvo."""

    estrategia: EstrategiaAmortizacao
    projecao: pd.DataFrame
    prestacao_base: PrestacaoPosteriorAporte
    prestacao_obtida: PrestacaoPosteriorAporte
    meta_ja_cumprida: bool

    @property
    def valor_minimo(self) -> Decimal:
        """Valor de cada aporte da estratégia encontrada."""
        return self.estrategia.valor


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

    estrategia_minima = _encontrar_estrategia_minima(
        estrategia,
        lambda candidata: _data_quitacao(_projetar_estrategia(cenario, candidata))
        <= meta.data_alvo,
    )
    projecao = _projetar_estrategia(cenario, estrategia_minima)
    return ResultadoMetaQuitacao(
        estrategia=estrategia_minima,
        projecao=projecao,
        meta_ja_cumprida=False,
    )


def obter_prestacao_posterior_ao_aporte(
    cenario: CenarioProjecao,
    estrategia: EstrategiaAmortizacao,
    projecao: pd.DataFrame,
) -> PrestacaoPosteriorAporte:
    """Obtém a primeira prestação posterior ao primeiro aporte da estratégia.

    A amortização é aplicada após a prestação regular de sua própria data;
    portanto, a linha da data do aporte não participa da meta. A coluna
    ``Prestação`` já inclui os acessórios contratuais.
    """
    from simulador.amortizacao import normalizar_data_amortizacao

    data_aporte = normalizar_data_amortizacao(estrategia.data_inicio, cenario)
    posteriores = projecao.loc[projecao["Data"] > data_aporte]
    if posteriores.empty:
        return PrestacaoPosteriorAporte(data=None, valor=Decimal("0.00"))
    linha = posteriores.iloc[0]
    data = linha["Data"]
    valor = linha["Prestação"]
    if not isinstance(data, date) or not isinstance(valor, Decimal):
        raise TypeError("A projeção possui uma prestação posterior inválida.")
    return PrestacaoPosteriorAporte(data=data, valor=valor)


def encontrar_aporte_minimo_prestacao(
    cenario: CenarioProjecao,
    meta: MetaPrestacao,
    estrategia: EstrategiaAmortizacao,
) -> ResultadoMetaPrestacao:
    """Encontra o menor aporte para a primeira prestação após o aporte."""
    projecao_base = projetar_contrato(cenario)
    prestacao_base = obter_prestacao_posterior_ao_aporte(
        cenario, estrategia, projecao_base
    )
    if prestacao_base.valor <= meta.valor_maximo:
        return ResultadoMetaPrestacao(
            estrategia=replace(estrategia, valor=Decimal("0.00")),
            projecao=projecao_base,
            prestacao_base=prestacao_base,
            prestacao_obtida=prestacao_base,
            meta_ja_cumprida=True,
        )

    estrategia_minima = _encontrar_estrategia_minima(
        estrategia,
        lambda candidata: obter_prestacao_posterior_ao_aporte(
            cenario, candidata, _projetar_estrategia(cenario, candidata)
        ).valor
        <= meta.valor_maximo,
    )
    projecao = _projetar_estrategia(cenario, estrategia_minima)
    return ResultadoMetaPrestacao(
        estrategia=estrategia_minima,
        projecao=projecao,
        prestacao_base=prestacao_base,
        prestacao_obtida=obter_prestacao_posterior_ao_aporte(
            cenario, estrategia_minima, projecao
        ),
        meta_ja_cumprida=False,
    )


def _encontrar_estrategia_minima(
    estrategia: EstrategiaAmortizacao,
    atende_meta: Callable[[EstrategiaAmortizacao], bool],
) -> EstrategiaAmortizacao:
    """Busca o menor valor em centavos cuja estratégia atende à meta."""
    limite_superior = 1
    while not atende_meta(_estrategia_com_centavos(estrategia, limite_superior)):
        limite_superior *= 2
        if limite_superior > _LIMITE_BUSCA_CENTAVOS:
            raise ValueError("Não foi possível encontrar um aporte viável para a meta.")

    limite_inferior = 0
    while limite_inferior + 1 < limite_superior:
        meio = (limite_inferior + limite_superior) // 2
        if atende_meta(_estrategia_com_centavos(estrategia, meio)):
            limite_superior = meio
        else:
            limite_inferior = meio
    return _estrategia_com_centavos(estrategia, limite_superior)


def _estrategia_com_centavos(
    estrategia: EstrategiaAmortizacao, valor_centavos: int
) -> EstrategiaAmortizacao:
    return replace(
        estrategia, valor=(Decimal(valor_centavos) * CENTAVO).quantize(CENTAVO)
    )


def _projetar_estrategia(
    cenario: CenarioProjecao, estrategia: EstrategiaAmortizacao
) -> pd.DataFrame:
    return projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia)
    )


def _data_quitacao(projecao: pd.DataFrame) -> date:
    """Obtém a data da última prestação da projeção."""
    if projecao.empty:
        raise ValueError("A projeção não possui parcelas para avaliar a quitação.")
    data = projecao.iloc[-1]["Data"]
    if not isinstance(data, date):
        raise TypeError("A projeção possui uma data de quitação inválida.")
    return data
