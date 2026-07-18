"""Modelo imutável de um evento financeiro registrado no extrato."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EventoHistorico:
    """Representa um evento conforme os valores reportados pelo Banco do Brasil.

    O evento não pressupõe que cada linha seja uma parcela mensal PRICE. Eventos
    de encargos, períodos de carência e ajustes também podem estar presentes.
    """

    data: date
    saldo_devedor: Decimal
    correcao_monetaria: Decimal
    saldo_atualizado: Decimal
    prestacao: Decimal
    capital: Decimal
    juros: Decimal
    acessorios: Decimal
    correcao_prestacao: Decimal
    encargos: Decimal
    valor_pago: Decimal

    @property
    def tr_historica(self) -> Decimal | None:
        """Retorna a TR observada, ou ``None`` quando o saldo é zero."""
        if self.saldo_devedor == 0:
            return None
        return self.correcao_monetaria / self.saldo_devedor

    @property
    def amortizacao_reportada(self) -> Decimal:
        """Retorna o capital informado no extrato como amortização histórica."""
        return self.capital

    @property
    def componentes_conhecidos_prestacao(self) -> Decimal:
        """Soma os componentes cuja participação no pagamento é explícita."""
        return self.capital + self.juros + self.acessorios + self.encargos

    @property
    def residuo_prestacao(self) -> Decimal:
        """Retorna a parte da prestação não explicada pelos componentes conhecidos."""
        return self.prestacao - self.componentes_conhecidos_prestacao

    @property
    def saldo_teorico_sem_ajustes(self) -> Decimal:
        """Calcula o saldo sob a hipótese simplificada de correção e capital.

        Este valor é diagnóstico: não substitui o saldo atualizado reportado,
        pois o extrato pode conter liberações, carência ou outros ajustes.
        """
        return self.saldo_devedor + self.correcao_monetaria - self.capital

    @property
    def ajuste_saldo_nao_classificado(self) -> Decimal:
        """Quantifica a diferença entre o saldo reportado e o modelo simplificado."""
        return self.saldo_atualizado - self.saldo_teorico_sem_ajustes
