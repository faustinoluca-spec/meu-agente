from dotenv import load_dotenv
import os
load_dotenv()
import requests
from groq import Groq
from datetime import date
from twilio.rest import Client

GROQ_KEY = os.environ.get("GROQ_KEY")
SERPER_KEY = os.environ.get("SERPER_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_NUMERO = "whatsapp:+14155238886"

NUMEROS = [
    "whatsapp:+5521991845374",
    "whatsapp:+5521996504112","whatsapp:+5511991831244"
]

cliente_groq = Groq(api_key=GROQ_KEY)
cliente_twilio = Client(TWILIO_SID, TWILIO_TOKEN)

FONTES = "site:g1.globo.com OR site:uol.com.br OR site:cnnbrasil.com.br"

CATEGORIAS = [
    {"emoji": "🏛️", "nome": "Política", "busca": f"política Brasil hoje {FONTES}"},
    {"emoji": "💰", "nome": "Economia", "busca": f"economia Brasil hoje {FONTES}"},
    {"emoji": "🗳️", "nome": "Eleições", "busca": f"eleições 2026 Brasil {FONTES}"
    {"emoji": "🎭", "nome": "Cultura", "busca": f"cultura entretenimento Brasil hoje {FONTES}"},},
]

def buscar_noticias(busca):
    print(f"🔍 Buscando: {busca}")
    url = "https://google.serper.dev/news"
    headers = {"X-API-KEY": SERPER_KEY}
    payload = {"q": busca, "gl": "br", "hl": "pt-br", "num": 5}
    resposta = requests.post(url, headers=headers, json=payload)
    noticias = resposta.json().get("news", [])
    texto = ""
    for n in noticias:
        texto += f"- {n['title']} | Fonte: {n['source']}\n"
    return texto

def analisar_noticias(noticias, categoria):
    print(f"🧠 Analisando {categoria}...")
    resposta = cliente_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Você é um analista político sênior com 20 anos de experiência no Brasil.

Com base nas notícias abaixo sobre {categoria}, escreva um briefing detalhado com:

1. PRINCIPAIS FATOS - o que aconteceu, com nomes completos, cargos e partidos
2. CONTEXTO - histórico detalhado de por que isso importa
3. PERSPECTIVAS - como diferentes lados estão interpretando
4. ANÁLISE - o que pode acontecer a seguir

Seja detalhado. Mencione nomes, partidos e cargos.
Cite a fonte de cada fato entre parênteses. Exemplo: (G1), (UOL), (CNN Brasil).
Máximo 3000 caracteres.

Notícias:
{noticias}"""
        }]
    )
    return resposta.choices[0].message.content

def enviar_whatsapp(mensagem, emoji, categoria):
    print(f"📱 Enviando {categoria}...")
    hoje = date.today().strftime("%d/%m/%Y")
    texto_completo = f"{emoji} *{categoria} — {hoje}*\n\n{mensagem}"
    partes = []
    while len(texto_completo) > 1500:
        corte = texto_completo[:1500].rfind("\n")
        if corte == -1:
            corte = 1500
        partes.append(texto_completo[:corte])
        texto_completo = texto_completo[corte:]
    partes.append(texto_completo)
    for numero in NUMEROS:
        for i, parte in enumerate(partes):
            if len(partes) > 1:
                parte = f"({i+1}/{len(partes)}) {parte}"
            cliente_twilio.messages.create(
                body=parte,
                from_=TWILIO_NUMERO,
                to=numero
            )
    print(f"✅ {categoria} enviado em {len(partes)} mensagem(ns)!")

def agente():
    print("🤖 Agente iniciado!")
    for categoria in CATEGORIAS:
        noticias = buscar_noticias(categoria["busca"])
        analise = analisar_noticias(noticias, categoria["nome"])
        enviar_whatsapp(analise, categoria["emoji"], categoria["nome"])
    print("🎉 Todas as mensagens enviadas!")

agente()

