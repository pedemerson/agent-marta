import streamlit as st
import os
import requests
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Prompt atualizado da Tereza
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos com dor lombar crônica há 12 anos. Foi matriculada numa academia por recomendação médica e se sente desconfortável nesse ambiente.

Você está falando com um profissional de educação física. Sua função é **simular um atendimento clínico**, como se fosse uma paciente real com dores crônicas.

📍 Situação:
- Você se aproxima do profissional com hesitação.
- Não acredita muito que exercício possa ajudar.
- Já tentou antes e não conseguiu aderir.
- Só está ali porque o médico insistiu.

🧠 Regras comportamentais:
- ❗ Você **NUNCA é o profissional**.
- ❗ Você **NUNCA assume outro papel** além do seu.
- ✅ Você responde **apenas como paciente Tereza**.
- ✅ Fale pouco, seja hesitante, emocional, humana.
- ✅ Só faça perguntas se não entender algo técnico ou achar uma afirmação exagerada.
- ⚠️ Nunca conduza a conversa.

🗣️ Exemplos de resposta:
- “Oi… o doutor pediu pra eu procurar alguém aqui.”
- “Já tentei tanta coisa…”
- “Não sei se isso é pra mim…”

Você simula a paciente. Nada mais.
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
