async function enviar() {

    let input =
        document.getElementById(
            "mensagem"
        );

    let imagem =
        document.getElementById(
            "imagem"
        );

    let texto =
        input.value.trim();

    let file =
        imagem.files[0];

    if (!texto && !file) return;

    // ====================
    // MENSAGEM USUÁRIO
    // ====================

    if(texto){

        adicionarMensagem(
            texto,
            "user"
        );

    }

    // ====================
    // IMAGEM
    // ====================

    if(file){

        let url =
            URL.createObjectURL(file);

        adicionarImagem(
            url,
            "user"
        );
    }

    // ====================
    // FORM DATA
    // ====================

    let formData =
        new FormData();

    formData.append(
        "mensagem",
        texto
    );

    if(file){

        formData.append(
            "imagem",
            file
        );
    }

    input.value = "";
    imagem.value = "";

    // ====================
    // FETCH
    // ====================

    // ANTES: URL absoluta "http://127.0.0.1:5000/chat".
    // AGORA: URL relativa "/chat", porque o próprio Flask está servindo
    // esta página (mesma origem). Isso evita problemas de CORS.
    // "credentials: same-origin" garante que o cookie de sessão seja
    // enviado junto — sem isso, o Flask não lembra do jogo/histórico
    // entre uma mensagem e outra.
    let resposta =
        await fetch(
            "/chat",
            {
                method: "POST",
                credentials: "same-origin",
                body: formData
            }
        );

    let dados =
        await resposta.json();

    adicionarMensagem(
        dados.resposta,
        "bot"
    );
}

// ====================
// ADICIONAR MENSAGEM
// ====================

function adicionarMensagem(
    texto,
    tipo
){

    let chat =
        document.getElementById(
            "chat"
        );

    let div =
        document.createElement(
            "div"
        );

    div.className = tipo;

    // white-space: pre-line faz o texto respeitar as quebras de linha (\n)
    // que vêm tanto da mensagem de boas-vindas quanto do histórico de cálculos.
    div.style.whiteSpace = "pre-line";

    div.innerText = texto;

    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;
}

// ====================
// ADICIONAR IMAGEM
// ====================

function adicionarImagem(
    src,
    tipo
){

    let chat =
        document.getElementById(
            "chat"
        );

    let div =
        document.createElement(
            "div"
        );

    div.className = tipo;

    let img =
        document.createElement(
            "img"
        );

    img.src = src;

    div.appendChild(img);

    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;
}

// ====================
// COMANDOS
// ====================

function enviarComando(cmd){

    document.getElementById(
        "mensagem"
    ).value = cmd;

    enviar();
}

// ====================
// ENTER
// ====================

document
.getElementById("mensagem")
.addEventListener(
    "keypress",
    function(e){

        if(e.key==="Enter"){
            enviar();
        }

    }
);

// ====================
// MENSAGEM DE BOAS-VINDAS
// ====================

// Aparece assim que a página carrega, sem precisar chamar a API —
// deixa claro pro usuário o que o bot sabe fazer, sem gastar cota do Gemini.
window.addEventListener("DOMContentLoaded", function () {

    adicionarMensagem(
        "Oi! Eu sou o Genius IA 🤖\n\n" +
        "Posso te ajudar com:\n" +
        "💬 Conversar e tirar dúvidas de programação\n" +
        "🧮 Fazer contas (ex: \"10 dividido por 2\")\n" +
        "🎮 Jogar de adivinhar o número (clique em Jogar)\n" +
        "🖼️ Analisar uma imagem que você enviar\n" +
        "📜 Mostrar o histórico de cálculos (clique em Histórico)",
        "bot"
    );

});