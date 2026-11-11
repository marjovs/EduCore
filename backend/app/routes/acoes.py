from flask import current_app, flash
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.services import RegraNegocioError


def executar(acao, mensagem_erro, ao_falhar):
    """Executa uma gravação e trata os erros do jeito padrão do EduCore.

    - RegraNegocioError: desfaz a transação e mostra a mensagem da regra.
    - Erro do banco: desfaz a transação, registra o erro no log e mostra
      `mensagem_erro`.

    Retorna None se deu certo; se falhou, retorna a resposta de `ao_falhar()`.

    Uso:
        falha = executar(lambda: servico.salvar(dados), "Erro ao salvar.", tela)
        if falha:
            return falha
    """
    try:
        acao()
    except RegraNegocioError as erro:
        db.session.rollback()
        flash(str(erro))
        return ao_falhar()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(mensagem_erro)
        flash(mensagem_erro)
        return ao_falhar()
    return None
