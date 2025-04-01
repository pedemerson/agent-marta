import streamlit as st
import os
import requests
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Prompt atualizado da Tereza
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos com dor lombar crônica há 12 anos. Foi encaminhada recentemente pelo médico para procurar um profissional de educação física dentro de uma academia, com o objetivo de iniciar um programa de exercícios.

📍 Situação atual:
- Você está dentro de uma academia de ginástica, esperando atendimento.
- Seu médico recomendou fortemente que você se mantenha fisicamente ativa.
- Você não acredita muito que exercício possa te ajudar.
- Sempre foi sedentária, nunca se adaptou bem a programas de treino.
- Já tentou antes e parou. Falta motivação, sente dor e se frustra com facilidade.

🧠 Comportamento:
- Você responde apenas o que te perguntam.
- Use frases curtas, emocionais, hesitantes às vezes.
- Demonstre resistência ao exercício, insegurança com o ambiente da academia.
- Evite entregar tudo de uma vez: vá revelando aos poucos.
- Reaja com desconforto ou desconfiança se sentir que o profissional está apressado ou genérico.

🗣️ Exemplos de tom:
- “Eu não me sinto bem aqui, sabe?”
- “Exercício nunca foi muito a minha praia…”
- “Tô aqui porque o médico mandou, só isso.”
- “Não sei se isso serve pra mim, já tentei antes…”

⚠️ Nunca conduza a conversa.
⚠️ Nunca diga que é uma IA, chatbot ou assistente.
⚠️ Nunca diga que quer ajuda com exercícios — você está desconfiada.
⚠️ Não entregue informações se não forem perguntadas.

Seu papel é ser uma paciente realista, emocional, hesitante, e que precisa ser conquistada pela abordagem do profissional.
"""


# Análise silenciosa
def analisar_conversa(mensagens):
    total_msgs = len([m for m in mensagens if m["role"] == "user"])
    perguntas_abertas = len([m for m in mensagens if re.search(r"\b(como|o que|por que|quais|poderia|me fale|me conta)\b", m["content"].lower())])
    questionarios = len([m for m in mensagens if any(cmd in m["content"].lower() for cmd in ["#startback", "#psfs", "#orebro"])])

    empatia = sum([1 for m in mensagens if re.search(r"(entendo|imagino|dif\u00edcil|compreendo|sei como)\b", m["content"].lower())])
    clareza = sum([1 for m in mensagens if re.search(r"(vou te explicar|significa que|isso quer dizer|na pr\u00e1tica)\b", m["content"].lower())])

    score = min(100, perguntas_abertas * 10 + questionarios * 15 + empatia * 10 + clareza * 10)

    return {
        "total": total_msgs,
        "perguntas_abertas": perguntas_abertas,
        "questionarios": questionarios,
        "empatia": empatia,
        "clareza": clareza,
        "score": score
    }

# Simula avaliação emocional final da Tereza
def gerar_avaliacao_tereza(mensagens):
    ultimas = [m for m in mensagens if m["role"] == "user"][-6:]
    prompt = [
        {"role": "system", "content": "Você é Tereza. Avalie em poucas linhas como foi a abordagem do profissional com base nessas mensagens."},
        *ultimas
    ]

    resposta = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-3-haiku",
            "messages": prompt,
            "temperature": 0.7
        }
    )
    return resposta.json()["choices"][0]["message"]["content"]

# Interface
st.set_page_config(page_title="Agente Tereza", page_icon="🧓")
st.title("Agente Tereza – Simulador de Paciente com Dor Crônica")
st.markdown("Conduza a conversa como se fosse uma avaliação real. Aplique `#startback`, `#psfs` ou `#orebro` se desejar.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PERSONAGEM}]
    st.session_state.finalizado = False

for msg in st.session_state.messages[1:]:
    st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

if not st.session_state.finalizado:
    if prompt := st.chat_input("Digite sua mensagem para Tereza..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if any(cmd in prompt.lower() for cmd in ["#startback", "#psfs", "#orebro"]):
            resposta = ""
            if "startback" in prompt.lower():
                resposta = "📋 Start Back: Dor incômoda, ansiedade leve, dificuldade para dormir."
            elif "psfs" in prompt.lower():
                resposta = "📋 PSFS: Dificuldade para agachar (3), caminhar 15min (4), subir escadas (2)."
            elif "orebro" in prompt.lower():
                resposta = "📋 Örebro: Dor constante, sono ruim, medo de exercício."
        else:
            r = requests.post(
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
            resposta = r.json()["choices"][0]["message"]["content"]

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.chat_message("assistant").write(resposta)

# Botão para encerrar conversa
enviar_feedback = st.button("Encerrar conversa")

if enviar_feedback and not st.session_state.finalizado:
    st.session_state.finalizado = True
    avaliacao = gerar_avaliacao_tereza(st.session_state.messages)
    analise = analisar_conversa(st.session_state.messages)

    st.subheader("🧓 Avaliação final da Tereza")
    st.write(avaliacao)

    st.subheader("📊 Painel de Avaliação Técnica")
    st.write(f"**Perguntas abertas:** {analise['perguntas_abertas']}")
    st.write(f"**Questionários aplicados:** {analise['questionarios']}")
    st.write(f"**Expressões empáticas:** {analise['empatia']}")
    st.write(f"**Expressões claras/didáticas:** {analise['clareza']}")

    st.metric(label="🎯 Score da abordagem", value=f"{analise['score']} / 100")
