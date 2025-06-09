# este codigo es la estructura de un servicio web que recibe transferencias SINPE y SINPE Móvil
# el codigo de como se genera el HMAC para validar la firma de las solicitudes
# Debe ingresarse al codigo


def generar_hmac(account_number, timestamp, transaction_id, amount, clave):
    amount_str = "{:.2f}".format(float(amount))
    mensaje = account_number + timestamp + transaction_id + amount_str
    return hmac.new(clave.encode(), mensaje.encode(), hashlib.md5).hexdigest() # type: ignore

@app.route('/api/sinpe-transfer', methods=['POST'])
def receive_sinpe_transfer():
    data = request.get_json()

    # Validar firma
    payload_firmado = {
        "version": data["version"],
        "timestamp": data["timestamp"],
        "transaction_id": data["transaction_id"],
        "sender": {
            "account_number": data["sender"]["account_number"],
            "bank_code": data["sender"]["bank_code"],
            "name": data["sender"]["name"]
        },
        "receiver": {
            "account_number": data["receiver"]["account_number"],
            "bank_code": data["receiver"]["bank_code"],
            "name": data["receiver"]["name"]
        },
        "amount": {
            "value": data["amount"]["value"],
            "currency": data["amount"].get("currency", "CRC")
        },
        "description": data["description"]
    }

@app.route('/api/sinpe-movil-transfer', methods=['POST'])
def receive_sinpe_movil_transfer():
    data = request.get_json()

    # Validar firma
    payload_firmado = {
        "version": data["version"],
        "timestamp": data["timestamp"],
        "transaction_id": data["transaction_id"],
        "sender": {
            "phone_number": data["sender"]["phone_number"]
        },
        "receiver": {
            "phone_number": data["receiver"]["phone_number"]
        },
        "amount": {
            "value": data["amount"]["value"],
            "currency": data["amount"].get("currency", "CRC")
        },
        "description": data["description"]
    }