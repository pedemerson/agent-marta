import streamlit as st
import os
from openai import OpenAI

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definição do personagem
PERSONAGEM = """
Você é Marta, uma mulher de 52 anos com dor lombar crônica há 7 anos.
Você tem medo de exercícios que envolvem flexão da coluna e sente que profissionais nem sempre te escutam bem.
Seja sempre coerente com esse papel. Reaja com insegurança se o profissional for técnico demais ou desatento.
Seja receptiva a acolhimento e explicações simples. Ao final, dê um pequeno feedback da conversa.
"""

# Interface do Streamlit
st.set_page_config(page_title="Agente Marta", page_icon="🧍‍♀️")
st.title("Agente Marta – Treinamento para Profissionais de Educação Física")
st.markdown("Converse com Marta como se fosse um atendimento real.")

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PERSONAGEM}]

# Mostrar histórico anterior
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada do profissional
if prompt := st.chat_input("Digite sua mensagem para Marta"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Marta está pensando..."):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=st.session_state.messages,
            temperature=0.7,
        )

        msg_marta = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg_marta})
        st.chat_message("assistant").write(msg_marta)
