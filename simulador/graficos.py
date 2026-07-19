"""Gráficos derivados do histórico reconstruído e da projeção do contrato."""

from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from simulador.parcelas import COLUNA_PARCELA_VALIDA

NOMES_GRAFICOS = {
    "saldo_devedor": "saldo_devedor.png",
    "prestacao": "prestacao.png",
    "tr": "tr.png",
    "juros": "juros.png",
    "amortizacao": "amortizacao.png",
    "evolucao_contrato": "evolucao_contrato.png",
}


def criar_graficos(
    historico: pd.DataFrame, projecao: pd.DataFrame
) -> dict[str, Figure]:
    """Cria os gráficos de saldo, componentes financeiros e evolução contratual."""
    historico_valido = historico.loc[historico[COLUNA_PARCELA_VALIDA]].sort_values(
        "Data"
    )
    if historico_valido.empty or projecao.empty:
        raise ValueError(
            "Histórico válido e projeção são obrigatórios para os gráficos."
        )

    return {
        "saldo_devedor": _grafico_series(
            historico_valido,
            projecao,
            "Saldo Atualizado",
            "Saldo Final",
            "Saldo devedor",
            "R$",
        ),
        "prestacao": _grafico_series(
            historico_valido,
            projecao,
            "Prestação",
            "Prestação",
            "Prestação mensal",
            "R$",
        ),
        "tr": _grafico_series(
            historico_valido,
            projecao,
            "TR Histórica",
            "TR Projetada",
            "TR mensal",
            "%",
            conversor=lambda valores: valores * 100,
        ),
        "juros": _grafico_series(
            historico_valido,
            projecao,
            "Juros",
            "Juros",
            "Juros mensais",
            "R$",
        ),
        "amortizacao": _grafico_series(
            historico_valido,
            projecao,
            "Capital",
            "Amortização",
            "Amortização mensal",
            "R$",
        ),
        "evolucao_contrato": _grafico_evolucao(historico_valido, projecao),
    }


def exportar_graficos(
    graficos: dict[str, Figure], diretorio: str | Path
) -> dict[str, Path]:
    """Salva os gráficos em PNG no diretório indicado."""
    destino = Path(diretorio)
    destino.mkdir(parents=True, exist_ok=True)
    arquivos: dict[str, Path] = {}
    for nome, figura in graficos.items():
        caminho = destino / NOMES_GRAFICOS[nome]
        figura.savefig(caminho, dpi=150, bbox_inches="tight")
        plt.close(figura)
        arquivos[nome] = caminho
    return arquivos


def _grafico_series(
    historico: pd.DataFrame,
    projecao: pd.DataFrame,
    coluna_historico: str,
    coluna_projecao: str,
    titulo: str,
    unidade: str,
    conversor: Callable[[pd.Series], pd.Series] | None = None,
) -> Figure:
    figura, eixo = plt.subplots(figsize=(11, 5))
    valores_historicos = _numeros(historico[coluna_historico])
    valores_projetados = _numeros(projecao[coluna_projecao])
    if conversor is not None:
        valores_historicos = conversor(valores_historicos)
        valores_projetados = conversor(valores_projetados)
    eixo.plot(historico["Data"], valores_historicos, label="Histórico", color="#1f77b4")
    eixo.plot(projecao["Data"], valores_projetados, label="Projeção", color="#ff7f0e")
    _configurar_eixo(eixo, titulo, unidade)
    return figura


def _grafico_evolucao(historico: pd.DataFrame, projecao: pd.DataFrame) -> Figure:
    """Combina saldo e prestação para evidenciar a evolução do contrato."""
    figura, eixo_saldo = plt.subplots(figsize=(11, 5))
    eixo_prestacao = eixo_saldo.twinx()
    eixo_saldo.plot(
        historico["Data"],
        _numeros(historico["Saldo Atualizado"]),
        color="#1f77b4",
        label="Saldo histórico",
    )
    eixo_saldo.plot(
        projecao["Data"],
        _numeros(projecao["Saldo Final"]),
        color="#ff7f0e",
        label="Saldo projetado",
    )
    eixo_prestacao.plot(
        historico["Data"],
        _numeros(historico["Prestação"]),
        color="#2ca02c",
        alpha=0.65,
        label="Prestação histórica",
    )
    eixo_prestacao.plot(
        projecao["Data"],
        _numeros(projecao["Prestação"]),
        color="#d62728",
        alpha=0.65,
        label="Prestação projetada",
    )
    eixo_saldo.set_title("Evolução do contrato")
    eixo_saldo.set_xlabel("Data")
    eixo_saldo.set_ylabel("Saldo devedor (R$)")
    eixo_prestacao.set_ylabel("Prestação (R$)")
    eixo_saldo.grid(alpha=0.25)
    linhas, rotulos = eixo_saldo.get_legend_handles_labels()
    linhas_prestacao, rotulos_prestacao = eixo_prestacao.get_legend_handles_labels()
    eixo_saldo.legend(linhas + linhas_prestacao, rotulos + rotulos_prestacao)
    figura.tight_layout()
    return figura


def _configurar_eixo(eixo: plt.Axes, titulo: str, unidade: str) -> None:
    eixo.set_title(titulo)
    eixo.set_xlabel("Data")
    eixo.set_ylabel(unidade)
    eixo.grid(alpha=0.25)
    eixo.legend()
    plt.tight_layout()


def _numeros(valores: pd.Series) -> pd.Series:
    return pd.to_numeric(valores, errors="coerce")
