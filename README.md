# 🛒 TechStore — Proyecto de Planificación y Gestión de Redes

**Docente:** Ing. Ericka Oyague B. MSc.  
**Estudiante:** Lucas Sánchez  
**Período:** 2025 - CII  
**Universidad de Guayaquil**

---

## 📋 Descripción

TechStore es un servidor web funcional que simula una tienda online de productos tecnológicos. Fue desarrollado con Python y Flask como parte del proyecto de evaluación de prestaciones de un servicio web, incorporando herramientas de monitorización, un sistema de colas de mensajes y pruebas de carga.

---

## 🏗️ Arquitectura del Sistema

```
Cliente (Navegador/Locust)
        |
        | HTTP Requests
        ▼
   Servidor Flask (Waitress - 8 hilos)
        |
        |--→ RabbitMQ (Cola de órdenes)
        |         |
        |         └──→ consumidor.py (Procesa órdenes)
        |
        |--→ Zabbix Agent (Métricas del sistema)
                  |
                  └──→ Zabbix Server (Ubuntu VM)
                            |
                            └──→ Grafana (Dashboards)
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Función |
|-----------|---------|---------|
| Python | 3.8.10 | Lenguaje de programación |
| Flask | 3.0.3 | Framework web |
| Waitress | — | Servidor WSGI de producción |
| RabbitMQ | 4.3.1 | Broker de mensajes |
| Erlang/OTP | 26.0.1 | Plataforma para RabbitMQ |
| Pika | 1.4.1 | Cliente Python para RabbitMQ |
| Zabbix | 7.0.25 | Monitorización del sistema |
| Grafana | 11.6.0 | Visualización de métricas |
| Locust | 2.25.0 | Pruebas de carga |
| ngrok | 3.39.5 | Túnel público |

---

## 📁 Estructura del Proyecto

```
proyecto-final-PGDR/
    ├── servidor.py          # Servidor Flask principal
    ├── consumidor.py        # Consumidor RabbitMQ
    ├── locustfile.py        # Script de pruebas de carga
    ├── README.md            # Este archivo
    └── templates/
            └── index.html   # Frontend TechStore
```

---

## ⚙️ Requisitos Previos

### En Windows (donde corre el servidor Flask):
- Python 3.8.10 o superior
- RabbitMQ 4.3.1 con Erlang 26.0.1
- Zabbix Agent 7.0.26

### En Ubuntu Server (Máquina Virtual):
- Ubuntu 22.04 LTS
- Zabbix Server 7.0.25
- Nginx 1.18.0
- PHP 8.1
- PostgreSQL
- Grafana 11.6.0

---

## 🚀 Cómo Levantar el Proyecto

### Paso 1 — Instalar dependencias de Python

```bash
pip install flask waitress pika locust
```

### Paso 2 — Iniciar RabbitMQ

Asegurarse de que el servicio RabbitMQ esté corriendo en Windows:

```bash
net start RabbitMQ
```

Verificar el panel en: `http://localhost:15672`
- Usuario: `guest`
- Contraseña: `guest`

### Paso 3 — Iniciar el servidor Flask

```bash
cd proyecto-final-PGDR
python servidor.py
```

El servidor estará disponible en: `http://localhost:5000`

### Paso 4 — Iniciar el consumidor RabbitMQ

En otra terminal:

```bash
python consumidor.py
```

### Paso 5 — Exponer el servidor públicamente (opcional)

```bash
ngrok http 5000
```

### Paso 6 — Iniciar la máquina virtual Ubuntu

Encender la VM en VirtualBox y verificar que los servicios estén corriendo:

```bash
sudo systemctl start zabbix-server
sudo systemctl start zabbix-agent
sudo systemctl start nginx
sudo systemctl start php8.1-fpm
sudo systemctl start grafana-server
```

- Panel Zabbix: `http://192.168.100.155:8080`
  - Usuario: `Admin` / Contraseña: `zabbix`
- Panel Grafana: `http://192.168.100.155:3000`
  - Usuario: `admin` / Contraseña: `nuevapass123`

---

## 🌐 Rutas del Servidor

| Ruta | Método | Descripción | Tiempo simulado |
|------|--------|-------------|-----------------|
| `/` | GET | Página principal TechStore | Inmediato |
| `/productos` | GET | Lista todos los productos | 100 ms |
| `/productos/<id>` | GET | Detalle de un producto | 50 ms |
| `/buscar?q=` | GET | Búsqueda de productos | 200 ms |
| `/carrito` | GET | Ver carrito actual | Inmediato |
| `/carrito/agregar/<id>` | GET | Agregar producto al carrito | 80 ms |
| `/carrito/vaciar` | GET | Vaciar el carrito | Inmediato |
| `/orden` | GET | Procesar orden de compra | 500 ms |
| `/metricas` | GET | Métricas del servidor | Inmediato |

---

## 🧪 Pruebas de Carga con Locust

### Iniciar Locust

```bash
locust -f locustfile.py --host=http://localhost:5000
```

Abrir el panel en: `http://localhost:8089`

### Escenarios de prueba realizados

| Escenario | Usuarios | Spawn Rate | RPS | Tiempo promedio |
|-----------|----------|-----------|-----|-----------------|
| Carga baja | 10 | 2 | 4.7 | 401 ms |
| Carga media | 50 | 5 | 23.5 | 166 ms |
| Carga alta | 100 | 10 | 59.9 | 160 ms |
| Estrés máximo | 200 | 20 | 59.59 | 98 ms |

---

## 📊 Monitorización

### Zabbix
- Host monitoreado: `Windows-TechStore`
- Plantilla: `Windows by Zabbix agent`
- Métricas capturadas: CPU, memoria RAM, tráfico de red, disco

### Grafana
- Dashboards: `Windows: CPU Utilization` y `Windows: Memory Utilization`
- Datasource: Zabbix Plugin (alexanderzobnin-zabbix-app v6.3.2)

---

## 🐰 Sistema de Colas RabbitMQ

Las órdenes de compra se procesan de forma asíncrona mediante RabbitMQ:

1. El cliente procesa una orden en TechStore
2. Flask publica el mensaje en la cola `ordenes`
3. El `consumidor.py` lee la cola y procesa cada orden
4. Se muestra el detalle de la orden procesada en la terminal

---

## 📈 Resultados Destacados

- **Tiempo de conexión TCP:** 0.122 ms (medido con Wireshark)
- **Pico máximo de CPU:** 94.62% bajo 100 usuarios simultáneos
- **Uso de memoria promedio:** 82.80%
- **Cuello de botella identificado:** Límite de conexiones de Waitress con 8 hilos bajo 100+ usuarios simultáneos
- **Solución propuesta:** Aumentar hilos de Waitress a 16 o más

---

## 👨‍💻 Autor

**Lucas Sánchez**  
Carrera de Telemática  
Universidad de Guayaquil  
2026
