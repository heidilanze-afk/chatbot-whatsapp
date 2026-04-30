from flask import Flask, request
from groq import Groq
import requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ZAPI_INSTANCE = os.environ.get("ZAPI_INSTANCE")
ZAPI_TOKEN = os.environ.get("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)

base_de_conhecimento = """
Somos a Loja XYZ. Vendemos roupas femininas.
Horário: segunda a sábado, 9h às 18h.
Frete grátis para compras acima de R$200.
Prazo de entrega: 3 a 7 dias úteis.
Trocas aceitas em até 30 dias com nota fiscal.
"""

def gerar_resposta_ia(pergunta):
    resposta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"Você é um atendente simpático. Use apenas: {base_de_conhecimento}. Se não souber, diga que vai verificar."},
            {"role": "user", "content": pergunta}
        ]
    )
    return resposta.choices[0].message.content

def enviar_whatsapp(numero, mensagem):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    payload = {"phone": numero, "message": mensagem}
    requests.post(url, json=payload, headers=headers)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and "phone" in data and "text" in data:
        numero = data["phone"]
        mensagem = data["text"]["message"]
        resposta = gerar_resposta_ia(mensagem)
        enviar_whatsapp(numero, resposta)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
