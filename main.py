"""Interface de linha de comando do simulador."""

from datetime import date
from decimal import Decimal, InvalidOperation
import logging
from typing import cast
from pathlib import Path

import typer

from simulador import (
    comparar_estrategias,
    converter_pdf_para_csv,
    criar_agenda_estrategia,
    criar_cenario_padrao,
    criar_graficos,
    comparar_projecoes,
    configurar_logging,
    encontrar_aporte_minimo_quitacao,
    encontrar_aporte_minimo_prestacao,
    exportar_projecao_csv,
    exportar_graficos,
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
from modelos import (
    AmortizacaoExtraordinaria,
    CenarioProjecao,
    EstrategiaAmortizacao,
    FrequenciaAmortizacao,
    MetaPrestacao,
    MetaQuitacao,
    ModoAmortizacao,
)

app = typer.Typer(help="Simulador de financiamento imobiliário do Banco do Brasil.")
logger = logging.getLogger(__name__)

AJUDA_ESTRATEGIA = """Formato de --estrategia

Repita a opção uma vez para cada cenário a comparar. Ela não pode ser combinada
com --valor, --data, --modo, --frequencia, --ate ou --amortizacao.

Estratégia única:
  NOME:VALOR:DATA:MODO

Estratégia recorrente:
  NOME:VALOR:DATA:MODO:FREQUENCIA:ATE

Campos:
  NOME        identificador único, sem o caractere ':'
  VALOR       decimal positivo, por exemplo 10000 ou 500.50
  DATA        primeira data do aporte, no formato AAAA-MM-DD
  MODO        prazo, prestacao ou parcelas
  FREQUENCIA  mensal ou anual
  ATE         última data do aporte, no formato AAAA-MM-DD

Exemplos:
  --estrategia 'Prazo:10000:2026-08-10:prazo'
  --estrategia 'Mensal:500:2026-08-10:prestacao:mensal:2026-10-10'
"""


@app.callback()
def principal(
    ctx: typer.Context,
    log_level: str = typer.Option(
        "WARNING", "--log-level", help="DEBUG, INFO, WARNING ou ERROR."
    ),
) -> None:
    """Configura a execução comum aos comandos da CLI."""
    try:
        configurar_logging(log_level)
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro
    if ctx.invoked_subcommand is not None:
        logger.info("Executando comando: %s", ctx.invoked_subcommand)


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


def _frequencia(valor: str) -> FrequenciaAmortizacao:
    if valor not in {"unica", "mensal", "anual"}:
        raise typer.BadParameter("Use 'unica', 'mensal' ou 'anual'.")
    return cast(FrequenciaAmortizacao, valor)


def _amortizacao_programada(
    valor: str, modo: ModoAmortizacao, cenario: CenarioProjecao
) -> AmortizacaoExtraordinaria:
    try:
        data_texto, valor_texto = valor.split(":", maxsplit=1)
    except ValueError as erro:
        raise typer.BadParameter("Use AAAA-MM-DD:VALOR.") from erro
    valor_decimal = _tr_decimal(valor_texto)
    if valor_decimal is None:
        raise typer.BadParameter("O valor da amortização é obrigatório.")
    try:
        data = normalizar_data_amortizacao(_data(data_texto), cenario)
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro
    return AmortizacaoExtraordinaria(data, valor_decimal, modo)


def _criar_agenda_por_opcoes(
    valor: str | None,
    data: str | None,
    modo: ModoAmortizacao,
    frequencia: str,
    ate: str | None,
    amortizacao: list[str],
    cenario: CenarioProjecao,
) -> list[AmortizacaoExtraordinaria]:
    """Converte as opções compartilhadas da CLI em uma agenda validada."""
    if amortizacao:
        if (
            valor is not None
            or data is not None
            or ate is not None
            or frequencia != "unica"
        ):
            raise typer.BadParameter("Use apenas --amortizacao para agenda programada.")
        return [_amortizacao_programada(item, modo, cenario) for item in amortizacao]

    if valor is None:
        raise typer.BadParameter("Informe --valor ou ao menos um --amortizacao.")
    valor_decimal = _tr_decimal(valor)
    if valor_decimal is None or valor_decimal <= 0:
        raise typer.BadParameter("O valor da amortização deve ser positivo.")
    frequencia_validada = _frequencia(frequencia)
    if frequencia_validada == "unica" and ate is not None:
        raise typer.BadParameter("--ate é aceito apenas para amortizações recorrentes.")
    if frequencia_validada != "unica" and ate is None:
        raise typer.BadParameter("Informe --ate para amortizações recorrentes.")
    try:
        estrategia = EstrategiaAmortizacao(
            nome="Estratégia informada na linha de comando",
            valor=valor_decimal,
            data_inicio=_data(data) if data else cenario.data_inicio,
            modo=modo,
            frequencia=frequencia_validada,
            data_fim=_data(ate) if ate else None,
        )
        return criar_agenda_estrategia(cenario, estrategia)
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro


def _estrategia_por_texto(
    valor: str, cenario: CenarioProjecao
) -> EstrategiaAmortizacao:
    """Lê ``NOME:VALOR:DATA:MODO[:FREQUENCIA:ATE]`` para comparação."""
    partes = valor.split(":")
    if len(partes) not in {4, 6}:
        raise typer.BadParameter(
            "Use NOME:VALOR:AAAA-MM-DD:MODO[:FREQUENCIA:AAAA-MM-DD]."
        )
    nome, valor_texto, data_texto, modo_texto = partes[:4]
    frequencia = "unica" if len(partes) == 4 else partes[4]
    fim = None if len(partes) == 4 else partes[5]
    valor_decimal = _tr_decimal(valor_texto)
    if valor_decimal is None or valor_decimal <= 0:
        raise typer.BadParameter("O valor da estratégia deve ser positivo.")
    try:
        return EstrategiaAmortizacao(
            nome=nome,
            valor=valor_decimal,
            data_inicio=_data(data_texto),
            data_fim=_data(fim) if fim else None,
            modo=_modo(modo_texto),
            frequencia=_frequencia(frequencia),
        )
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro


def _estrategia_para_planejamento(
    data: str | None,
    modo: str,
    frequencia: str,
    ate: str | None,
    cenario: CenarioProjecao,
) -> EstrategiaAmortizacao:
    """Cria a estratégia cujo valor será calculado pelo planejador."""
    frequencia_validada = _frequencia(frequencia)
    if frequencia_validada != "unica" and ate is None:
        raise typer.BadParameter("Informe --ate para uma estratégia recorrente.")
    if frequencia_validada == "unica" and ate is not None:
        raise typer.BadParameter("--ate é aceito apenas para estratégias recorrentes.")
    try:
        return EstrategiaAmortizacao(
            nome="Meta de quitação",
            valor=Decimal("0.00"),
            data_inicio=_data(data) if data else cenario.data_inicio,
            data_fim=_data(ate) if ate else None,
            modo=_modo(modo),
            frequencia=frequencia_validada,
        )
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro


def _tabela(cabecalhos: tuple[str, ...], linhas: list[tuple[str, ...]]) -> str:
    """Renderiza uma tabela de terminal com colunas calculadas pelos dados."""
    larguras = [
        max(len(cabecalho), *(len(linha[indice]) for linha in linhas))
        for indice, cabecalho in enumerate(cabecalhos)
    ]
    cabecalho = " | ".join(
        texto.ljust(larguras[indice]) for indice, texto in enumerate(cabecalhos)
    )
    separador = "-+-".join("-" * largura for largura in larguras)
    dados = [
        " | ".join(
            (
                texto.ljust(larguras[indice])
                if indice == 0
                else texto.rjust(larguras[indice])
            )
            for indice, texto in enumerate(linha)
        )
        for linha in linhas
    ]
    return "\n".join([cabecalho, separador, *dados])


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


@app.command("extrair-pdf")
def extrair_pdf(
    pdf: Path = typer.Option(
        Path("extrato319405086.pdf"), "--pdf", help="Extrato PDF do Banco do Brasil."
    ),
    saida: Path = typer.Option(
        Path("extrato_extraido.csv"), "--saida", help="CSV extraído e validado."
    ),
) -> None:
    """Converte um extrato PDF para CSV validado sem alterar a fonte original."""
    try:
        caminho = converter_pdf_para_csv(pdf, saida)
        quantidade = len(ler_extrato_csv(caminho))
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro
    typer.echo(f"PDF extraído e validado: {quantidade} eventos.")
    typer.echo(f"CSV gerado em: {caminho}.")


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
    agenda = _criar_agenda_por_opcoes(
        valor, data, modo_validado, frequencia, ate, amortizacao, cenario
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
    estrategia: list[str] = typer.Option(
        [],
        "--estrategia",
        metavar="FORMATO",
        help=(
            "Repita por cenário. Use NOME:VALOR:DATA:MODO ou "
            "NOME:VALOR:DATA:MODO:FREQUENCIA:ATE. "
            "Execute com --estrategia --help para detalhes e exemplos."
        ),
    ),
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
) -> None:
    """Compara uma estratégia ou múltiplas estratégias ao cenário-base."""
    if estrategia == ["--help"]:
        typer.echo(AJUDA_ESTRATEGIA)
        return
    modo_validado = _modo(modo)
    historico = _historico(csv)
    cenario = criar_cenario_padrao(historico)
    if estrategia:
        if valor is not None or data is not None or ate is not None or amortizacao:
            raise typer.BadParameter(
                "Use apenas --estrategia para comparar múltiplos cenários."
            )
        try:
            resultados = comparar_estrategias(
                cenario,
                [_estrategia_por_texto(item, cenario) for item in estrategia],
            )
        except ValueError as erro:
            raise typer.BadParameter(str(erro)) from erro
        typer.echo("COMPARAÇÃO DE ESTRATÉGIAS")
        typer.echo(
            _tabela(
                (
                    "Estratégia",
                    "Aporte total",
                    "Juros economizados",
                    "Desembolso futuro",
                    "Quitação",
                    "Prazo abatido",
                    "Próxima prestação",
                    "Saldo",
                ),
                [
                    (
                        resultado.estrategia.nome,
                        f"R$ {resultado.aporte_total:.2f}",
                        f"R$ {resultado.juros_economizados:.2f}",
                        f"R$ {resultado.desembolso_futuro:.2f}",
                        f"{resultado.data_quitacao:%d/%m/%Y}",
                        f"{resultado.meses_abatidos} meses",
                        f"R$ {resultado.proxima_prestacao:.2f}",
                        f"R$ {resultado.saldo_devedor:.2f}",
                    )
                    for resultado in resultados
                ],
            )
        )
        return
    agenda = _criar_agenda_por_opcoes(
        valor, data, modo_validado, frequencia, ate, amortizacao, cenario
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


@app.command()
def planejar(
    meta_quitacao: str | None = typer.Option(
        None, "--meta-quitacao", help="Data máxima de quitação AAAA-MM-DD."
    ),
    meta_prestacao: str | None = typer.Option(
        None, "--meta-prestacao", help="Valor máximo da prestação."
    ),
    data: str | None = typer.Option(None, "--data", help="Início dos aportes."),
    modo: str = typer.Option("prazo", "--modo"),
    frequencia: str = typer.Option("unica", "--frequencia"),
    ate: str | None = typer.Option(None, "--ate", help="Fim da recorrência."),
    csv: Path = typer.Option(Path("extrato.csv"), "--csv"),
) -> None:
    """Encontra o menor aporte para atingir uma meta de quitação ou prestação."""
    if (meta_quitacao is None) == (meta_prestacao is None):
        raise typer.BadParameter(
            "Informe exatamente uma meta: --meta-quitacao ou --meta-prestacao."
        )
    historico = _historico(csv)
    cenario = criar_cenario_padrao(historico)
    frequencia_validada = _frequencia(frequencia)
    data_final_aportes = ate
    if meta_quitacao is not None and ate is None and frequencia_validada != "unica":
        data_final_aportes = meta_quitacao
    try:
        estrategia = _estrategia_para_planejamento(
            data, modo, frequencia, data_final_aportes, cenario
        )
        if meta_quitacao is not None:
            data_meta = _data(meta_quitacao)
            resultado_quitacao = encontrar_aporte_minimo_quitacao(
                cenario, MetaQuitacao(data_meta), estrategia
            )
        else:
            valor_meta = _tr_decimal(meta_prestacao)
            if valor_meta is None:
                raise typer.BadParameter("O valor da meta de prestação é obrigatório.")
            resultado_prestacao = encontrar_aporte_minimo_prestacao(
                cenario, MetaPrestacao(valor_meta), estrategia
            )
    except ValueError as erro:
        raise typer.BadParameter(str(erro)) from erro
    if meta_quitacao is not None:
        typer.echo("PLANEJAMENTO — META DE QUITAÇÃO")
        typer.echo(f"Meta de quitação: {data_meta:%d/%m/%Y}.")
        if resultado_quitacao.meta_ja_cumprida:
            typer.echo("O cenário-base já atende à meta; aporte necessário: R$ 0.00.")
        else:
            typer.echo(
                f"Aporte mínimo por ocorrência: R$ {resultado_quitacao.valor_minimo:.2f}."
            )
            typer.echo(f"Frequência: {resultado_quitacao.estrategia.frequencia}.")
        typer.echo(f"Quitação obtida: {resultado_quitacao.data_quitacao:%d/%m/%Y}.")
        return

    typer.echo("PLANEJAMENTO — META DE PRESTAÇÃO")
    typer.echo(f"Meta de prestação: R$ {valor_meta:.2f}.")
    if resultado_prestacao.meta_ja_cumprida:
        typer.echo("O cenário-base já atende à meta; aporte necessário: R$ 0.00.")
    else:
        typer.echo(
            f"Aporte mínimo por ocorrência: R$ {resultado_prestacao.valor_minimo:.2f}."
        )
        typer.echo(f"Frequência: {resultado_prestacao.estrategia.frequencia}.")
    base = resultado_prestacao.prestacao_base
    obtida = resultado_prestacao.prestacao_obtida
    data_avaliada = obtida.data or base.data
    if data_avaliada is None:
        typer.echo("Não haverá prestação posterior: o contrato estará quitado.")
    else:
        typer.echo(f"Prestação avaliada: {data_avaliada:%d/%m/%Y}.")
    typer.echo(f"Prestação sem amortização: R$ {base.valor:.2f}.")
    typer.echo(f"Prestação obtida: R$ {obtida.valor:.2f}.")


if __name__ == "__main__":
    app()
