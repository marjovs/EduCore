# Pendências técnicas

**Atualizado em:** 10/11/2026

## ✅ Resolvidas

| Pendência | O que foi feito |
|---|---|
| 19 páginas fora do `base.html` | Todas as páginas estendem o `base.html`, que tem o cabeçalho (cor da área, tema, e-mail, "Minha senha" e "Sair"). O `<head>`, o Tailwind e o tema estão num lugar só. |
| Bloco de mensagens repetido em 16 templates | Um só `_mensagens.html`: mensagens com "sucesso" em verde, as demais em vermelho. |
| Telas de notas e frequência duplicadas | `consultas/notas.html` e `consultas/frequencia.html` servem a secretaria e a coordenação (muda só a cor). As rotas usam `app/routes/consultas.py`. |
| Tratamento de erro repetido nas rotas | `app/routes/acoes.py` (`executar`) faz rollback, registra o erro e mostra a mensagem. `_consulta_filtrada` e `_opcoes_de_filtro` não estão mais duplicadas. |
| CSS/JS sem uso, avisos de formatação | `style.css` e `main.js` removidos; `pyflakes` e `pycodestyle` sem avisos. |
| Flask-Migrate | Migrações em `backend/migrations/`. O Neon foi marcado na versão inicial (`4aca4c82fab5`). Veja "Criação das tabelas" no README. |
| Tela de usuários e troca de senha | Coordenação → **Usuários** (cadastrar, redefinir senha, excluir); todos → **Minha senha**. |
| Tailwind local | `frontend/static/css/tailwind.css` gerado por `npm run css`; o CDN saiu. |
| Testes com `pytest` | `backend/tests/` (79 testes, SQLite temporário): `cd backend && python -m pytest`. |
| README e relatório | Atualizados. |

## Ainda em aberto (não atrapalham o uso)

- **Formulários de aluno, curso e turma não mantêm o que foi digitado quando dá erro**: a pessoa precisa preencher de novo. O cadastro de matrícula e o de usuário já mantêm.
- **Usuários são excluídos, não desativados.** Para desativar sem apagar, seria preciso uma coluna nova (`ativo`) com uma migração no Neon.
- **Cada página confere no banco se o usuário ainda existe** (para que excluir um usuário corte o acesso na hora). É uma consulta pequena por página; se o sistema ficar lento no Neon, dá para trocar por uma verificação menos frequente.
- **Os 2 alunos de teste do Neon têm CPFs fictícios.** Ao editar um deles, será preciso informar um CPF válido.
