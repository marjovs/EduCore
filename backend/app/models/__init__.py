"""Importa todos os models (usado pelo Flask-Migrate para enxergar as tabelas)."""
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.turma import Turma
from app.models.usuario import Usuario

__all__ = ["Aluno", "Curso", "Frequencia", "Matricula", "Nota", "Turma", "Usuario"]
