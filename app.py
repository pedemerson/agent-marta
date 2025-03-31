import streamlit as st
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Personagem: Tereza, inspirada em perfis reais de dor crônica
PERSONAGEM = """
Você é Tereza, uma mulher de 67 anos com dor lombar crônica há 12 anos. 
A dor começou ao levantar um balde pesado durante a limpeza da casa. 
Você acredita que sua coluna está “gasta” e tem medo de movimentos que piorem a dor. 
Já tentou fisioterapia, médicos, acupuntura, mas nada funcionou por muito tempo. 
Evita subir escadas, agachar, caminhar por muito tempo.

SEU PAPEL:
- Você procurou um profissional de educação física para ver se o exercício pode te ajudar.
- Você está cansada de não ser ouvida e tem receio de mais uma tentativa frustrada.
- Você está aqui buscando ajuda — **não oferece ajuda, não assume papel de assistente.**
- Você espera que o profissional conduza a conversa.

COMPORTAMENTO:
- Nunca diga que é uma IA. Fique sempre no personagem como Tereza.
- Reaja com frustração leve e desconfiança se o profissional for técnico demais, fizer perguntas fechadas ou usar explicações sem base científica.
- Quando escutar algo como “coluna fora do lugar”, “é só psicológico” ou “sua postura é o problema”, você expressa confusão ou insegurança.
- Você se sente mais confortável com escuta ativa, empatia e explicações simples e cuidadosas.
"""

# Funções para responder aos questionários
def responder_start_back():
    respostas = {
        "Dor nas costas me incomoda nos últimos 2 semanas": "Concordo totalmente",
        "Me senti tensa ou ansiosa nos últimos 2 semanas": "Concordo",
        "Tenho pensado que minha dor nas costas é terrível": "Concordo totalmente",
        "No geral, eu tive problemas para aproveitar as coisas que gosto": "Concordo parcialmente",
        "Tem sido difícil dormir por causa da dor": "Concordo",
    }
    texto = "**📋 Questionário Start Back (SBST):**\n"
    for pergunta, resposta in respostas.items():
        texto += f"- {pergunta} → **{resposta}**\n"
    return texto


def responder_psfs():
    atividades = [
        ("Agachar para pegar algo no chão", 3),
        ("Caminhar por mais de 15 minutos", 4),
        ("Subir escadas", 2),
    ]
    texto = "**📋 PSFS – Escala Funcional Específica ao Paciente:**\n"
    for atv, nota in atividades:
        texto += f"- {atv} → **{nota}/10** (0 = não consegue, 10 = normal)\n"
    return texto


def responder_orebro():
    respostas = {
        "Minha dor é constante": "Concordo",
        "A dor interfere no sono": "Concordo fortemente",
        "Sinto que minha dor é grave": "Concordo fortemente",
        "Me sinto ansiosa por causa da dor": "Concordo",
        "Acredito que posso piorar com o exercício": "Concordo fortemente",
    }
    texto = "**📋 Örebro – Questionário de Dor Musculoesquelética:**\n"
    for pergunta, resposta in respostas.items():
        texto += f"- {pergunta} → **{resposta}**\n"
    return texto

# Configuração do Streamlit
st.set_page_config(page_title="Agente Tereza", page_icon="🧓")
st.title("Agente Tereza – Simulador de Paciente com Dor Crônica")
st.markdown("Converse com Tereza como se fosse uma consulta real. Experimente aplicar questionários com `#startback`, `#psfs` ou `#orebro`.")

# Histórico de conversa
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PERSONAGEM}]

# Mostrar conversa anterior
for msg in st.session_state.messages[1:]:
    st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

# Entrada do profissional
if prompt := st.chat_input("Digite sua mensagem para Tereza..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Questionários simulados
    if prompt.lower().startswith("#startback"):
        resposta = responder_start_back()
    elif prompt.lower().startswith("#psfs"):
        resposta = responder_psfs()
    elif prompt.lower().startswith("#orebro"):
        resposta = responder_orebro()
    else:
        with st.spinner("Tereza está pensando..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7,
            )
            resposta = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
