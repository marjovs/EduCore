# Pendências técnicas (para ler com calma)

**Data:** 10/11/2026

Nada aqui é um erro: o sistema funciona normalmente com tudo isso no lugar.
São pontos que deixam o código mais trabalhoso de manter e que valem ser
resolvidos quando houver tempo, de preferência **antes** de criar telas novas.

Os erros que atrapalhavam o uso (CPF duplicado, validações, exclusão de aluno,
erro 500 com números gigantes na URL, turma duplicada e textos cortados) **já
foram corrigidos**.

---

## 1. Páginas que não usam o `base.html` (prioridade: média)

**O que é:** 19 páginas repetem o HTML inteiro (`<head>`, Tailwind, tema
claro/escuro) em vez de herdar do `base.html`:

- `auth/login.html`
- `instrutor/frequencias/listar.html`, `instrutor/frequencias/registrar.html`
- `instrutor/notas/listar.html`, `instrutor/notas/registrar.html`
- `secretaria/painel.html`
- `secretaria/alunos/` (cadastrar, editar, listar)
- `secretaria/cursos/` (cadastrar, editar, listar)
- `secretaria/turmas/` (cadastrar, editar, listar)
- `secretaria/matriculas/` (cadastrar, listar)
- `secretaria/notas/listar.html`, `secretaria/frequencias/listar.html`

**Por que importa:** qualquer coisa que precise estar em todas as páginas
tem que ser colada 19 vezes. Foi exatamente por isso que o modo escuro, na
primeira versão, só funcionava em 7 páginas. Hoje cada uma dessas páginas tem
estas linhas para o tema funcionar:

```jinja
{% include "_tema.html" %}                {# no <head> #}
{% import "_botao_tema.html" as tema %}   {# antes de </body> #}
{{ tema.flutuante() }}
```

**Como resolver:**

1. Fazer o `base.html` aceitar a cor da área (azul para a secretaria e o
   instrutor, roxo para a coordenação) e um título por página, por exemplo
   com `{% block titulo %}`.
2. Trocar o topo de cada página por `{% extends "base.html" %}` e deixar só o
   conteúdo dentro de `{% block content %}`.
3. O login pode ganhar um `base_login.html` próprio, sem cabeçalho.

Dá para fazer uma área de cada vez (instrutor, depois secretaria), testando
no navegador a cada passo.

## 2. Bloco de mensagens repetido (prioridade: baixa)

O bloco que mostra as mensagens (`get_flashed_messages`) está copiado em
16 templates, cada um com uma cor um pouco diferente. Quando o item 1 for
feito, ele pode ir para o `base.html` ou para um `_mensagens.html` incluído
uma vez só.

## 3. Telas de notas e frequência quase iguais (prioridade: baixa)

Secretaria e coordenação têm telas praticamente idênticas, mudando só a cor:

| Secretaria | Coordenação |
|---|---|
| `secretaria/notas/listar.html` | `coordenacao/desempenho.html` |
| `secretaria/frequencias/listar.html` | `coordenacao/frequencia.html` |

Uma mudança numa delas (por exemplo, uma coluna nova) precisa ser repetida
na outra. Daria para ter um template só para cada uma, recebendo a cor como
parâmetro, como já foi feito com `_filtros.html` e `_paginacao.html`.

O mesmo vale, em menor grau, para `instrutor/notas/listar.html` e
`instrutor/frequencias/listar.html`, que são a mesma lista de turmas com
outro botão.

## 4. Blocos de erro repetidos nas rotas (prioridade: baixa)

As rotas de cadastro, edição e exclusão repetem o mesmo tratamento de erro
(13 `except SQLAlchemyError` e 10 `except RegraNegocioError`):

```python
try:
    servico.salvar(...)
except RegraNegocioError as e:
    db.session.rollback()
    flash(str(e))
    return tela()
except SQLAlchemyError:
    db.session.rollback()
    current_app.logger.exception("Erro ao ...")
    flash("Erro ao ...")
    return tela()
```

Isso poderia virar uma função auxiliar (por exemplo `executar(acao,
mensagem_erro)`) em `app/routes/`. Não tem pressa, porque o código repetido
está correto.

No mesmo espírito:

- `_consulta_filtrada` está igual em `nota_service.py` e `frequencia_service.py`.
- `_opcoes_de_filtro` está igual em `secretaria_routes.py` e `coordenacao_routes.py`.

## 5. Pequenas limpezas

- `frontend/static/css/style.css` e `frontend/static/js/main.js` não são
  usados por nenhuma página. Podem ser apagados.
- O `README.md` não fala do modo escuro, da busca e da paginação. Também vale
  marcar no Roadmap o que já foi feito, e o `relatorio.md` está desatualizado.
- O `pycodestyle` aponta 7 avisos de formatação (linhas em branco) em
  `models/curso.py`, `models/matricula.py` e `models/turma.py`.
- Continuam pendentes do relatório anterior: Flask-Migrate para versionar o
  banco, uma tela para cadastrar usuários e trocar senhas, gerar o CSS do
  Tailwind localmente (hoje ele vem de um CDN) e testes automatizados com
  `pytest`.

## Observação sobre os dados de teste do Neon

Os 2 alunos cadastrados hoje têm CPFs fictícios (`111.222.333-00` e
`123.123.123-00`). Desde a correção de validação, o sistema confere os
dígitos verificadores do CPF. Por isso, ao **editar** um desses alunos, será
preciso informar um CPF válido. A listagem e as consultas continuam
funcionando normalmente.
