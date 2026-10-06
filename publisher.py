import json
import pika


RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "sismos"


def publicar_sismo(sismo_id, latitud, longitud):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )

    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="fanout"
    )

    evento = {
        "id": sismo_id,
        "latitud": latitud,
        "longitud": longitud
    }

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key="",
        body=json.dumps(evento)
    )

    print("Evento publicado:")
    print(json.dumps(evento, indent=4))

    connection.close()


if __name__ == "__main__":
    publicar_sismo(
        "sismo-001",
        -33.036,
        -71.629
    )
