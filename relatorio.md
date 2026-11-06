# Relatório de Análise — EduCore

**Data:** 06/11/2026
**Escopo:** varredura completa de `backend/` (Python/Flask) e `frontend/` (templates Jinja), análise de erros e viabilidade de migração para **Neon** (PostgreSQL em nuvem).

> ### ✅ Atualização — erros críticos corrigidos (06/11/2026)
> Os itens **2.1 a 2.4** já foram corrigidos:
> - Templates renomeados: `secretaria/aluno/` → `secretaria/alunos/`, `notas/resgistrar.html` → `notas/registrar.html`, `coordenacao/aluno.html` → `coordenacao/alunos.html`, `coordenacao/matricula.html` → `coordenacao/matriculas.html`; em `frequencia_routes.py` o caminho passou a ser `instrutor/frequencias/`.
> - `frequencia_service.py` reescrito com `listar_frequencias`, `buscar_frequencia_por_data`, `registrar_frequencia`, `atualizar_frequencia`, `buscar_frequencia` e `excluir_frequencia`. A rota agora busca a frequência existente com uma consulta filtrada em vez de carregar todas as frequências dentro do loop.
> - `coordenacao/alunos.html` passou a listar os alunos (com a contagem de matrículas ativas).
>
> Reteste com os 3 perfis: **20/20 verificações OK**. Todas as rotas abrem, a frequência é gravada, e lançar de novo no mesmo dia atualiza o registro em vez de duplicar.
> As seções 3 a 5 (segurança, lógica e limpeza) **continuam pendentes**, exceto os itens 3.1, 3.2 e 3.5, resolvidos na migração abaixo.

> ### ✅ Atualização — código preparado para o Neon (06/11/2026)
> - `config.py` lê `SECRET_KEY` e `DATABASE_URL` do `backend/.env`, converte automaticamente `postgresql://` → `postgresql+psycopg://` e usa `pool_pre_ping`/`pool_recycle` (por causa da suspensão automática do Neon). Se faltar alguma variável, o app para com uma mensagem clara.
> - `requirements.txt` regravado em UTF‑8: entrou `psycopg[binary]==3.3.8`; saíram `PyMySQL` e `mysql-connector-python`.
> - `backend/.env` criado (ignorado pelo Git) com uma `SECRET_KEY` aleatória; `backend/.env.example` documenta as variáveis.
> - `run.py`: o modo debug só liga com `FLASK_DEBUG=1`.
> - `database/educore_postgres.sql`: schema em sintaxe PostgreSQL, para referência. O `educore.sql` (MySQL) ficou obsoleto.
> - **Migração de dados não é necessária**: o MySQL local tinha 0 registros em todas as tabelas.
>
> ### ✅ Atualização — conectado ao Neon (06/11/2026)
> - `DATABASE_URL` configurada no `backend/.env` (endpoint pooled em `sa-east-1`, PostgreSQL 18).
> - As 6 tabelas foram criadas pelo `create_all()`. A escrita foi validada com um insert que depois foi desfeito, e as tabelas continuam vazias.
> - As 13 páginas dos 3 perfis responderam 200. Cada página que consulta o banco leva cerca de 220–260 ms por causa da ida e volta até o Neon. Corrigir as consultas N×M do item 4.4 passa a ser mais importante.
> - ⚠️ A senha do banco foi colada no chat. Recomenda-se trocá-la em *Neon > Roles > Reset password* e atualizar o `.env`.
> - A skill do Neon (`npx neon skills -y`) não foi instalada: ela exige Node.js ≥ 22.20.0 e a máquina tem o 22.14.0.

---

## 1. Como a análise foi feita

| Etapa | O que foi feito |
|---|---|
| Leitura | Todos os 30 arquivos Python, o `educore.sql`, `requirements.txt` e os 26 templates HTML. |
| Análise estática | `pyflakes` em todo o backend. |
| Execução real | Ambiente virtual isolado com o `requirements.txt` do projeto; app executado com banco **SQLite em memória** (sem tocar no MySQL local), simulando login dos 3 perfis e chamando todas as rotas via `test_client` do Flask. |
| Compatibilidade Neon | Os models foram compilados para DDL do dialeto PostgreSQL para validar a portabilidade. |

### Resumo do resultado

| Gravidade | Qtd. | Exemplo |
|---|---|---|
| 🔴 Crítico (quebra a funcionalidade) | 7 | 8 rotas retornam **erro 500** (`TemplateNotFound`); registro de frequência **nunca funciona** |
| 🟠 Alto (segurança) | 5 | `SECRET_KEY` fixa no código permite forjar login; senhas em texto puro |
| 🟡 Médio (lógica/qualidade) | 9 | Notas duplicadas; API legada do SQLAlchemy; consultas ineficientes |
| ⚪ Baixo (limpeza) | 5 | imports não usados, `requirements.txt` em UTF‑16 |

Resultado da execução das rotas (antes de qualquer correção):

```
SECRETARIA
GET  /secretaria/alunos/                 -> TemplateNotFound: secretaria/alunos/listar.html
GET  /secretaria/alunos/cadastrar        -> TemplateNotFound: secretaria/alunos/cadastrar.html
INSTRUTOR
GET  /instrutor/frequencia/              -> TemplateNotFound: instrutor/frequencia/listar.html
GET  /instrutor/frequencia/registrar/1   -> TemplateNotFound: instrutor/frequencia/registrar.html
POST /instrutor/frequencia/registrar/1   -> TemplateNotFound (e, por trás disso, AttributeError)
GET  /instrutor/notas/registrar/1        -> TemplateNotFound: instrutor/notas/registrar.html
COORDENAÇÃO
GET  /coordenacao/alunos                 -> TemplateNotFound: coordenacao/alunos.html
GET  /coordenacao/matriculas             -> TemplateNotFound: coordenacao/matriculas.html
```

Todas as outras rotas (painéis, cursos, turmas, matrículas da secretaria, listagem de notas, desempenho e frequência da coordenação) responderam corretamente (200/302).

---

## 2. Erros críticos 🔴

### 2.1 `frequencia_service.py` é uma cópia de `matricula_service.py`
**Arquivo:** [backend/app/services/frequencia_service.py](backend/app/services/frequencia_service.py)

O arquivo contém exatamente o mesmo código do serviço de matrículas (`listar_matriculas`, `cadastrar_matricula`, …). Porém a rota de frequência chama funções que **não existem**:

| Chamada em [frequencia_routes.py](backend/app/routes/frequencia_routes.py) | Existe? |
|---|---|
| `frequencia_service.listar_frequencias()` (linha 102) | ❌ |
| `frequencia_service.atualizar_frequencia(...)` (linha 110) | ❌ |
| `frequencia_service.registrar_frequencia(...)` (linha 115) | ❌ |

**Efeito:** gera `AttributeError`, que é capturado pelo `except Exception` da linha 117. O usuário vê sempre a mensagem *"Erro ao registrar frequências."* e **nenhuma frequência é gravada**. Confirmado na execução:

```
funcoes em frequencia_service: ['Matricula', 'atualizar_matricula', 'buscar_matricula',
                                'cadastrar_matricula', 'cancelar_matricula', 'db', 'listar_matriculas']
flash: [('message', 'Erro ao registrar frequências.')]
```

**Correção sugerida:**
```python
from app import db
from app.models.frequencia import Frequencia

def listar_frequencias():
    return Frequencia.query.order_by(Frequencia.data.desc()).all()

def buscar_frequencia_por_data(matricula_id, data):
    return Frequencia.query.filter_by(matricula_id=matricula_id, data=data).first()

def registrar_frequencia(dados):
    frequencia = Frequencia(
        matricula_id=dados["matricula_id"],
        data=dados["data"],
        status=dados["status"],
        observacao=dados.get("observacao"),
    )
    db.session.add(frequencia)
    db.session.commit()
    return frequencia

def atualizar_frequencia(frequencia, dados):
    frequencia.status = dados["status"]
    db.session.commit()
    return frequencia
```

> Observação: o `except Exception` genérico em todas as rotas esconde erros de programação como este. Recomenda-se capturar `sqlalchemy.exc.IntegrityError`/`SQLAlchemyError` e registrar o erro com `app.logger.exception(...)`.

### 2.2 Nomes de templates não batem com os arquivos (8 rotas com erro 500)

| Rota renderiza | Arquivo que existe | Onde corrigir |
|---|---|---|
| `secretaria/alunos/listar.html` | `secretaria/aluno/listar.html` | [aluno_routes.py:25](backend/app/routes/aluno_routes.py:25) |
| `secretaria/alunos/cadastrar.html` | `secretaria/aluno/cadastrar.html` | [aluno_routes.py:44](backend/app/routes/aluno_routes.py:44) (+ linhas 52, 68, 73) |
| `secretaria/alunos/editar.html` | `secretaria/aluno/editar.html` | [aluno_routes.py:93](backend/app/routes/aluno_routes.py:93) (+ 104, 123, 131) |
| `instrutor/frequencia/listar.html` | `instrutor/frequencias/listar.html` | [frequencia_routes.py:38](backend/app/routes/frequencia_routes.py:38) |
| `instrutor/frequencia/registrar.html` | `instrutor/frequencias/registrar.html` | [frequencia_routes.py:71](backend/app/routes/frequencia_routes.py:71) (+ 85, 121, 131) |
| `instrutor/notas/registrar.html` | `instrutor/notas/`**`resgistrar`**`.html` (erro de digitação) | renomear o arquivo para `registrar.html` |
| `coordenacao/alunos.html` | `coordenacao/aluno.html` | [coordenacao_routes.py:50](backend/app/routes/coordenacao_routes.py:50) |
| `coordenacao/matriculas.html` | `coordenacao/matricula.html` | [coordenacao_routes.py:66](backend/app/routes/coordenacao_routes.py:66) |

**Solução mais simples:** renomear as **pastas/arquivos** para o plural usado no código (`secretaria/alunos/`, `instrutor/frequencia/` ou ajustar o código), e corrigir `resgistrar.html` → `registrar.html`. Escolha uma convenção (singular ou plural) e aplique em todo o projeto.

### 2.3 `coordenacao/aluno.html` tem o conteúdo errado
Mesmo após corrigir o nome, o template [coordenacao/aluno.html](frontend/templates/coordenacao/aluno.html) é uma **cópia do painel** (usa `total_alunos`, `total_matriculas`…), mas a rota envia apenas a variável `alunos`. A página renderizaria cartões vazios e não listaria os alunos. É preciso criar uma tabela que percorra `{% for aluno in alunos %}`.

### 2.4 Lançamento de notas: cadastro funciona “às cegas”
Como `GET /instrutor/notas/registrar/<id>` dá erro 500 (item 2.2), o instrutor não consegue abrir o formulário. O POST em si funciona (confirmado), mas é inalcançável pela interface.

---

## 3. Segurança 🟠

| # | Problema | Local | Risco | Correção |
|---|---|---|---|---|
| 3.1 | `SECRET_KEY = "educore_secret_key"` fixa no código | [config.py:2](backend/config.py:2) | Quem lê o repositório pode **assinar um cookie de sessão** com `perfil="secretaria"` (ou `coordenacao`) e entrar sem senha. | Ler de variável de ambiente (`os.environ["SECRET_KEY"]`) via `.env` (o `python-dotenv` já está no `requirements.txt`, mas não é usado). |
| 3.2 | Usuário e senha do banco no código (`root:root`) | [config.py:4](backend/config.py:4) | Credencial vaza no Git; com Neon, a URL contém a senha do banco em nuvem. | `DATABASE_URL` no `.env` (já ignorado pelo `.gitignore`). |
| 3.3 | Usuários e senhas em texto puro num dicionário | [auth_routes.py:6-19](backend/app/routes/auth_routes.py:6) | Senhas fracas (`012345`…) e visíveis no código; impossível cadastrar/trocar usuário. | Criar model `Usuario` com hash (`werkzeug.security.generate_password_hash` / `check_password_hash`). |
| 3.4 | Sem proteção CSRF nos formulários POST (excluir aluno/curso/turma, cancelar matrícula) | templates `listar.html` | Um site externo pode disparar exclusões em nome do usuário logado. | `Flask-WTF` com `CSRFProtect`. |
| 3.5 | `app.run(debug=True)` fixo | [run.py:9](backend/run.py:9) | Debugger do Werkzeug permite executar código remoto se exposto em rede. | `debug=os.getenv("FLASK_DEBUG") == "1"`. |

Ponto relacionado: em [auth_routes.py:53](backend/app/routes/auth_routes.py:53) `url_for(f"{perfil}.painel")` gera `BuildError` (erro 500) se a sessão tiver um perfil inesperado — testado: `Could not build url for endpoint 'hacker.painel'`. Com a `SECRET_KEY` vazada isso é explorável; vale validar o perfil contra uma lista.

---

## 4. Erros de lógica e qualidade 🟡

| # | Problema | Local | Detalhe |
|---|---|---|---|
| 4.1 | Notas duplicadas | [nota_routes.py:118-120](backend/app/routes/nota_routes.py:118) | Enviar a mesma avaliação "P1" duas vezes cria 2 registros por aluno (confirmado: `notas apos 2 envios: 2`). Verificar se já existe nota da mesma avaliação/matrícula ou criar `UniqueConstraint(matricula_id, avaliacao)`. |
| 4.2 | Frequência sem restrição única | [models/frequencia.py](backend/app/models/frequencia.py) | Faltaria `UniqueConstraint("matricula_id", "data")` para garantir 1 registro por aluno/dia. |
| 4.3 | Commit por item em loop | [frequencia_routes.py:98-115](backend/app/routes/frequencia_routes.py:98), [nota_routes.py:119](backend/app/routes/nota_routes.py:119) | Cada serviço faz `commit()`; se falhar no 3º aluno, os 2 primeiros já foram gravados e o `rollback()` não os desfaz. Fazer um único commit ao final. |
| 4.4 | Consultas ineficientes (N×M) | [frequencia_routes.py:102](backend/app/routes/frequencia_routes.py:102), [nota_routes.py:52](backend/app/routes/nota_routes.py:52), [matricula_routes.py:92](backend/app/routes/matricula_routes.py:92) | Carrega **todas** as matrículas/frequências e filtra em Python, e `listar_frequencias()` é chamado dentro do loop. Num banco em nuvem (latência de rede) isso fica bem mais lento. Usar `filter_by(turma_id=..., status="Ativa")`. |
| 4.5 | API legada do SQLAlchemy | todos os `services/*.py` (`Query.get_or_404`) | Gera `LegacyAPIWarning` a cada chamada (observado 10× no teste). Usar `db.get_or_404(Aluno, aluno_id)`. |
| 4.6 | Verificação de perfil inconsistente | [aluno_routes.py:10](backend/app/routes/aluno_routes.py:10), [curso_routes.py:10](backend/app/routes/curso_routes.py:10) | Retornam booleano e mandam para o **login** (mesmo logado), enquanto as demais rotas mandam para o dashboard. Além disso a função está duplicada em 7 arquivos — centralizar num decorator `@perfil_required("secretaria")`. |
| 4.7 | Exclusão de curso/turma/aluno com vínculos | `excluir_*` | No MySQL/PostgreSQL a FK impede a exclusão e o usuário vê só “Não foi possível excluir”. Melhor checar vínculos e informar o motivo (ou inativar em vez de excluir). No SQLite de teste a exclusão passou porque FKs não são verificadas por padrão. |
| 4.8 | Edição de turma aceita curso inativo | [turma_routes.py:156](backend/app/routes/turma_routes.py:156) | No cadastro há validação de `status == "Ativo"`; na edição não. |
| 4.9 | Criação de tabelas no import | [run.py:6](backend/run.py:6) | `inicializar_banco` roda `create_all()` a cada import/execução e não altera tabelas existentes. Para evolução de schema usar **Flask‑Migrate (Alembic)**. |

---

## 5. Itens menores ⚪

1. `pyflakes`: import não usado `Curso` em [models/aluno.py:2](backend/app/models/aluno.py:2) e `db` em [coordenacao_routes.py:2](backend/app/routes/coordenacao_routes.py:2).
2. [requirements.txt](backend/requirements.txt) está salvo em **UTF‑16 LE** (gerado por `pip freeze > requirements.txt` no PowerShell). O `pip` consegue ler, mas muitas ferramentas (Docker, Render, Vercel, GitHub Dependabot) não. Salvar em UTF‑8.
3. `mysql-connector-python` está no requirements mas não é usado (o driver em uso é `PyMySQL`).
4. [educore.sql](backend/database/educore.sql) duplica o schema dos models (e contém `SHOW TABLES;` no meio do script). Duas fontes de verdade tendem a divergir.
5. `app.config.from_object("config.Config")` e `from database.database import …` só funcionam se o comando for executado **dentro de `backend/`**. Executar de outra pasta dá `ModuleNotFoundError`.
6. Templates misturam estilos: só `coordenacao/*` e `instrutor/painel.html` usam `{% extends "base.html" %}`; os demais são HTML completos e repetem cabeçalho. `static/js/main.js` e `static/css/style.css` não são referenciados por nenhum template. Todos dependem do `cdn.tailwindcss.com` (CDN de desenvolvimento, não recomendado em produção).

---

## 6. Viabilidade da migração para Neon (PostgreSQL em nuvem)

### Veredito: ✅ **Viável e de baixo esforço**

O projeto usa SQLAlchemy ORM em 100% do acesso a dados — **não há SQL específico de MySQL no código Python**. Os models compilam para PostgreSQL sem nenhuma alteração (validado):

```sql
CREATE TABLE alunos (
    id SERIAL NOT NULL, nome VARCHAR(120) NOT NULL, email VARCHAR(120) NOT NULL,
    cpf VARCHAR(14) NOT NULL, telefone VARCHAR(20), data_nascimento DATE NOT NULL,
    PRIMARY KEY (id), UNIQUE (email), UNIQUE (cpf)
)
-- cursos, turmas, matriculas, frequencias, notas: todos gerados sem erro
```

### 6.1 O que precisa mudar

| Item | Hoje | Com Neon |
|---|---|---|
| Driver | `PyMySQL` | `psycopg[binary]` (psycopg 3) |
| URL | `mysql+pymysql://root:root@localhost/educore` | `postgresql+psycopg://USUARIO:SENHA@ep-xxxx-pooler.REGIAO.aws.neon.tech/neondb?sslmode=require` |
| Onde fica a URL | fixa no `config.py` | variável `DATABASE_URL` no `.env` |
| Script SQL | `educore.sql` (sintaxe MySQL: `AUTO_INCREMENT`, `CREATE DATABASE`, `USE`) | Descartar e deixar o `db.create_all()`/Alembic criar as tabelas, ou reescrever com `SERIAL`/`GENERATED ALWAYS AS IDENTITY`. |

**`config.py` sugerido:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # Neon suspende o compute ocioso; evita conexões "mortas"
        "pool_recycle": 300,
    }
```

**`.env` (não vai para o Git):**
```
SECRET_KEY=<gere com: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@ep-xxxx-pooler.REGIAO.aws.neon.tech/neondb?sslmode=require
```

**`requirements.txt`:** remover `PyMySQL` e `mysql-connector-python`, adicionar `psycopg[binary]`.

> Atenção: a string que o painel do Neon fornece começa com `postgresql://`. Para usar psycopg 3 com SQLAlchemy troque o prefixo por `postgresql+psycopg://` (sem isso o SQLAlchemy procura o `psycopg2`).

### 6.2 Diferenças de comportamento MySQL → PostgreSQL a observar

| Diferença | Impacto no EduCore |
|---|---|
| **Comparação de texto sensível a maiúsculas.** O MySQL (`utf8mb4_unicode_ci`) trata `Ana@x.com` e `ana@x.com` como iguais; o PostgreSQL não. | O `UNIQUE(email)` e `UNIQUE(nome)` de cursos passam a aceitar duplicatas que só diferem em maiúsculas. Normalizar com `.lower()` antes de salvar e-mail. |
| Ordenação (`ORDER BY nome`) usa a collation do banco | Ordem pode mudar levemente para acentos/maiúsculas. |
| `FLOAT` vira `double precision` | Sem impacto (notas de 0 a 10). |
| Defaults (`"Ativo"`, `"Ativa"`) são aplicados pelo Python, não pelo banco | Sem impacto pelo ORM; inserts manuais via SQL precisarão informar o status. |

### 6.3 Particularidades do Neon

- **Scale‑to‑zero:** o compute é suspenso após um período ocioso; a primeira requisição depois disso tem um atraso de "cold start". Por isso o `pool_pre_ping=True`.
- **Use o endpoint com `-pooler`** (PgBouncer) para aplicações web; ele suporta muito mais conexões simultâneas.
- **SSL obrigatório** (`sslmode=require`).
- **Latência de rede:** cada consulta vai à internet. Os problemas de N×M consultas do item 4.4 ficam bem mais visíveis — corrigi‑los antes ou junto da migração.
- **Branches:** o Neon permite criar um branch do banco para desenvolvimento/testes sem afetar os dados de produção.
- Verifique os limites atuais do plano gratuito (armazenamento e horas de compute) no site do Neon antes de usar em produção.

### 6.4 Migração dos dados existentes (se houver dados no MySQL)

1. Criar o projeto no Neon e copiar a connection string (pooled).
2. Configurar `.env` e rodar `python run.py` uma vez — o `create_all()` cria as 6 tabelas no Neon.
3. Copiar os dados, na ordem das FKs: `cursos → alunos → turmas → matriculas → frequencias → notas`. Opções:
   - **pgloader** (`pgloader mysql://root:root@localhost/educore postgresql://...`) — migra schema + dados automaticamente; ou
   - um script Python com dois engines SQLAlchemy lendo do MySQL e inserindo no Neon.
4. **Ajustar as sequences** (senão o próximo `INSERT` dá erro de chave duplicada):
   ```sql
   SELECT setval('alunos_id_seq',      (SELECT COALESCE(MAX(id),1) FROM alunos));
   SELECT setval('cursos_id_seq',      (SELECT COALESCE(MAX(id),1) FROM cursos));
   SELECT setval('turmas_id_seq',      (SELECT COALESCE(MAX(id),1) FROM turmas));
   SELECT setval('matriculas_id_seq',  (SELECT COALESCE(MAX(id),1) FROM matriculas));
   SELECT setval('frequencias_id_seq', (SELECT COALESCE(MAX(id),1) FROM frequencias));
   SELECT setval('notas_id_seq',       (SELECT COALESCE(MAX(id),1) FROM notas));
   ```
5. Testar os 3 perfis e então desativar o MySQL local.

**Estimativa:** a troca de banco em si (itens 6.1) leva menos de 1 hora; a migração de dados depende do volume (para um projeto acadêmico, minutos).

---

## 7. Ordem recomendada de correção

1. **Renomear templates** (item 2.2) — destrava 8 rotas.
2. **Reescrever `frequencia_service.py`** (item 2.1) e o template `coordenacao/aluno.html` (2.3).
3. **Mover segredos para `.env`** (3.1, 3.2) — pré‑requisito para usar Neon com segurança.
4. **Migrar para Neon** (seção 6).
5. Corrigir commits em loop, duplicidades e consultas N×M (4.1–4.4).
6. Hash de senhas, CSRF, decorator de perfil, Flask‑Migrate (3.3, 3.4, 4.6, 4.9).
7. Limpezas da seção 5.
