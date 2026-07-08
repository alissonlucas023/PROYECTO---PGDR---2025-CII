import pika
import json
import time
import datetime

print("🐰 Consumidor RabbitMQ iniciado, esperando órdenes...")

# Conexión a RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declarar la cola
channel.queue_declare(queue='ordenes', durable=True)

# Función que procesa cada orden
def procesar_orden(ch, method, properties, body):
    orden = json.loads(body)
    print(f"\n{'='*45}")
    print(f"📦 Nueva orden recibida:")
    print(f"   Orden ID  : {orden['orden_id']}")
    print(f"   Items     : {orden['items']}")
    print(f"   Total     : ${orden['total']}")
    print(f"   Hora      : {orden['hora']}")
    print(f"   Productos comprados:")
    for producto in orden['productos']:
        print(f"      🛒 {producto}")
    print(f"{'='*45}")
    
    time.sleep(1)
    
    print(f"✅ Orden {orden['orden_id']} procesada exitosamente!")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Configurar consumidor
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ordenes', on_message_callback=procesar_orden)

# Empezar a escuchar
channel.start_consuming()