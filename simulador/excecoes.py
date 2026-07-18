"""Exceções específicas para a importação do extrato."""


class ExtratoCSVError(ValueError):
    """Erro base para problemas encontrados em um extrato CSV."""


class ArquivoExtratoNaoEncontradoError(ExtratoCSVError):
    """O arquivo informado para leitura não existe."""


class LeituraCSVError(ExtratoCSVError):
    """O conteúdo do arquivo não pôde ser interpretado como CSV."""


class ColunasObrigatoriasAusentesError(ExtratoCSVError):
    """O CSV não contém todas as colunas exigidas pelo contrato de entrada."""


class CampoObrigatorioVazioError(ExtratoCSVError):
    """Uma coluna obrigatória contém valor vazio."""


class DataInvalidaError(ExtratoCSVError):
    """Uma data não segue o formato brasileiro DD/MM/AAAA."""


class ValorInvalidoError(ExtratoCSVError):
    """Um valor monetário é inválido ou não pode ser negativo."""


class RegistroDuplicadoError(ExtratoCSVError):
    """O CSV possui registros completamente duplicados."""
