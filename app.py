from flask import Flask, request, jsonify, session, render_template
from google import genai
from dotenv import load_dotenv
from PIL import Image
import os
import random
import re

load_dotenv()

app = Flask(__name__)

# Necessário para que o Flask consiga criar/assinar o cookie de sessão.
# Em produção, coloque isso no .env também (ex: FLASK_SECRET_KEY=algum-valor-aleatorio-grande).
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")

# Limite de tamanho do corpo da requisição (evita upload de imagem gigante travando o servidor).
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")

# ANTES (SDK antigo): genai.configure(api_key=...) + genai.GenerativeModel(...)
# guardavam a configuração de forma global no módulo.
# AGORA: o SDK novo usa um objeto "client" explícito, que carrega tudo que
# precisamos pra chamar a API (chave e, depois, o nome do modelo é passado
# em cada chamada, não fica preso a um objeto "model").
client = genai.Client(api_key=api_key)

# Uso o alias "gemini-flash-latest" em vez de fixar uma versão (ex: "gemini-2.5-flash").
# O Google aposenta modelos com frequência; esse alias sempre aponta pro Flash
# mais recente disponível, então o código não quebra a cada nova versão.
NOME_MODELO = "gemini-flash-latest"


# ---------------------------------------------------------------------------
# ANTES: historico, jogo_ativo e numero_secreto eram variáveis globais,
# compartilhadas por TODOS os usuários que acessassem a API ao mesmo tempo.
# AGORA: cada usuário tem seu próprio estado, guardado na sessão do Flask
# (um cookie assinado que identifica o navegador/cliente). Assim, dois
# usuários jogando ao mesmo tempo não interferem um no jogo do outro.
# ---------------------------------------------------------------------------

def get_estado():
    """Garante que a sessão atual tenha os campos de estado inicializados."""
    if "historico" not in session:
        session["historico"] = []
    if "jogo_ativo" not in session:
        session["jogo_ativo"] = False
    if "numero_secreto" not in session:
        session["numero_secreto"] = 0
    return session


def perguntar_ia(texto):
    prompt = f"""
Você é o Genius IA.

Seja amigável.
Ajude estudantes.
Explique programação passo a passo.
Seja direto e claro.

Usuário:
{texto}
"""

    resposta = client.models.generate_content(
        model=NOME_MODELO,
        contents=prompt,
    )

    return resposta.text


def calculadora(a, b, op):
    if op == "+":
        return a + b

    if op == "-":
        return a - b

    if op == "*":
        return a * b

    if op == "/":
        if b == 0:
            return "Não pode dividir por zero"

        return a / b

    return "Operador inválido"


# ---------------------------------------------------------------------------
# ANTES: a função fazia várias substituições de string em sequência
# (.replace("mais", "+"), .replace("por", "") etc) e depois dava split().
# Isso é frágil: qualquer variação na frase ("dividido por" vs "dividir por",
# espaços extras, etc) podia quebrar o parsing.
# AGORA: uma regex captura o padrão "número operador número" diretamente,
# aceitando tanto símbolos (+, -, *, /) quanto palavras (mais, menos, vezes,
# dividido). É mais previsível e mais fácil de estender no futuro.
# ---------------------------------------------------------------------------

PADRAO_CALCULO = re.compile(
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(\+|-|\*|/|mais|menos|vezes|dividido(?:\s+por)?)\s*"
    r"(-?\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)

MAPA_OPERADORES = {
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "mais": "+",
    "menos": "-",
    "vezes": "*",
    "dividido": "/",
    "dividido por": "/",
}


def interpretar_calculo(texto, estado):
    match = PADRAO_CALCULO.search(texto.lower())

    if not match:
        return None

    num1_str, op_str, num2_str = match.groups()

    num1 = float(num1_str.replace(",", "."))
    num2 = float(num2_str.replace(",", "."))

    op_str = op_str.strip()
    operador = MAPA_OPERADORES.get(op_str)

    if operador is None:
        return None

    resultado = calculadora(num1, num2, operador)

    estado["historico"].append(f"{num1} {operador} {num2} = {resultado}")
    estado.modified = True  # avisa o Flask que a lista dentro da sessão mudou

    return f"Resultado: {resultado}"


def detectar_intencao(texto):
    texto = texto.lower()

    if "jogar" in texto:
        return "jogo"

    if "historico" in texto or "histórico" in texto:
        return "historico"

    if PADRAO_CALCULO.search(texto):
        return "calculo"

    return "ia"


def responder(texto):
    estado = get_estado()

    if estado["jogo_ativo"]:
        try:
            palpite = int(texto)

            if palpite == estado["numero_secreto"]:
                estado["jogo_ativo"] = False
                return "🎉 Acertou!"

            if palpite < estado["numero_secreto"]:
                return "Maior!"

            return "Menor!"

        except ValueError:
            return "Digite um número."

    intencao = detectar_intencao(texto)

    if intencao == "jogo":
        estado["numero_secreto"] = random.randint(1, 100)
        estado["jogo_ativo"] = True

        return "🎮 Pensei em um número de 1 a 100"

    if intencao == "historico":
        if estado["historico"]:
            return "\n".join(estado["historico"])

        return "Histórico vazio"

    if intencao == "calculo":
        resultado = interpretar_calculo(texto, estado)

        if resultado:
            return resultado

    return perguntar_ia(texto)


# Serve o front-end (templates/index.html). O Flask, por padrão, já serve
# tudo que estiver dentro da pasta static/ no caminho /static/<arquivo>
# (é por isso que o index.html usa url_for('static', filename=...)).
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    texto = request.form.get("mensagem", "").strip()
    imagem = request.files.get("imagem")

    if not texto and not imagem:
        return jsonify({
            "resposta": "Digite uma mensagem ou envie uma imagem."
        }), 400

    if imagem:
        try:
            img = Image.open(imagem)

            resposta = client.models.generate_content(
                model=NOME_MODELO,
                contents=[texto or "Analise esta imagem.", img],
            )

            return jsonify({
                "resposta": resposta.text
            })

        except Exception as erro:
            # Antes o erro real desaparecia; agora ele aparece no terminal
            # onde o Flask está rodando, mesmo com a mensagem genérica indo
            # pro usuário. Facilita muito debugar da próxima vez.
            print(f"[ERRO ao analisar imagem] {erro}")
            return jsonify({
                "resposta": "Não consegui analisar essa imagem."
            }), 400

    try:
        resposta = responder(texto)

        return jsonify({
            "resposta": resposta
        })

    except Exception as erro:
        print(f"[ERRO ao responder] {erro}")
        return jsonify({
            "resposta": "Ocorreu um erro ao processar sua mensagem."
        }), 500


if __name__ == "__main__":
    # ANTES: debug=True estava fixo no código, o que é um risco em produção
    # (se der erro, o Flask mostra um console interativo que executa código
    # Python no servidor). Agora o modo debug só liga se você definir
    # FLASK_DEBUG=1 no .env — em produção, deixe sem essa variável.
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)