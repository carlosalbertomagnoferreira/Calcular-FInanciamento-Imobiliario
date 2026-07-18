"""Interface de linha de comando do simulador."""

from decimal import Decimal, InvalidOperation
from pathlib import Path

import typer

from simulador import (
    criar_cenario_padrao,
    gerar_resumo_financeiro,
    identificar_parcelas_validas,
    ler_extrato_csv,
    projetar_contrato,
    reconstruir_historico,
    renderizar_relatorio_markdown,
    renderizar_relatorio_txt,
)

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
    typer.echo(f"Próxima prestação: R$ {primeira['Prestação']:.2f}.")


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


if __name__ == "__main__":
    app()
