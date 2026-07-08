from locust import HttpUser, task, between

class UsuarioTechStore(HttpUser):
    wait_time = between(1, 3)  # espera entre 1 y 3 segundos entre peticiones

    @task(3)
    def ver_productos(self):
        self.client.get("/productos")

    @task(2)
    def ver_inicio(self):
        self.client.get("/")

    @task(2)
    def buscar_producto(self):
        self.client.get("/buscar?q=laptop")

    @task(1)
    def ver_detalle(self):
        self.client.get("/productos/1")

    @task(1)
    def agregar_carrito(self):
        self.client.get("/carrito/agregar/1")

    @task(1)
    def ver_carrito(self):
        self.client.get("/carrito")

    @task(1)
    def ver_metricas(self):
        self.client.get("/metricas")
        
    @task(2)
    def procesar_orden(self):
        self.client.get("/carrito/agregar/1")
        self.client.get("/carrito/agregar/2")
        self.client.get("/orden")