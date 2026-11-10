from flask import request

from app.validacao import inteiro_seguro


def ler_filtros():
    """Filtros comuns das listagens: ?busca=&turma_id=&ano=&pagina=

    Números inválidos ou gigantes são ignorados (em vez de causar erro 500).
    """
    return {
        "busca": request.args.get("busca", "").strip()[:100],
        "turma_id": inteiro_seguro(request.args.get("turma_id")),
        "ano": inteiro_seguro(request.args.get("ano")),
        "pagina": inteiro_seguro(request.args.get("pagina")) or 1,
    }
