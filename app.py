from flask import Flask, request, jsonify
import google.generativeai as genai
from PIL import Image
import random

app = Flask(__name__)

# ====================================
# COLOQUE SUA API KEY AQUI
# ====================================

genai.configure(
    api_key="AIzaSyBdcGgWf7dXsCBhiSthQX7zwO1B6hUneUA"
)

model = genai.GenerativeModel(
    "gemini-1.5-flash-latest"
)

# ====================================
# VARIÁVEIS
# ====================================

historico = []

jogo_ativo = False
numero_secreto = 0

# ====================================
# IA
# ====================================

def perguntar_ia(texto):

    prompt = f"""
Você é o Genius IA.

- Seja amigável
- Ajude estudantes
- Explique programação passo a passo
- Seja direto

Usuário:
{texto}
"""

    resposta = model.generate_content(
        prompt
    )

    return resposta.text

# ====================================
# CALCULADORA
# ====================================

def calculadora(a, b, op):

    if op == "+":
        return a + b

    elif op == "-":
        return a - b

    elif op == "*":
        return a * b

    elif op == "/":

        if b == 0:
            return "Não pode dividir por zero"

        return a / b

    return "Operador inválido"

def interpretar_calculo(texto):

    texto = texto.lower()

    texto = texto.replace("mais", "+")
    texto = texto.replace("menos", "-")
    texto = texto.replace("vezes", "*")
    texto = texto.replace("dividido", "/")
    texto = texto.replace("por", "")

    partes = texto.split()

    numeros = []
    operador = None

    for p in partes:

        try:
            numeros.append(float(p))

        except:

            if p in ["+", "-", "*", "/"]:
                operador = p

    if len(numeros) >= 2 and operador:

        resultado = calculadora(
            numeros[0],
            numeros[1],
            operador
        )

        historico.append(
            f"{numeros[0]} {operador} {numeros[1]} = {resultado}"
        )

        return f"Resultado: {resultado}"

    return None

# ====================================
# DETECTAR INTENÇÃO
# ====================================

def detectar_intencao(texto):

    texto = texto.lower()

    if "jogar" in texto:
        return "jogo"

    if "historico" in texto:
        return "historico"

    if any(
        op in texto
        for op in [
            "+",
            "-",
            "*",
            "/",
            "mais",
            "menos",
            "vezes",
            "dividido"
        ]
    ):
        return "calculo"

    return "ia"

# ====================================
# CÉREBRO
# ====================================

def responder(texto):

    global jogo_ativo
    global numero_secreto

    # =================
    # JOGO
    # =================

    if jogo_ativo:

        try:

            palpite = int(texto)

            if palpite == numero_secreto:

                jogo_ativo = False

                return "🎉 Acertou!"

            elif palpite < numero_secreto:

                return "Maior!"

            else:

                return "Menor!"

        except:

            return "Digite um número."

    # =================
    # INTENÇÃO
    # =================

    intencao = detectar_intencao(texto)

    # =================
    # JOGO
    # =================

    if intencao == "jogo":

        numero_secreto = random.randint(1, 100)

        jogo_ativo = True

        return "🎮 Pensei em um número de 1 a 100"

    # =================
    # HISTÓRICO
    # =================

    elif intencao == "historico":

        if historico:

            return "\n".join(historico)

        return "Histórico vazio"

    # =================
    # CALCULADORA
    # =================

    elif intencao == "calculo":

        resultado = interpretar_calculo(texto)

        if resultado:
            return resultado

    # =================
    # IA
    # =================

    return perguntar_ia(texto)

# ====================================
# API
# ====================================

@app.route("/chat", methods=["POST"])
def chat():

    texto = request.form.get(
        "mensagem",
        ""
    )

    imagem = request.files.get(
        "imagem"
    )

    # =================
    # CASO TENHA IMAGEM
    # =================

    if imagem:

        img = Image.open(imagem)

        resposta = model.generate_content([
            texto,
            img
        ])

        return jsonify({
            "resposta": resposta.text
        })

    # =================
    # SEM IMAGEM
    # =================

    resposta = responder(texto)

    return jsonify({
        "resposta": resposta
    })

# ====================================
# INICIAR
# ====================================

if __name__ == "__main__":

    app.run(
        debug=True
    )