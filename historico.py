import json
import os
from datetime import datetime

ARQUIVO = "historico.json"

def carregar_historico() -> list:
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def salvar_entrada(pergunta: str, resposta: str) -> None:
    historico = carregar_historico()
    historico.append(
        {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "pergunta": pergunta,
            "resposta": resposta,
        }
    )
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[historico] Erro ao salvar: {e}")


def limpar_historico() -> None:
    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)