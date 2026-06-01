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

    let resposta =
        await fetch(
            "http://127.0.0.1:5000/chat",
            {
                method:"POST",
                body:formData
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