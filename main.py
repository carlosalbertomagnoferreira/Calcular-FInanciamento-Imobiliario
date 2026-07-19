"""Interface de linha de comando do simulador."""

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import cast
from pathlib import Path

import typer

from simulador import (
    criar_cenario_padrao,
    criar_graficos,
    comparar_projecoes,
    exportar_projecao_csv,
    exportar_graficos,
    gerar_amortizacoes_recorrentes,
    gerar_resumo_financeiro,
    identificar_parcelas_validas,
    ler_extrato_csv,
    normalizar_data_amortizacao,
    projetar_contrato,
    projetar_com_amortizacoes,
    reconstruir_historico,
    renderizar_relatorio_markdown,
    renderizar_relatorio_txt,
)
from modelos import AmortizacaoExtraordinaria, ModoAmortizacao

app = typer.Typer(help="Simulador de financiamento imobiliário do Banco do Brasil.")


def _historico(csv: Path):
    return identificar_parcelas_validas(reconstruir_historico(ler_extrato_csv(csv)))


def _tr_decimal(valor: str | None) -> Decimal | None:
    if valor is None:
        return None
    try:
        tr = Decimal(valor)
    except InvalidOperation as erro:
        raise typer.BadParameter(
            "A TR deve ser um decimal, por exemplo 0.001."
        ) from erro
    if tr < 0:
        raise typer.BadParameter("A TR não pode ser negativa.")
    return tr


def _data(valor: str) -> date:
    try:
        return date.fromisoformat(valor)
    except ValueError as erro:
        raise typer.BadParameter("Use a data no formato AAAA-MM-DD.") from erro


def _modo(valor: str) -> ModoAmortizacao:
    if valor == "parcelas":
        return "prestacao"
    if valor not in {"prazo", "prestacao"}:
        raise typer.BadParameter("Use 'prazo', 'prestacao' ou 'parcelas'.")
    return cast(ModoAmortizacao, valor)


def _amortizacao_programada(
    valor: str, modo: ModoAmortizacao, cenario: object
) -> AmortizacaoExtraordinaria:
    try:
        data_texto, valor_texto = valor.split(":", maxsplit=1)
    except ValueError as erro:
        raise typer.BadParameter("Use AAAA-MM-DD:VALOR.") from erro
    valor_decimal = _tr_decimal(valor_texto)
    if valor_decimal is None:
        raise typer.BadParameter("O valor da amortização é obrigatório.")
    try:
        data = normalizar_data_amortizacao(_data(data_texto), cenario)  # type: ignore[arg-type]
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro
    return AmortizacaoExtraordinaria(data, valor_decimal, modo)


@app.command()
def validar(csv: Path = typer.Option(Path("extrato.csv"), "--csv")) -> None:
    """Valida o extrato e informa a sequência de parcelas encontrada."""
    historico = _historico(csv)
    validas = historico.loc[historico["Parcela Válida"]]
    typer.echo(f"Extrato validado: {len(historico)} eventos.")
    typer.echo(
        f"Parcelas válidas: {len(validas)} ("
        f"{validas.iloc[0]['Número da Parcela']} a "
        f"{validas.iloc[-1]['Número da Parcela']})."
    )


@app.command()
def projetar(
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
    tr: str | None = typer.Option(None, "--tr", help="TR mensal decimal do cenário."),
    saida: Path | None = typer.Option(
        None, "--saida", help="Caminho do CSV para exportar a projeção."
    ),
) -> None:
    """Projeta as parcelas restantes do contrato."""
    historico = _historico(csv)
    projecao = projetar_contrato(
        criar_cenario_padrao(historico, tr_mensal=_tr_decimal(tr))
    )
    primeira = projecao.iloc[0]
    ultima = projecao.iloc[-1]
    typer.echo(
        f"Projeção: parcelas {primeira['Número da Parcela']} a {ultima['Número da Parcela']}."
    )
    typer.echo(f"Quitação prevista: {ultima['Data']:%d/%m/%Y}.")
    typer.echo(
        f"Próxima prestação: {primeira['Data']:%d/%m/%Y} — "
        f"R$ {primeira['Prestação']:.2f}."
    )
    if saida is not None:
        caminho = exportar_projecao_csv(projecao, saida)
        typer.echo(f"Projeção exportada para: {caminho}.")


@app.command()
def relatorio(
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
    formato: str = typer.Option("markdown", "--formato", help="markdown ou txt"),
) -> None:
    """Exibe o relatório financeiro no terminal."""
    if formato not in {"markdown", "txt"}:
        raise typer.BadParameter("Use 'markdown' ou 'txt'.")
    historico = _historico(csv)
    projecao = projetar_contrato(criar_cenario_padrao(historico))
    resumo = gerar_resumo_financeiro(historico, projecao)
    texto = (
        renderizar_relatorio_markdown(resumo)
        if formato == "markdown"
        else renderizar_relatorio_txt(resumo)
    )
    typer.echo(texto)


@app.command()
def graficos(
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
    diretorio: Path = typer.Option(
        Path("graficos"), "--diretorio", help="Diretório para os PNGs gerados."
    ),
) -> None:
    """Gera gráficos do histórico e da projeção do contrato."""
    historico = _historico(csv)
    projecao = projetar_contrato(criar_cenario_padrao(historico))
    arquivos = exportar_graficos(criar_graficos(historico, projecao), diretorio)
    typer.echo(f"Gráficos gerados em: {diretorio}.")
    for caminho in arquivos.values():
        typer.echo(f"- {caminho.name}")


@app.command()
def amortizar(
    valor: str | None = typer.Option(None, "--valor", help="Valor da amortização."),
    data: str | None = typer.Option(None, "--data", help="Data inicial AAAA-MM-DD."),
    modo: str = typer.Option("prazo", "--modo", help="prazo, prestacao ou parcelas"),
    frequencia: str = typer.Option(
        "unica", "--frequencia", help="unica, mensal ou anual"
    ),
    ate: str | None = typer.Option(
        None, "--ate", help="Última data recorrente AAAA-MM-DD."
    ),
    amortizacao: list[str] = typer.Option(
        [], "--amortizacao", help="AAAA-MM-DD:VALOR."
    ),
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
    saida: Path | None = typer.Option(None, "--saida"),
) -> None:
    """Projeta o contrato com amortizações extraordinárias."""
    modo_validado = _modo(modo)
    historico = _historico(csv)
    cenario = criar_cenario_padrao(historico)
    if amortizacao:
        if (
            valor is not None
            or data is not None
            or ate is not None
            or frequencia != "unica"
        ):
            raise typer.BadParameter("Use apenas --amortizacao para agenda programada.")
        agenda = [
            _amortizacao_programada(item, modo_validado, cenario)
            for item in amortizacao
        ]
    else:
        if valor is None:
            raise typer.BadParameter("Informe --valor ou ao menos um --amortizacao.")
        try:
            inicio = normalizar_data_amortizacao(
                _data(data) if data else cenario.data_inicio, cenario
            )
            fim = normalizar_data_amortizacao(_data(ate), cenario) if ate else inicio
        except ValueError as erro:
            raise typer.BadParameter(str(erro)) from erro
        if fim < inicio:
            raise typer.BadParameter("--ate não pode ser anterior à data inicial.")
        meses = {"unica": 1, "mensal": 1, "anual": 12}.get(frequencia)
        if meses is None:
            raise typer.BadParameter("Use 'unica', 'mensal' ou 'anual'.")
        if frequencia != "unica" and ate is None:
            raise typer.BadParameter("Informe --ate para amortizações recorrentes.")
        valor_decimal = _tr_decimal(valor)
        if valor_decimal is None:
            raise typer.BadParameter("O valor da amortização é obrigatório.")
        agenda = gerar_amortizacoes_recorrentes(
            valor_decimal, inicio, fim, modo_validado, meses
        )
    projecao_original = projetar_contrato(cenario)
    projecao = projetar_com_amortizacoes(cenario, agenda)
    ultima = projecao.iloc[-1]
    typer.echo(f"Quitação prevista: {ultima['Data']:%d/%m/%Y}.")
    typer.echo(
        f"Total amortizado: R$ {sum(projecao['Amortização Extraordinária']):.2f}."
    )
    juros_economizados = sum(projecao_original["Juros"]) - sum(projecao["Juros"])
    typer.echo(f"Juros economizados: R$ {juros_economizados:.2f}.")
    data_referencia = agenda[-1].data if frequencia != "unica" else agenda[0].data
    linha_saldo = projecao.loc[projecao["Data"] == data_referencia]
    saldo_apos = linha_saldo.iloc[0]["Saldo Final"] if not linha_saldo.empty else None
    texto_saldo_apos = (
        f"R$ {saldo_apos:.2f}"
        if saldo_apos is not None
        else f"quitado antes de {data_referencia:%d/%m/%Y}"
    )
    if modo_validado == "prazo":
        typer.echo(f"Saldo devedor atual: R$ {cenario.saldo_inicial:.2f}.")
        typer.echo(f"Saldo devedor após amortizar: {texto_saldo_apos}.")
        meses_abatidos = len(projecao_original) - len(projecao)
        anos, meses = divmod(meses_abatidos, 12)
        typer.echo(
            f"Prazo abatido: {meses_abatidos} meses ({anos} anos e {meses} meses)."
        )
    else:
        ultima_paga = (
            historico.loc[historico["Parcela Válida"]].sort_values("Data").iloc[-1]
        )
        typer.echo(f"Saldo devedor atual: R$ {cenario.saldo_inicial:.2f}.")
        typer.echo(f"Saldo devedor após amortizar: {texto_saldo_apos}.")
        typer.echo(
            f"Última parcela paga: {ultima_paga['Data']:%d/%m/%Y} — "
            f"R$ {ultima_paga['Valor Pago']:.2f}."
        )
        typer.echo("Próximas cinco prestações:")
        for sem_amortizacao, com_amortizacao in zip(
            projecao_original.head(5).itertuples(), projecao.head(5).itertuples()
        ):
            diferenca = cast(Decimal, sem_amortizacao.Prestação) - cast(
                Decimal, com_amortizacao.Prestação
            )
            typer.echo(
                f"- {sem_amortizacao.Data:%d/%m/%Y}: "
                f"sem amortização R$ {sem_amortizacao.Prestação:.2f}; "
                f"com amortização R$ {com_amortizacao.Prestação:.2f}; "
                f"diferença R$ {diferenca:.2f}."
            )
    if saida is not None:
        caminho = exportar_projecao_csv(projecao, saida)
        typer.echo(f"Projeção exportada para: {caminho}.")


@app.command()
def comparar(
    valor: str | None = typer.Option(None, "--valor"),
    data: str | None = typer.Option(None, "--data"),
    modo: str = typer.Option("prazo", "--modo"),
    frequencia: str = typer.Option("unica", "--frequencia"),
    ate: str | None = typer.Option(None, "--ate"),
    amortizacao: list[str] = typer.Option([], "--amortizacao"),
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
) -> None:
    """Compara a projeção original com um cenário de amortização."""
    modo_validado = _modo(modo)
    historico = _historico(csv)
    cenario = criar_cenario_padrao(historico)
    if amortizacao:
        if (
            valor is not None
            or data is not None
            or ate is not None
            or frequencia != "unica"
        ):
            raise typer.BadParameter("Use apenas --amortizacao para agenda programada.")
        agenda = [
            _amortizacao_programada(item, modo_validado, cenario)
            for item in amortizacao
        ]
    else:
        if valor is None:
            raise typer.BadParameter("Informe --valor ou ao menos um --amortizacao.")
        try:
            inicio = normalizar_data_amortizacao(
                _data(data) if data else cenario.data_inicio, cenario
            )
            fim = normalizar_data_amortizacao(_data(ate), cenario) if ate else inicio
        except ValueError as erro:
            raise typer.BadParameter(str(erro)) from erro
        if fim < inicio:
            raise typer.BadParameter("--ate não pode ser anterior à data inicial.")
        meses = {"unica": 1, "mensal": 1, "anual": 12}.get(frequencia)
        if meses is None:
            raise typer.BadParameter("Use 'unica', 'mensal' ou 'anual'.")
        if frequencia != "unica" and ate is None:
            raise typer.BadParameter("Informe --ate para amortizações recorrentes.")
        valor_decimal = _tr_decimal(valor)
        if valor_decimal is None:
            raise typer.BadParameter("O valor da amortização é obrigatório.")
        agenda = gerar_amortizacoes_recorrentes(
            valor_decimal, inicio, fim, modo_validado, meses
        )
    projecao_original = projetar_contrato(cenario)
    projecao_cenario = projetar_com_amortizacoes(cenario, agenda)
    resumo = comparar_projecoes(projecao_original, projecao_cenario)
    typer.echo("COMPARAÇÃO DE CENÁRIOS")
    typer.echo(f"Juros economizados: R$ {resumo.juros_economizados:.2f}.")
    typer.echo(f"Economia total: R$ {resumo.economia_total:.2f}.")
    typer.echo(
        f"Quitação: {resumo.data_quitacao_original:%d/%m/%Y} → "
        f"{resumo.data_quitacao_cenario:%d/%m/%Y}."
    )
    typer.echo(f"Prazo abatido: {resumo.meses_abatidos} meses.")
    typer.echo(
        f"Próxima prestação: R$ {resumo.prestacao_original:.2f} → "
        f"R$ {resumo.prestacao_cenario:.2f} "
        f"(diferença R$ {resumo.diferenca_prestacao:.2f})."
    )
    if frequencia == "unica":
        typer.echo(
            f"Saldo após a próxima parcela: R$ {resumo.saldo_original:.2f} → "
            f"R$ {resumo.saldo_cenario:.2f}."
        )
    else:
        referencia = agenda[-1].data
        saldo_original = projecao_original.loc[
            projecao_original["Data"] == referencia, "Saldo Final"
        ].iloc[0]
        saldo_cenario = projecao_cenario.loc[
            projecao_cenario["Data"] == referencia, "Saldo Final"
        ].iloc[0]
        typer.echo(
            f"Saldo em {referencia:%d/%m/%Y}: R$ {saldo_original:.2f} → "
            f"R$ {saldo_cenario:.2f}."
        )
    if modo_validado == "prestacao":
        typer.echo("Próximas cinco prestações:")
        for sem_amortizacao, com_amortizacao in zip(
            projecao_original.head(5).itertuples(),
            projecao_cenario.head(5).itertuples(),
        ):
            diferenca = cast(Decimal, sem_amortizacao.Prestação) - cast(
                Decimal, com_amortizacao.Prestação
            )
            typer.echo(
                f"- {sem_amortizacao.Data:%d/%m/%Y}: "
                f"sem amortização R$ {sem_amortizacao.Prestação:.2f}; "
                f"com amortização R$ {com_amortizacao.Prestação:.2f}; "
                f"diferença R$ {diferenca:.2f}."
            )


if __name__ == "__main__":
    app()
