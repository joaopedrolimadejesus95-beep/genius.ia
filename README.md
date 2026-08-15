# 🤖 Genius IA

Chatbot web feito com Flask e a API do Gemini (Google), com detecção de intenção para conversar livremente, resolver cálculos, jogar um jogo de adivinhação e analisar imagens.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

## ✨ Funcionalidades

- 💬 **Conversa livre** — tira dúvidas e conversa com você usando a API do Gemini, com foco em ajudar estudantes de programação
- 🧮 **Calculadora por texto** — entende cálculos escritos em linguagem natural (ex: "10 dividido por 2", "5 + 3")
- 🎮 **Jogo de adivinhação** — o bot pensa em um número de 1 a 100 e você tenta adivinhar
- 📜 **Histórico** — guarda os cálculos feitos durante a sessão
- 🖼️ **Análise de imagem** — envie uma imagem e peça pro bot descrever ou analisar

Cada usuário tem seu próprio estado (jogo, histórico) isolado por sessão — várias pessoas podem usar o chat ao mesmo tempo sem interferir uma na outra.

## 🛠️ Tecnologias

- **Backend:** Python, Flask
- **IA:** [google-genai](https://pypi.org/project/google-genai/) (SDK oficial do Gemini)
- **Frontend:** HTML, CSS, JavaScript puro
- **Imagens:** Pillow (PIL)

## 📦 Como rodar localmente

### Pré-requisitos
- Python 3.10 ou superior
- Uma chave de API do Gemini ([gerar aqui](https://aistudio.google.com/apikey))

### Passo a passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/joaopedrolimadejesus95-beep/genius.ia.git
   cd genius.ia
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz do projeto com:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   FLASK_SECRET_KEY=uma_string_aleatoria_grande
   ```
   > Gere uma `FLASK_SECRET_KEY` segura com: `python -c "import secrets; print(secrets.token_hex(32))"`

4. Rode o servidor:
   ```bash
   python app.py
   ```

5. Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador.

## 📁 Estrutura do projeto

```
genius.ia/
├── app.py              # Backend Flask: rotas, lógica de intenção, integração com o Gemini
├── requirements.txt    # Dependências do projeto
├── templates/
│   └── index.html      # Página do chat
└── static/
    ├── script.js        # Lógica do front-end (envio de mensagens, exibição do chat)
    └── style.css         # Estilos visuais
```

## 🧠 Como funciona

O backend detecta a intenção de cada mensagem antes de decidir o que fazer:

1. Contém "jogar"? → inicia o jogo de adivinhação
2. Contém "histórico"? → mostra os cálculos feitos na sessão
3. Casa com um padrão de cálculo (`número operador número`)? → calcula e retorna o resultado
4. Nenhum dos anteriores → envia a mensagem para o Gemini responder livremente

## 🔒 Segurança

- O arquivo `.env` (com as chaves de API) nunca é versionado — está listado no `.gitignore`
- O tamanho de upload de imagem é limitado a 5MB
- O modo debug do Flask é controlado por variável de ambiente, desligado por padrão

## 🚧 Próximos passos

- [ ] Testes automatizados para as funções de cálculo
- [ ] Deploy em produção (Render/Railway)
- [ ] Melhorar a interface visual

---

Projeto feito para fins de aprendizado e portfólio.
