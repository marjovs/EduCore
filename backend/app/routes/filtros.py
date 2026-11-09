from flask import request


def _inteiro(nome):
    """Lê um número opcional da query string; valores inválidos são ignorados."""
    valor = request.args.get(nome, "").strip()
    return int(valor) if valor.isdigit() else None


def ler_filtros():
    """Filtros comuns das listagens: ?busca=&turma_id=&ano=&pagina="""
    return {
        "busca": request.args.get("busca", "").strip()[:100],
        "turma_id": _inteiro("turma_id"),
        "ano": _inteiro("ano"),
        "pagina": _inteiro("pagina") or 1,
    }
