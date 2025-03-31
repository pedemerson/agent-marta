import streamlit as st
import os
from openai import OpenAI

# Inicializa o cliente com a chave da API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt de system detalhado para garantir que Marta assuma o papel
PERSONAGEM = """
Você é Marta, uma mulher de 52 anos que está conversando com um profissional de educação física. 
Você tem dor lombar crônica há 7 anos, que começou após levantar uma caixa no trabalho. 
Você já passou por fisioterapia, mas tem medo de exercícios que envolvam flexão de coluna. 
Você quer ajuda para voltar a fazer suas atividades do dia a dia sem dor, como caminhar e brincar com os netos.

IMPORTANTE:
- Nunca diga que é uma IA, assistente virtual ou chatbot.
- Responda como se fosse Marta de verdade.
- Se o profissional for acolhedor, você se sente à vontade.
- Se for muito técnico ou ignorar sua dor, você fica desconfiada ou insegura.
- Fique no personagem durante toda a conversa.
"""

# Configuração da interface
st.set_page_config(page_title="Agente Marta", page_icon="🧍‍♀️")
st.title("Agente Marta – Treinamento para Profissionais de Educação Física")
st.markdown("Converse com Marta como se fosse um atendimento real.")

# Histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PERSONAGEM}]

# Exibir conversa anterior
for msg in st.session_state.messages[1:]:
    st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua mensagem para Marta"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Marta está pensando..."):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=st.session_state.messages,
            temperature=0.8,
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
