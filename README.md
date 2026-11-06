<div align="center">

# 🎓 EduCore

**Sistema web de gestão acadêmica: alunos, cursos, turmas, matrículas, notas e frequência em um só lugar.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

<img src="docs/img/login.png" alt="Tela de login do EduCore" width="720">

</div>

---

## 📑 Sumário

- [Sobre o projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Telas](#-telas)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração do `.env`](#-configuração-do-env)
- [Banco de dados](#-banco-de-dados)
- [Executando o projeto](#️-executando-o-projeto)
- [Acessos de desenvolvimento](#-acessos-de-desenvolvimento)
- [Segurança](#-segurança)
- [Solução de problemas](#-solução-de-problemas)
- [Roadmap](#️-roadmap)
- [Autoria](#-autoria)

---

## 📌 Sobre o projeto

O **EduCore** é uma aplicação web para instituições de ensino que centraliza a rotina acadêmica em três perfis de acesso:

| Perfil | Papel no sistema |
|---|---|
| 🗂️ **Secretaria** | Mantém o cadastro de alunos, cursos e turmas e realiza as matrículas. |
| 👩‍🏫 **Instrutor** | Registra a frequência diária e lança as notas das avaliações de suas turmas. |
| 📊 **Coordenação** | Acompanha indicadores e consulta alunos, matrículas, desempenho e frequência. |

Cada perfil vê apenas as telas que lhe dizem respeito. O banco de dados é um **PostgreSQL gerenciado na nuvem ([Neon](https://neon.tech))**, então os dados ficam disponíveis de qualquer computador.

---

## ✨ Funcionalidades

### 🗂️ Secretaria
- **Alunos:** cadastro, edição e exclusão, com validação de e-mail e CPF únicos.
- **Cursos:** carga horária, modalidade (Presencial, EAD ou Híbrido) e status (Ativo ou Inativo).
- **Turmas:** vinculadas a um curso ativo, com ano, turno e status.
- **Matrículas:** vínculo aluno ↔ turma, com bloqueio de matrícula ativa duplicada e opção de cancelamento.
- **Integridade:** não é possível excluir curso com turmas, turma com matrículas nem aluno com matrículas; o sistema explica o motivo.

### 👩‍🏫 Instrutor
- **Frequência:** registro de presença ou falta por aluno e por dia. Um novo envio no mesmo dia atualiza o registro em vez de duplicar.
- **Notas:** lançamento de notas de 0 a 10 por avaliação (aceita vírgula). A mesma avaliação não pode ser lançada duas vezes.
- **Gravação atômica:** os dados da turma inteira são salvos numa única transação.

### 📊 Coordenação
- **Painel** com total de alunos, matrículas ativas, notas e registros de frequência.
- **Consultas** de alunos (com número de matrículas ativas), matrículas, desempenho e frequência.

---

## 🖼️ Telas

| Secretaria: alunos | Secretaria: matrículas |
|---|---|
| <img src="docs/img/secretaria-alunos.png" alt="Lista de alunos"> | <img src="docs/img/secretaria-matriculas.png" alt="Lista de matrículas"> |
| **Instrutor: lançamento de notas** | **Coordenação: painel** |
| <img src="docs/img/instrutor-notas.png" alt="Lançamento de notas"> | <img src="docs/img/coordenacao-painel.png" alt="Painel da coordenação"> |
| **Coordenação: desempenho** | **Secretaria: painel** |
| <img src="docs/img/coordenacao-desempenho.png" alt="Desempenho acadêmico"> | <img src="docs/img/secretaria-painel.png" alt="Painel da secretaria"> |

> As capturas usam dados fictícios.

---

## 🧰 Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | [Python 3.12](https://www.python.org/) |
| Framework web | [Flask 3.1](https://flask.palletsprojects.com/) |
| ORM | [SQLAlchemy 2.1](https://www.sqlalchemy.org/) + [Flask-SQLAlchemy 3.1](https://flask-sqlalchemy.readthedocs.io/) |
| Banco de dados | [PostgreSQL](https://www.postgresql.org/) hospedado no [Neon](https://neon.tech) |
| Driver | [psycopg 3](https://www.psycopg.org/psycopg3/) |
| Segurança | [Flask-WTF](https://flask-wtf.readthedocs.io/) (CSRF) e Werkzeug (hash de senhas) |
| Templates | [Jinja2](https://jinja.palletsprojects.com/) |
| Estilo | [Tailwind CSS](https://tailwindcss.com/) (via CDN) |
| Configuração | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## 🏗️ Arquitetura

O backend segue uma separação em camadas: **rotas** recebem e validam a requisição, **serviços** aplicam as regras de negócio, e **models** representam as tabelas.

```mermaid
flowchart LR
    U([👤 Usuário]) -->|HTTP| R[Rotas<br/>Blueprints Flask]
    R -->|"@perfil_required"| A{Controle<br/>de acesso}
    A --> S[Serviços<br/>regras de negócio]
    S --> M[Models<br/>SQLAlchemy]
    M -->|psycopg 3 + TLS| DB[(PostgreSQL<br/>Neon)]
    R --> T[Templates<br/>Jinja2 + Tailwind]
    T --> U
```

### Modelo de dados

```mermaid
erDiagram
    CURSOS ||--o{ TURMAS : possui
    TURMAS ||--o{ MATRICULAS : recebe
    ALUNOS ||--o{ MATRICULAS : realiza
    MATRICULAS ||--o{ NOTAS : tem
    MATRICULAS ||--o{ FREQUENCIAS : tem

    CURSOS {
        int id PK
        string nome UK
        int carga_horaria
        string modalidade
        string status
    }
    TURMAS {
        int id PK
        string nome
        int ano
        string turno
        string status
        int curso_id FK
    }
    ALUNOS {
        int id PK
        string nome
        string email UK
        string cpf UK
        date data_nascimento
    }
    MATRICULAS {
        int id PK
        date data_matricula
        string status
        int aluno_id FK
        int turma_id FK
    }
    NOTAS {
        int id PK
        string avaliacao
        float valor
        date data
        int matricula_id FK
    }
    FREQUENCIAS {
        int id PK
        date data
        string status
        int matricula_id FK
    }
    USUARIOS {
        int id PK
        string email UK
        string senha_hash
        string perfil
    }
```

### Estrutura de pastas

```text
EduCore/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # create_app(): Flask, SQLAlchemy, CSRF e blueprints
│   │   ├── acesso.py            # decorator @perfil_required
│   │   ├── models/              # Aluno, Curso, Turma, Matricula, Nota, Frequencia, Usuario
│   │   ├── services/            # regras de negócio (uma por entidade)
│   │   └── routes/              # blueprints: auth, secretaria, instrutor, coordenacao...
│   ├── database/
│   │   ├── database.py          # criação das tabelas e dos usuários iniciais
│   │   └── educore_postgres.sql # schema de referência em SQL
│   ├── config.py                # lê o .env e configura o banco
│   ├── run.py                   # ponto de entrada da aplicação
│   ├── requirements.txt
│   └── .env.example             # modelo das variáveis de ambiente
├── frontend/
│   ├── templates/               # páginas Jinja2 por perfil
│   └── static/                  # CSS e JS
├── docs/img/                    # imagens deste README
└── relatorio.md                 # relatório técnico de análise e correções
```

---

## 🚀 Instalação

### Pré-requisitos

| Ferramenta | Versão | Download |
|---|---|---|
| 🐍 Python | 3.12 ou superior | [python.org/downloads](https://www.python.org/downloads/) |
| 🌱 Git | qualquer recente | [git-scm.com](https://git-scm.com/) |
| 🐘 Banco PostgreSQL | conta gratuita no Neon | [neon.tech](https://neon.tech) |

> No Windows, marque a opção **"Add Python to PATH"** durante a instalação do Python.

### 1. Clonar o repositório

```bash
git clone https://github.com/marjovs/EduCore.git
cd EduCore
```

### 2. Criar e ativar o ambiente virtual

<details open>
<summary><b>🪟 Windows (PowerShell)</b></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Se aparecer erro de *execution policy*, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

</details>

<details>
<summary><b>🐧 Linux / 🍎 macOS</b></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>

Com o ambiente ativo, o terminal mostra `(.venv)` no início da linha.

### 3. Instalar as dependências

```bash
pip install -r backend/requirements.txt
```

### 4. Criar o arquivo `.env`

Copie o modelo e depois preencha os valores (veja a [próxima seção](#-configuração-do-env)):

```bash
# Windows
copy backend\.env.example backend\.env

# Linux / macOS
cp backend/.env.example backend/.env
```

---

## 🔐 Configuração do `.env`

O arquivo **`backend/.env`** guarda as configurações sensíveis. Ele está no `.gitignore` e **nunca deve ser enviado ao GitHub**. O modelo completo, com comentários, está em [`backend/.env.example`](backend/.env.example).

| Variável | Obrigatória | Descrição |
|---|:---:|---|
| `SECRET_KEY` | ✅ | Chave que assina o cookie de sessão. Gere uma com o comando abaixo. |
| `DATABASE_URL` | ✅ | Connection string do PostgreSQL (Neon, local ou outro). |
| `FLASK_DEBUG` | ➖ | `1` liga o modo debug (recarrega ao salvar). Use `0` em produção. |
| `SENHA_SECRETARIA` | ➖ | Senha inicial do usuário da secretaria. |
| `SENHA_INSTRUTOR` | ➖ | Senha inicial do usuário instrutor. |
| `SENHA_COORDENACAO` | ➖ | Senha inicial do usuário da coordenação. |

Para gerar uma `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Exemplo de `.env` preenchido:

```dotenv
SECRET_KEY=3f9c1a...gerada-pelo-comando-acima...b72e
DATABASE_URL=postgresql://usuario:senha@ep-exemplo-123456-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FLASK_DEBUG=1
```

> 💡 Pode colar a URL do Neon exatamente como ele mostra (`postgresql://...`). O `config.py` ajusta o prefixo para o driver `psycopg` automaticamente.

---

## 🐘 Banco de dados

### Criando o banco no Neon

1. Crie uma conta gratuita em [neon.tech](https://neon.tech) e um novo projeto. A região **São Paulo (`sa-east-1`)** dá menor latência no Brasil.
2. No painel do projeto, clique em **Connect**.
3. Marque **Connection pooling** e copie a connection string.
4. Cole a string em `DATABASE_URL` no `backend/.env`.

### Criação das tabelas

Não é preciso rodar nenhum script SQL. Na primeira execução, o EduCore:

1. cria as 7 tabelas (`alunos`, `cursos`, `turmas`, `matriculas`, `notas`, `frequencias` e `usuarios`);
2. cria os 3 usuários iniciais, se a tabela `usuarios` estiver vazia.

O arquivo [`backend/database/educore_postgres.sql`](backend/database/educore_postgres.sql) contém o mesmo schema em SQL, para consulta ou criação manual pelo *SQL Editor* do Neon.

> ℹ️ O plano gratuito do Neon suspende o banco após alguns minutos sem uso. A primeira requisição depois disso pode levar alguns segundos a mais; a aplicação já trata a reconexão automaticamente (`pool_pre_ping`).

---

## ▶️ Executando o projeto

Com o ambiente virtual ativo, a partir da raiz do projeto:

```bash
python backend/run.py
```

Saída esperada:

```text
Banco de dados EduCore inicializado com sucesso!
 * Running on http://127.0.0.1:5000
```

Abra **http://127.0.0.1:5000** no navegador. 🎉

---

## 🔑 Acessos de desenvolvimento

| Perfil | E-mail | Senha |
|---|---|---|
| 🗂️ Secretaria | `secretaria@educore.com` | `012345` |
| 👩‍🏫 Instrutor | `instrutor@educore.com` | `123456` |
| 📊 Coordenação | `coordenacao@educore.com` | `234567` |

> ⚠️ Essas senhas valem apenas quando as variáveis `SENHA_*` não estão definidas no `.env`. **Antes de qualquer uso real, defina senhas fortes.** Elas só são aplicadas quando a tabela `usuarios` ainda está vazia; depois disso, as senhas precisam ser trocadas no próprio banco.

### Roteiro rápido de teste

1. **Secretaria:** cadastre um curso, uma turma, dois alunos e as matrículas.
2. **Instrutor:** registre a frequência da turma e lance as notas da "Prova 1".
3. **Coordenação:** confira os indicadores do painel e as consultas.

---

## 🛡️ Segurança

- 🔒 **Senhas com hash** (`scrypt`, via Werkzeug); nenhuma senha é guardada em texto puro.
- 🧾 **Proteção CSRF** em todos os formulários (Flask-WTF).
- 👥 **Controle de acesso por perfil** com o decorator `@perfil_required`.
- 🗝️ **Segredos fora do código:** `SECRET_KEY` e a URL do banco ficam apenas no `.env`.
- 🔐 **Conexão criptografada** com o banco (`sslmode=require`).

---

## 🧯 Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `RuntimeError: DATABASE_URL não definida` | O `backend/.env` não existe ou está vazio | Crie-o a partir do `.env.example` (passo 4 da instalação). |
| `ModuleNotFoundError: No module named 'flask'` (ou `psycopg`) | Ambiente virtual desativado ou dependências não instaladas | Ative o `.venv` e rode `pip install -r backend/requirements.txt`. |
| `password authentication failed` | Usuário ou senha incorretos na `DATABASE_URL` | Copie a URL de novo no painel do Neon. |
| "Sua sessão expirou ou o formulário é inválido" | O token CSRF expirou ou a `SECRET_KEY` mudou | Recarregue a página e envie de novo. |
| Primeira página demora a abrir | O banco do Neon estava suspenso | Normal no plano gratuito; as próximas requisições ficam rápidas. |
| `Address already in use` (porta 5000) | Outra instância do app está rodando | Feche o outro terminal ou finalize o processo `python`. |

---

## 🗺️ Roadmap

- [x] Migração do MySQL local para PostgreSQL na nuvem (Neon)
- [x] Autenticação com hash de senha e proteção CSRF
- [x] Regras de integridade (duplicidades e exclusões com vínculo)
- [ ] Migrações de schema versionadas com Flask-Migrate (Alembic)
- [ ] Tela para cadastrar usuários e trocar senhas
- [ ] Padronizar todos os templates a partir do `base.html`
- [ ] Gerar o CSS do Tailwind localmente, sem depender do CDN
- [ ] Testes automatizados com `pytest`

O histórico detalhado de análise e correções está em [`relatorio.md`](relatorio.md).

---

## 👩‍💻 Autoria

Desenvolvido por **Jovana Maciel** ([@marjovs](https://github.com/marjovs)).

<div align="center">
<sub>Feito com 💙 e Python.</sub>
</div>
