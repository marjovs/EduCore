"""Validações e formatações reaproveitadas pelos formulários."""
import re
from datetime import date

# Maior valor de uma coluna INTEGER no PostgreSQL. IDs, anos e páginas acima
# disso nem chegam ao banco (evita erro 500 com números gigantes na URL).
MAIOR_INTEIRO = 2_147_483_647

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def somente_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def cpf_valido(cpf):
    """Confere os 11 dígitos e os dois dígitos verificadores do CPF."""
    digitos = somente_digitos(cpf)

    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False

    for posicao in (9, 10):
        soma = sum(int(digitos[i]) * (posicao + 1 - i) for i in range(posicao))
        verificador = soma * 10 % 11 % 10
        if verificador != int(digitos[posicao]):
            return False

    return True


def formatar_cpf(cpf):
    """11122233344 -> 111.222.333-44 (outros valores voltam como estão)."""
    digitos = somente_digitos(cpf)
    if len(digitos) != 11:
        return cpf or ""
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def email_valido(email):
    return bool(_EMAIL.match(email or ""))


def data_nascimento_valida(data):
    return date(1900, 1, 1) <= data <= date.today()


def texto_grande_demais(campos):
    """Recebe {rótulo: (valor, limite)} e devolve a mensagem do primeiro campo
    que passa do limite, ou None."""
    for rotulo, (valor, limite) in campos.items():
        if valor and len(valor) > limite:
            return f"O campo {rotulo} aceita no máximo {limite} caracteres."
    return None


def inteiro_seguro(texto):
    """Converte texto em inteiro positivo dentro do limite do banco, ou None."""
    texto = (texto or "").strip()
    if not texto.isdigit() or len(texto) > 10:
        return None
    valor = int(texto)
    return valor if 0 < valor <= MAIOR_INTEIRO else None
