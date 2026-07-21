"""Dashboard Streamlit do simulador de financiamento."""

from datetime import date
from decimal import Decimal
from typing import cast

import pandas as pd
import streamlit as st

from modelos import (
    EstrategiaAmortizacao,
    FrequenciaAmortizacao,
    MetaPrestacao,
    MetaQuitacao,
    ModoAmortizacao,
)
from simulador import (
    comparar_estrategias,
    comparar_parcelas,
    criar_agenda_estrategia,
    criar_cenario_padrao,
    criar_graficos,
    encontrar_aporte_minimo_prestacao,
    encontrar_aporte_minimo_quitacao,
    ler_extrato_enviado,
    preparar_analise,
    projetar_com_amortizacoes,
    renderizar_relatorio_markdown,
    serializar_projecao_csv,
)

st.set_page_config(page_title="Simulador de Financiamento BB", layout="wide")
st.title("Simulador de Financiamento BB")
st.caption("Envie um extrato CSV ou um PDF textual do Banco do Brasil.")


def _moeda(valor: Decimal) -> str:
    """Formata valores financeiros no padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_valor_tabela(valor: object) -> object:
    """Formata um valor financeiro ou uma data para apresentação."""
    if isinstance(valor, Decimal):
        return _moeda(valor)
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return valor


def _formatar_tabela_financeira(dados: pd.DataFrame) -> pd.DataFrame:
    """Aplica formato brasileiro a datas e valores na tabela de apresentação."""
    return dados.map(_formatar_valor_tabela)


arquivo = st.file_uploader("Extrato", type=["csv", "pdf"])
if arquivo is None:
    st.info("Envie um CSV ou PDF para validar os dados e iniciar a análise.")
else:
    try:
        extrato = ler_extrato_enviado(arquivo.name, arquivo.getvalue())
    except ValueError as erro:
        st.error(str(erro))
    else:
        st.success(f"Extrato validado: {len(extrato)} eventos.")
        analise = preparar_analise(extrato)
        resumo, projecao, graficos = st.tabs(["Resumo", "Projeção", "Gráficos"])
        with resumo:
            st.metric("Saldo atual", _moeda(analise.resumo.saldo_atual))
            st.metric("Próxima prestação", _moeda(analise.resumo.proxima_prestacao))
            st.metric("Quitação prevista", f"{analise.resumo.data_quitacao:%d/%m/%Y}")
        with projecao:
            st.dataframe(
                _formatar_tabela_financeira(analise.projecao),
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Baixar projeção CSV",
                serializar_projecao_csv(analise.projecao),
                "projecao.csv",
                "text/csv",
            )
            st.download_button(
                "Baixar relatório",
                renderizar_relatorio_markdown(analise.resumo),
                "relatorio.md",
                "text/markdown",
            )
        with graficos:
            for figura in criar_graficos(analise.historico, analise.projecao).values():
                st.pyplot(figura, clear_figure=True)

        with st.expander("Simulações avançadas"):
            cenario = criar_cenario_padrao(analise.historico)
            valor = Decimal(str(st.number_input("Aporte (R$)", min_value=0.01)))
            data_aporte = st.date_input("Data do aporte", value=cenario.data_inicio)
            modo = st.selectbox("Modo", ["prazo", "prestacao"])
            frequencia = st.selectbox(
                "Frequência dos aportes", ["unica", "mensal", "anual"]
            )
            data_fim = None
            if frequencia != "unica":
                data_fim = st.date_input(
                    "Último aporte",
                    value=date(2045, 2, 10),
                    min_value=data_aporte,
                )
            estrategia = EstrategiaAmortizacao(
                "Dashboard",
                valor,
                data_aporte,
                cast(ModoAmortizacao, modo),
                cast(FrequenciaAmortizacao, frequencia),
                data_fim,
            )
            if st.button("Simular e comparar"):
                simulacao = projetar_com_amortizacoes(
                    cenario, criar_agenda_estrategia(cenario, estrategia)
                )
                comparacao = comparar_estrategias(cenario, [estrategia])[0]
                st.subheader("Simulação comparada ao cenário-base")
                st.caption(
                    "Economia na prestação e redução do saldo correspondem ao "
                    "valor do cenário-base menos o valor simulado."
                )
                st.dataframe(
                    _formatar_tabela_financeira(
                        comparar_parcelas(analise.projecao, simulacao)
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                anos, meses = divmod(comparacao.meses_abatidos, 12)
                st.info(
                    f"Juros economizados: {_moeda(comparacao.juros_economizados)}; quitação: {comparacao.data_quitacao:%d/%m/%Y}."
                )
                st.info(
                    f"Prazo abatido: {comparacao.meses_abatidos} meses "
                    f"({anos} anos e {meses} meses)."
                )
            tipo_meta = st.selectbox("Tipo de meta", ["quitação", "prestação"])
            if tipo_meta == "quitação":
                data_meta_minima = max(
                    cenario.data_inicio,
                    data_aporte.replace(day=cenario.data_inicio.day),
                )
                data_alvo = st.date_input(
                    "Meta de quitação",
                    value=max(date(2045, 2, 10), data_meta_minima),
                    min_value=data_meta_minima,
                )
                if st.button("Planejar meta"):
                    meta_quitacao = encontrar_aporte_minimo_quitacao(
                        cenario, MetaQuitacao(data_alvo), estrategia
                    )
                    st.success(f"Aporte mínimo: {_moeda(meta_quitacao.valor_minimo)}")
                    st.caption(
                        f"Frequência: {meta_quitacao.estrategia.frequencia}; "
                        f"quitação obtida: {meta_quitacao.data_quitacao:%d/%m/%Y}."
                    )
                    st.dataframe(
                        _formatar_tabela_financeira(
                            meta_quitacao.projecao.loc[
                                meta_quitacao.projecao["Data"] <= data_alvo
                            ]
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                valor_alvo = Decimal(
                    str(st.number_input("Prestação máxima (R$)", min_value=0.0))
                )
                if st.button("Planejar meta"):
                    meta_prestacao = encontrar_aporte_minimo_prestacao(
                        cenario, MetaPrestacao(valor_alvo), estrategia
                    )
                    st.success(f"Aporte mínimo: {_moeda(meta_prestacao.valor_minimo)}")
                    st.caption(
                        f"Frequência: {meta_prestacao.estrategia.frequencia}; "
                        "a tabela mostra as novas parcelas projetadas."
                    )
                    st.dataframe(
                        _formatar_tabela_financeira(meta_prestacao.projecao),
                        use_container_width=True,
                        hide_index=True,
                    )
