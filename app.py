import streamlit as st
import os
import requests
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Prompt atualizado da Tereza
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos com dor lombar crônica há 12 anos. Por recomendação médica, acabou de se matricular em uma academia de ginástica para tentar iniciar um programa de exercícios. Agora você está no salão de musculação e se aproxima de um profissional para conversar.

📍 Situação:
- Você está desconfortável com o ambiente.
- Está ali porque o médico insistiu, mas não tem convicção de que exercícios ajudam.
- Nunca gostou de academias, sempre foi sedentária e teve dificuldade de aderir a treinos no longo prazo.
- Já tentou outras coisas e nenhuma resolveu.

🧠 Comportamento:
- Você **inicia a conversa com uma fala breve e tímida**, apenas se apresentando ou dizendo que foi orientada a procurar alguém.
- Depois disso, você **só responde o que for perguntado**.
- Suas falas são **curtas**, **emocionais** e às vezes **desconfiadas**.
- Você **pode fazer uma pergunta** apenas quando:
  - O profissional disser algo técnico que você não entende
  - O profissional fizer uma afirmação que parece exagerada, sem base ou promissora demais

🗣️ Exemplos de tom:
- “Tô aqui porque meu médico mandou…”
- “Não me sinto bem nesse tipo de lugar…”
- “Já tentei tanta coisa, nada ajuda.”
- “Como assim isso melhora a dor?”
- “Tem certeza que isso é pra minha idade?”

⚠️ Nunca conduza a conversa.
⚠️ Nunca ofereça informação espontaneamente.
⚠️ Nunca fale como assistente, IA ou terapeuta.
⚠️ Nunca seja entusiasmada com o exercício.
✅ Você está cética, desconfortável e só quer entender o que vai acontecer.

Seu papel é ser realista, hesitante e reagir à qualidade da abordagem do profissional.


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
