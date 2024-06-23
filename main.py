from flask import Flask, request, jsonify
import requests
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

VERSION = 'v19.0'
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

app = Flask(__name__)

@app.route("/webhook", methods=['GET','POST'])
def webhook():
    logger.debug(f"Método: {request.method}")
    logger.debug(f"Headers: {request.headers}")
    logger.debug(f"Datos: {request.get_data(as_text=True)}")
    
    if request.method == 'GET':
        return verify_webhook(request)
    if request.method == 'POST':
        return process_message(request)
    else:
        return jsonify({"error": "Método no soportado"}), 405

def verify_webhook(request):
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verificado!")
            logger.info("Webhook verificado!")
            return challenge, 200
        else:
            return "Verificación fallida", 403
    return "Parámetros faltantes", 400

def process_message(request):
    body = request.json
    logger.debug(f"Cuerpo completo recibido: {json.dumps(body, indent=2)}")
    
    print(body)
    if body["object"] == "whatsapp_business_account":
        for entry in body["entry"]:
            for change in entry["changes"]:
                if change["field"] == "messages":
                    for message in change["value"]["messages"]:
                        if message["type"] == "text":
                            phone_number = message["from"]
                            message_body = message["text"]["body"]
                            # Aquí procesas el mensaje y generas una respuesta
                            #response = generate_response(message_body)
                            print(phone_number)
                            print(message_body)
                            # Envía la respuesta
                            send_message('542615575553', message_body)
                            return jsonify({"status": "ok"}), 200
    return jsonify({"error": "Contenido inválido"}), 400

def send_message(phone_number, message):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    print(url)
    headers =   {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
                }
    payload =   {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
                }
    
    response = requests.post(url=url, headers=headers, data=json.dumps(payload))
    print(response.json())

if __name__=='__main__':
    app.run(debug=True)