CREATE DATABASE educore
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE educore;

SHOW TABLES;

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    data_nascimento DATE NOT NULL
);

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    carga_horaria INT NOT NULL,
    modalidade VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Ativo'
);

CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ano INT NOT NULL,
    turno VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Ativa',
    curso_id INT NOT NULL,
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);

CREATE TABLE matriculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_matricula DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Ativa',
    aluno_id INT NOT NULL,
    turma_id INT NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
);

CREATE TABLE frequencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    observacao TEXT,
    matricula_id INT NOT NULL,
    FOREIGN KEY (matricula_id) REFERENCES matriculas(id)
);

CREATE TABLE notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    avaliacao VARCHAR(100) NOT NULL,
    valor FLOAT NOT NULL,
    data DATE NOT NULL,
    matricula_id INT NOT NULL,
    FOREIGN KEY (matricula_id) REFERENCES matriculas(id)
);