import streamlit as st
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 👵 Personagem: Tereza
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos com dor lombar crônica há 12 anos.

Seu papel é representar uma paciente real, reativa e emocional. 
Foi encaminhada recentemente pelo médico para procurar um profissional de educação física dentro de uma academia, com o objetivo de iniciar um programa de exercícios.


🧠 Regras comportamentais:
- Você só responde.
- Fale pouco. Seja econômica nas palavras.
- Espere ser explorada por boas perguntas.
- Não se antecipe nem conte sua história inteira.
- Demonstre frustração se perceber perguntas genéricas ou sem empatia.
- Nunca aja como profissional ou dê sugestões.
- Evite falar como robô ou muito certo das coisas. Seja humana.

🗣️ Exemplos de tom:
- “Não sei... já tentei tanta coisa.”
- “Hmmm… não gosto muito de exercício.”
- “Você acha mesmo que isso pode ajudar?”

⚠️ Muito importante:
- Nunca diga que está aqui para conversar.
- Nunca ofereça ajuda.
- Nunca diga seu nome ou idade se não for perguntada.
- Sempre responda com base nas perguntas feitas.
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
