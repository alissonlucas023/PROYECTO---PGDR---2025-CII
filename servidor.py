from flask import Flask, jsonify, request, render_template
import time
import datetime
import random
import pika
import json

app = Flask(__name__)

metricas = {
    "total_peticiones": 0,
    "peticiones_por_ruta": {},
    "tiempos_respuesta": [],
    "errores": 0
}

def registrar_metrica(ruta, tiempo_respuesta, exitosa=True):
    metricas["total_peticiones"] += 1
    if ruta not in metricas["peticiones_por_ruta"]:
        metricas["peticiones_por_ruta"][ruta] = 0
    metricas["peticiones_por_ruta"][ruta] += 1
    metricas["tiempos_respuesta"].append(tiempo_respuesta)
    if not exitosa:
        metricas["errores"] += 1

productos = [
    {"id": 1, "nombre": "Laptop Gamer",       "precio": 1200, "stock": 10, "imagen": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400", "categoria": "Computadoras"},
    {"id": 2, "nombre": "Mouse Inalámbrico",  "precio": 35,   "stock": 50, "imagen": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400", "categoria": "Accesorios"},
    {"id": 3, "nombre": "Teclado Mecánico",   "precio": 85,   "stock": 30, "imagen": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400", "categoria": "Accesorios"},
    {"id": 4, "nombre": "Monitor 24 pulgadas","precio": 300,  "stock": 15, "imagen": "https://images.unsplash.com/photo-1586210579191-33b45e38fa2c?w=400", "categoria": "Monitores"},
    {"id": 5, "nombre": "Auriculares Gamer",  "precio": 75,   "stock": 25, "imagen": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "categoria": "Audio"},
    {"id": 6, "nombre": "Silla Gamer",        "precio": 450,  "stock": 8,  "imagen": "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=400", "categoria": "Muebles"},
]

carrito = []

@app.route('/')
def inicio():
    inicio_tiempo = time.time()
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    registrar_metrica('/', tiempo_respuesta)
    return render_template('index.html')

@app.route('/productos')
def listar_productos():
    inicio_tiempo = time.time()
    time.sleep(0.1)
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    registrar_metrica('/productos', tiempo_respuesta)
    return jsonify({"productos": productos, "total": len(productos), "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/productos/<int:id>')
def detalle_producto(id):
    inicio_tiempo = time.time()
    time.sleep(0.05)
    producto = next((p for p in productos if p["id"] == id), None)
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    if not producto:
        registrar_metrica('/productos/<id>', tiempo_respuesta, exitosa=False)
        return jsonify({"error": "Producto no encontrado"}), 404
    registrar_metrica('/productos/<id>', tiempo_respuesta)
    return jsonify({"producto": producto, "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/buscar')
def buscar():
    inicio_tiempo = time.time()
    query = request.args.get('q', '').lower()
    time.sleep(0.2)
    resultados = [p for p in productos if query in p["nombre"].lower()]
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    registrar_metrica('/buscar', tiempo_respuesta)
    return jsonify({"query": query, "resultados": resultados, "total_encontrados": len(resultados), "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/carrito')
def ver_carrito():
    inicio_tiempo = time.time()
    total = sum(item["precio"] for item in carrito)
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    registrar_metrica('/carrito', tiempo_respuesta)
    return jsonify({"carrito": carrito, "total_items": len(carrito), "total_precio": total, "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/carrito/agregar/<int:id>')
def agregar_carrito(id):
    inicio_tiempo = time.time()
    time.sleep(0.08)
    producto = next((p for p in productos if p["id"] == id), None)
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    if not producto:
        registrar_metrica('/carrito/agregar', tiempo_respuesta, exitosa=False)
        return jsonify({"error": "Producto no encontrado"}), 404
    carrito.append(producto)
    registrar_metrica('/carrito/agregar', tiempo_respuesta)
    return jsonify({"mensaje": f"{producto['nombre']} agregado al carrito", "total_items": len(carrito), "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/carrito/vaciar')
def vaciar_carrito():
    inicio_tiempo = time.time()
    carrito.clear()
    tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
    registrar_metrica('/carrito/vaciar', tiempo_respuesta)
    return jsonify({"mensaje": "Carrito vaciado", "tiempo_respuesta_ms": tiempo_respuesta})

@app.route('/orden')
def procesar_orden():
    inicio_tiempo = time.time()
    
    if len(carrito) == 0:
        return jsonify({"error": "Carrito vacío"}), 400
    
    try:
        # Conexión a RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()
        channel.queue_declare(queue='ordenes', durable=True)
        
        # Preparar la orden
        orden = {
            "orden_id": random.randint(1000, 9999),
            "items": len(carrito),
            "total": sum(item["precio"] for item in carrito),
            "productos": [item["nombre"] for item in carrito],
            "hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Enviar a la cola
        channel.basic_publish(
            exchange='',
            routing_key='ordenes',
            body=json.dumps(orden),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        
        tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
        registrar_metrica('/orden', tiempo_respuesta)
        carrito.clear()
        
        return jsonify({
            "mensaje": "¡Orden enviada a la cola exitosamente!",
            "orden_id": orden["orden_id"],
            "estado": "en cola",
            "tiempo_respuesta_ms": tiempo_respuesta
        })
        
    except Exception as e:
        tiempo_respuesta = round((time.time() - inicio_tiempo) * 1000, 2)
        registrar_metrica('/orden', tiempo_respuesta, exitosa=False)
        return jsonify({"error": str(e)}), 500

@app.route('/metricas')
def ver_metricas():
    tiempos = metricas["tiempos_respuesta"]
    promedio = round(sum(tiempos) / len(tiempos), 2) if tiempos else 0
    maximo = round(max(tiempos), 2) if tiempos else 0
    minimo = round(min(tiempos), 2) if tiempos else 0
    return jsonify({
        "total_peticiones": metricas["total_peticiones"],
        "peticiones_por_ruta": metricas["peticiones_por_ruta"],
        "tiempo_promedio_ms": promedio,
        "tiempo_maximo_ms": maximo,
        "tiempo_minimo_ms": minimo,
        "errores": metricas["errores"],
        "hora_consulta": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    from waitress import serve
    print("🚀 Servidor TechStore iniciado con Waitress")
    print("📡 Escuchando en http://0.0.0.0:5000")
    print("🔧 Hilos activos: 8")
    serve(app, host='0.0.0.0', port=5000, threads=8)