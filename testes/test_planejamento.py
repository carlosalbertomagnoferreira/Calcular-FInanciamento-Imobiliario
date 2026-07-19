"""Testes do motor de planejamento de metas."""

from datetime import date
from decimal import Decimal
from typing import Literal

import pytest

from modelos import (
    CenarioProjecao,
    EstrategiaAmortizacao,
    MetaPrestacao,
    MetaQuitacao,
)
from simulador import (
    encontrar_aporte_minimo_quitacao,
    encontrar_aporte_minimo_prestacao,
    obter_prestacao_posterior_ao_aporte,
    projetar_contrato,
)
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


def test_avalia_primeira_prestacao_posterior_com_acessorios() -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Reduz prestação",
        valor=Decimal("100.00"),
        data_inicio=date(2026, 1, 2),
        modo="prestacao",
    )
    projecao = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia)
    )

    prestacao = obter_prestacao_posterior_ao_aporte(cenario, estrategia, projecao)

    assert prestacao.data == date(2026, 2, 10)
    assert prestacao.valor == projecao.iloc[1]["Prestação"]
    assert prestacao.valor == (
        projecao.iloc[1]["Prestação Financeira"] + cenario.acessorios_mensais
    )


def test_nao_avalia_prestacao_da_propria_data_do_aporte() -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Reduz prestação",
        valor=Decimal("100.00"),
        data_inicio=date(2026, 1, 10),
        modo="prestacao",
    )
    original = projetar_contrato(cenario)
    projecao = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia)
    )

    prestacao = obter_prestacao_posterior_ao_aporte(cenario, estrategia, projecao)

    assert projecao.iloc[0]["Prestação"] == original.iloc[0]["Prestação"]
    assert prestacao.data == date(2026, 2, 10)
    assert prestacao.valor < original.iloc[1]["Prestação"]


def test_quitacao_no_aporte_avalia_prestacao_como_zero() -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Quita",
        valor=Decimal("10000.00"),
        data_inicio=date(2026, 1, 10),
        modo="prestacao",
    )
    projecao = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia)
    )

    prestacao = obter_prestacao_posterior_ao_aporte(cenario, estrategia, projecao)

    assert prestacao.data is None
    assert prestacao.valor == Decimal("0.00")


@pytest.mark.parametrize(
    ("frequencia", "data_fim"),
    [
        ("unica", None),
        ("mensal", date(2026, 4, 12)),
        ("anual", date(2026, 12, 12)),
    ],
)
def test_encontra_aporte_minimo_para_prestacao_alvo(
    frequencia: str, data_fim: date | None
) -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Meta de prestação",
        valor=Decimal("1.00"),
        data_inicio=date(2026, 1, 2),
        modo="prestacao",
        frequencia=frequencia,  # type: ignore[arg-type]
        data_fim=data_fim,
    )
    resultado = encontrar_aporte_minimo_prestacao(
        cenario, MetaPrestacao(Decimal("95.00")), estrategia
    )

    assert resultado.valor_minimo > 0
    assert resultado.prestacao_base.valor > Decimal("95.00")
    assert resultado.prestacao_obtida.valor <= Decimal("95.00")
    assert resultado.prestacao_obtida.data == date(2026, 2, 10)


def test_aporte_para_prestacao_falha_com_um_centavo_a_menos() -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Meta de prestação",
        valor=Decimal("1.00"),
        data_inicio=date(2026, 1, 2),
        modo="prestacao",
    )
    meta = MetaPrestacao(Decimal("95.00"))
    resultado = encontrar_aporte_minimo_prestacao(cenario, meta, estrategia)
    estrategia_menor = EstrategiaAmortizacao(
        nome="Menor",
        valor=resultado.valor_minimo - Decimal("0.01"),
        data_inicio=estrategia.data_inicio,
        modo="prestacao",
    )
    projecao_menor = projetar_com_amortizacoes(
        cenario, criar_agenda_estrategia(cenario, estrategia_menor)
    )
    prestacao_menor = obter_prestacao_posterior_ao_aporte(
        cenario, estrategia_menor, projecao_menor
    )

    assert prestacao_menor.valor > meta.valor_maximo


def test_retorna_aporte_nulo_quando_prestacao_base_ja_atende_meta() -> None:
    cenario = _cenario()
    estrategia = EstrategiaAmortizacao(
        nome="Meta de prestação",
        valor=Decimal("1.00"),
        data_inicio=date(2026, 1, 2),
        modo="prestacao",
    )

    resultado = encontrar_aporte_minimo_prestacao(
        cenario, MetaPrestacao(Decimal("200.00")), estrategia
    )

    assert resultado.meta_ja_cumprida is True
    assert resultado.valor_minimo == Decimal("0.00")
