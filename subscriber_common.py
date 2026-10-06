import json
import math
import pika
import requests

RADIO_INTERES_KM = 500
API_URL = "http://localhost:8000"


def calcular_distancia(lat1, lon1, lat2, lon2):
    radio_tierra = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radio_tierra * c


def obtener_detalle_sismo(sismo_id):
    try:
        response = requests.get(
            f"{API_URL}/sismos/{sismo_id}",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        print(f"Error HTTP: {response.status_code}")

    except requests.RequestException as error:
        print(f"Error al contactar la API: {error}")

    return None


def iniciar_subscriber(nombre, latitud, longitud):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

    channel = connection.channel()

    channel.exchange_declare(
        exchange="sismos",
        exchange_type="fanout"
    )

    queue_name = f"sismos_{nombre.lower().replace(' ', '_')}"

    channel.queue_declare(queue=queue_name)

    channel.queue_bind(
        exchange="sismos",
        queue=queue_name
    )

    def procesar_evento(ch, method, properties, body):
        evento = json.loads(body)

        distancia = calcular_distancia(
            latitud,
            longitud,
            evento["latitud"],
            evento["longitud"]
        )

        print(f"\nSismo recibido en {nombre}")
        print(f"Distancia: {distancia:.2f} km")

        if distancia < RADIO_INTERES_KM:
            print("Sismo de interés")

            detalle = obtener_detalle_sismo(evento["id"])

            if detalle:
                print(
                    json.dumps(
                        detalle,
                        indent=4,
                        ensure_ascii=False
                    )
                )
        else:
            print("Sismo fuera del radio de interés")

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=procesar_evento,
        auto_ack=False
    )

    print(f"Subscriber {nombre} esperando eventos...")

    channel.start_consuming()
