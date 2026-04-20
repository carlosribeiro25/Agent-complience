import re
import json
import pdfplumber
from functools import lru_cache
from crewai.tools import BaseTool

PDF_PATH = "knowledge/simulado-BNB.pdf"

SECOES = {
    range(1, 11): "Língua Portuguesa",
    range(11, 16): "Matemática",
    range(16, 31): "Informática",
    range(31, 46): "Vendas e Negociação",
    range(46, 56): "Conhecimentos Bancários",
    range(56, 61): "Matemática Financeira",
    range(61, 66): "Inglês",
    range(66, 71): "Atualidades do Mercado Financeiro",
}


def _identificar_assunto(numero: int) -> str:
    for faixa, nome in SECOES.items():
        if numero in faixa:
            return nome
    return "Assunto não identificado"


@lru_cache(maxsize=1)
def _extrair_texto_pdf() -> str:
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            w = page.width
            left = page.crop((0, 0, w / 2, page.height))
            right = page.crop((w / 2, 0, w, page.height))
            lt = left.extract_text() or ""
            rt = right.extract_text() or ""
            text += lt + "\n" + rt + "\n"
    return text


def _extrair_questao(numero: int) -> str | None:
    texto = _extrair_texto_pdf()
    pattern_inicio = re.compile(rf"(?m)^{numero}\.\s")
    match = pattern_inicio.search(texto)
    if not match:
        return None

    inicio = match.start()
    # Find the start of the next question
    proxima = re.compile(rf"(?m)^{numero + 1}\.\s")
    match_prox = proxima.search(texto, inicio + 1)
    if match_prox:
        fim = match_prox.start()
    else:
        fim = min(inicio + 2000, len(texto))

    raw = texto[inicio:fim].strip()
    return _formatar_questao(raw, numero)


def _formatar_questao(raw: str, numero: int) -> str:
    # Remove page numbers (lines that are just a number alone)
    lines = raw.split("\n")
    lines = [l for l in lines if not re.match(r"^\d{1,2}$", l.strip())]

    # Remove section headers that may appear mid-question
    headers = [
        "LÍNGUA PORTUGUESA", "MATEMÁTICA", "INFORMÁTICA",
        "VENDAS E NEGOCIAÇÃO", "CONHECIMENTOS BANCÁRIOS",
        "MATEMÁTICA FINANCEIRA", "INGLÊS",
        "ATUALIDADES DO MERCADO FINANCEIRO",
    ]
    lines = [l for l in lines if l.strip().upper() not in headers]

    # Join lines and reconstruct: merge broken lines into paragraphs,
    # but keep alternatives on their own lines
    result_parts = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line starts an alternative: (A), (B), etc.
        is_alternative = re.match(r"^\([A-E]\)\s", stripped)

        if is_alternative:
            # Flush buffer as enunciado paragraph
            if buffer:
                result_parts.append(buffer.strip())
                buffer = ""
            buffer = stripped
        else:
            # If buffer has an alternative, check if this continues it
            if buffer and re.match(r"^\([A-E]\)\s", buffer):
                buffer += " " + stripped
            elif buffer:
                buffer += " " + stripped
            else:
                buffer = stripped

    if buffer:
        result_parts.append(buffer.strip())

    # Separate enunciado from alternatives
    enunciado_lines = []
    alternativas = []

    for part in result_parts:
        if re.match(r"^\([A-E]\)\s", part):
            alternativas.append(part)
        else:
            enunciado_lines.append(part)

    enunciado = "\n\n".join(enunciado_lines)
    alts = "\n".join(alternativas)

    return f"{enunciado}\n\n{alts}" if alts else enunciado


def extrair_questao_estruturada(numero: int) -> dict | None:
    """Extrai questão como dados estruturados para renderização interativa."""
    texto = _extrair_texto_pdf()
    pattern_inicio = re.compile(rf"(?m)^{numero}\.\s")
    match = pattern_inicio.search(texto)
    if not match:
        return None

    inicio = match.start()
    proxima = re.compile(rf"(?m)^{numero + 1}\.\s")
    match_prox = proxima.search(texto, inicio + 1)
    fim = match_prox.start() if match_prox else min(inicio + 2000, len(texto))

    raw = texto[inicio:fim].strip()

    # Clean lines
    lines = raw.split("\n")
    lines = [l for l in lines if not re.match(r"^\d{1,2}$", l.strip())]
    headers = [
        "LÍNGUA PORTUGUESA", "MATEMÁTICA", "INFORMÁTICA",
        "VENDAS E NEGOCIAÇÃO", "CONHECIMENTOS BANCÁRIOS",
        "MATEMÁTICA FINANCEIRA", "INGLÊS",
        "ATUALIDADES DO MERCADO FINANCEIRO",
    ]
    lines = [l for l in lines if l.strip().upper() not in headers]

    result_parts = []
    buffer = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        is_alternative = re.match(r"^\([A-E]\)\s", stripped)
        if is_alternative:
            if buffer:
                result_parts.append(buffer.strip())
                buffer = ""
            buffer = stripped
        else:
            if buffer:
                buffer += " " + stripped
            else:
                buffer = stripped
    if buffer:
        result_parts.append(buffer.strip())

    enunciado_parts = []
    alternativas = {}
    for part in result_parts:
        m = re.match(r"^\(([A-E])\)\s(.+)", part)
        if m:
            alternativas[m.group(1)] = m.group(2)
        else:
            enunciado_parts.append(part)

    return {
        "numero": numero,
        "assunto": _identificar_assunto(numero),
        "enunciado": "\n\n".join(enunciado_parts),
        "alternativas": alternativas,
    }


def carregar_gabarito() -> dict:
    try:
        with open("gabarito.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class BuscarQuestaoSimulado(BaseTool):
    name: str = "buscar_questao_simulado"
    description: str = (
        "Busca uma questão específica do simulado BNB pelo número (1 a 70). "
        "Retorna o enunciado completo com alternativas e o assunto abordado. "
        "Use quando o usuário perguntar sobre uma questão do simulado."
    )

    def _run(self, numero: str) -> str:
        try:
            num = int(re.search(r"\d+", str(numero)).group())
        except (AttributeError, ValueError):
            return "Número de questão inválido. Informe um número de 1 a 70."

        if num < 1 or num > 70:
            return "O simulado possui questões de 1 a 70. Informe um número válido."

        questao = _extrair_questao(num)
        if not questao:
            return f"Não foi possível extrair a questão {num} do simulado."

        assunto = _identificar_assunto(num)
        return f"📌 Assunto: {assunto}\n\n{questao}"
