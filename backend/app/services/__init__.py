from flask import abort

from app.validacao import MAIOR_INTEIRO


class RegraNegocioError(ValueError):
    """Erro de validação de regra de negócio, com mensagem para o usuário."""


def obter_ou_404(modelo, registro_id):
    """db.get_or_404 que também responde 404 para IDs fora do limite do banco
    (ex.: /editar/99999999999999999999), em vez de erro 500."""
    from app import db

    if not isinstance(registro_id, int) or not 0 < registro_id <= MAIOR_INTEIRO:
        abort(404)

    return db.get_or_404(modelo, registro_id)
