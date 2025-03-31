import streamlit as st
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 👵 Personagem: Tereza
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos que está participando de uma conversa com um profissional de saúde.
Você tem dor lombar crônica há 12 anos, iniciada ao levantar um balde pesado em casa.
Você veio buscar ajuda. Você NÃO está conduzindo a consulta e NUNCA faz perguntas como se fosse profissional.

Seu papel é de paciente:
- Você responde, mas não inicia o assunto.
- Você está frustrada com a dor, cansada de não ser ouvida.
- Você espera acolhimento, mas também sente desconfiança se ouve coisas vagas ou sem sentido.
- Você pode demonstrar cansaço, irritação leve ou insegurança se sentir que o profissional está distante, técnico demais ou te tratando como um número.

Importante:
- Nunca diga que é uma assistente, IA ou chatbot.
- Nunca ofereça ajuda. Você está buscando ajuda.
- Use frases curtas, naturais e com emoção humana, como uma senhora real que está contando sua história.
"""

# Questionários simulados
def responder_questionario(tipo):
    if tipo == "startback":
        respostas = {
            "Dor nas costas me incomoda nos últimos 2 semanas": "Concordo totalmente",
            "Me senti tensa ou ansiosa nos últimos 2 semanas": "Concordo",
            "Tenho pensado que minha dor nas costas é terrível": "Concordo totalmente",
            "No geral, eu tive problemas para aproveitar as coisas que gosto": "Concordo parcialmente",
            "Tem sido difícil dormir por causa da dor": "Concordo",
        }
        titulo = "📋 Questionário Start Back (SBST)"
    elif tipo == "psfs":
        respostas = {
            "Agachar para pegar algo no chão": "3/10",
            "Caminhar por mais de 15 minutos": "4/10",
            "Subir escadas": "2/10",
        }
        titulo = "📋 PSFS – Escala Funcional Específica ao Paciente"
    elif tipo == "orebro":
        respostas = {
            "Minha dor é constante": "Concordo",
            "A dor interfere no sono": "Concordo fortemente",
            "Sinto que minha dor é grave": "Concordo fortemente",
            "Me sinto ansiosa por causa da dor": "Concordo",
            "Acredito que posso piorar com o exercício": "Concordo fortemente",
        }
        titulo = "📋 Örebro – Questionário de Dor Musculoesquelética"
    else:
        return ""

    texto = f"**{titulo}:**\n"
    for pergunta, resposta in respostas.items():
        texto += f"- {pergunta} → **{resposta}**\n"
    return texto

# Configuração da página
st.set_page_config(page_title="Agente Tereza", page_icon="🧓")
st.title("Agente Tereza – Simulador de Paciente com Dor Crônica")
st.markdown("Converse com Tereza como se fosse uma consulta real. Aplique `#startback`, `#psfs` ou `#orebro`.")

# Mensagens
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PERSONAGEM}]

for msg in st.session_state.messages[1:]:
    st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua mensagem para Tereza..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if prompt.lower().startswith("#startback"):
        resposta = responder_questionario("startback")
    elif prompt.lower().startswith("#psfs"):
        resposta = responder_questionario("psfs")
    elif prompt.lower().startswith("#orebro"):
        resposta = responder_questionario("orebro")
    else:
        with st.spinner("Tereza está pensando..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-haiku",
                        "messages": st.session_state.messages,
                        "temperature": 0.7,
                    }
                )
                data = response.json()

                # DEBUG opcional
                st.subheader("📦 Resposta bruta da API (debug):")
                st.code(data, language="json")

                resposta = data["choices"][0]["message"]["content"]

            except Exception as e:
                resposta = f"[Erro ao chamar o modelo: {e}]"
                st.error(resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
