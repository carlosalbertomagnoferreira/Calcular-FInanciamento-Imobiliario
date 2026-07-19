"""Testes do motor de planejamento de metas."""

from datetime import date
from decimal import Decimal
from typing import Literal

import pytest

from modelos import CenarioProjecao, EstrategiaAmortizacao, MetaQuitacao
from simulador import encontrar_aporte_minimo_quitacao
from simulador.amortizacao import criar_agenda_estrategia, projetar_com_amortizacoes


def _cenario() -> CenarioProjecao:
    return CenarioProjecao(
        saldo_inicial=Decimal("1000.00"),
        data_inicio=date(2026, 1, 10),
        numero_primeira_parcela=1,
        parcelas_restantes=12,
        taxa_mensal=Decimal("0.01"),
        tr_mensal=Decimal("0.00"),
        acessorios_mensais=Decimal("10.00"),
    )


def _estrategia(
    frequencia: Literal["unica", "mensal", "anual"] = "unica",
) -> EstrategiaAmortizacao:
    return EstrategiaAmortizacao(
        nome="Meta",
        valor=Decimal("1.00"),
        data_inicio=date(2026, 1, 2),
        data_fim=date(2026, 4, 12) if frequencia != "unica" else None,
        modo="prazo",
        frequencia=frequencia,
    )


@pytest.mark.parametrize("frequencia", ["unica", "mensal", "anual"])
def test_encontra_aporte_minimo_para_quitar_ate_meta(
    frequencia: Literal["unica", "mensal", "anual"],
) -> None:
    cenario = _cenario()
    resultado = encontrar_aporte_minimo_quitacao(
        cenario, MetaQuitacao(date(2026, 7, 10)), _estrategia(frequencia)
    )

    assert resultado.data_quitacao <= date(2026, 7, 10)
    assert resultado.valor_minimo > 0


def test_aporte_minimo_falha_com_um_centavo_a_menos() -> None:
    cenario = _cenario()
    meta = MetaQuitacao(date(2026, 7, 10))
    resultado = encontrar_aporte_minimo_quitacao(cenario, meta, _estrategia())
    estrategia_menor = EstrategiaAmortizacao(
        nome="Menor",
        valor=resultado.valor_minimo - Decimal("0.01"),
        data_inicio=date(2026, 1, 2),
        modo="prazo",
    )
    projecao_menor = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia_menor)
    )

    assert projecao_menor.iloc[-1]["Data"] > meta.data_alvo


def test_retorna_aporte_nulo_quando_cenario_base_ja_atende_meta() -> None:
    resultado = encontrar_aporte_minimo_quitacao(
        _cenario(), MetaQuitacao(date(2027, 1, 10)), _estrategia()
    )

    assert resultado.meta_ja_cumprida is True
    assert resultado.valor_minimo == Decimal("0.00")


@pytest.mark.parametrize(
    ("meta", "estrategia", "mensagem"),
    [
        (
            MetaQuitacao(date(2025, 12, 10)),
            _estrategia(),
            "anterior ao início",
        ),
        (
            MetaQuitacao(date(2026, 2, 10)),
            EstrategiaAmortizacao(
                nome="Tardia",
                valor=Decimal("1.00"),
                data_inicio=date(2026, 3, 2),
                modo="prazo",
            ),
            "posterior à data-alvo",
        ),
    ],
)
def test_rejeita_meta_inviavel(
    meta: MetaQuitacao, estrategia: EstrategiaAmortizacao, mensagem: str
) -> None:
    with pytest.raises(ValueError, match=mensagem):
        encontrar_aporte_minimo_quitacao(_cenario(), meta, estrategia)
