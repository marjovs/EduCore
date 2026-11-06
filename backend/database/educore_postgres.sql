-- Schema do EduCore para PostgreSQL / Neon.
-- Normalmente NÃO é preciso rodar este script: ao iniciar o app (python run.py),
-- o db.create_all() cria estas tabelas automaticamente a partir dos models.
-- Use-o apenas se quiser criar o schema manualmente pelo SQL Editor do Neon.

CREATE TABLE IF NOT EXISTS alunos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    cpf             VARCHAR(14)  NOT NULL UNIQUE,
    telefone        VARCHAR(20),
    data_nascimento DATE         NOT NULL
);

CREATE TABLE IF NOT EXISTS cursos (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(120) NOT NULL UNIQUE,
    descricao     TEXT,
    carga_horaria INTEGER      NOT NULL,
    modalidade    VARCHAR(50)  NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'Ativo'
);

CREATE TABLE IF NOT EXISTS turmas (
    id       SERIAL PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    ano      INTEGER      NOT NULL,
    turno    VARCHAR(30)  NOT NULL,
    status   VARCHAR(20)  NOT NULL DEFAULT 'Ativa',
    curso_id INTEGER      NOT NULL REFERENCES cursos (id)
);

CREATE TABLE IF NOT EXISTS matriculas (
    id             SERIAL PRIMARY KEY,
    data_matricula DATE        NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'Ativa',
    aluno_id       INTEGER     NOT NULL REFERENCES alunos (id),
    turma_id       INTEGER     NOT NULL REFERENCES turmas (id)
);

CREATE TABLE IF NOT EXISTS frequencias (
    id           SERIAL PRIMARY KEY,
    data         DATE        NOT NULL,
    status       VARCHAR(20) NOT NULL,
    observacao   TEXT,
    matricula_id INTEGER     NOT NULL REFERENCES matriculas (id),
    CONSTRAINT uq_frequencia_matricula_data UNIQUE (matricula_id, data)
);

CREATE TABLE IF NOT EXISTS notas (
    id           SERIAL PRIMARY KEY,
    avaliacao    VARCHAR(100)     NOT NULL,
    valor        DOUBLE PRECISION NOT NULL,
    data         DATE             NOT NULL,
    matricula_id INTEGER          NOT NULL REFERENCES matriculas (id),
    CONSTRAINT uq_nota_matricula_avaliacao UNIQUE (matricula_id, avaliacao)
);

-- Usuários do sistema (senhas guardadas como hash; os usuários iniciais
-- são criados pelo app na primeira execução).
CREATE TABLE IF NOT EXISTS usuarios (
    id         SERIAL PRIMARY KEY,
    email      VARCHAR(120) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil     VARCHAR(20)  NOT NULL
);
