from locust import HttpUser, TaskSet, task, between

class ShopFlow(TaskSet):
    def on_start(self):
        creds = {"username": "hamadadmin", "password": "securepassword"}

        # Pick the right content-type for the target environment
        if getattr(self.user, "login_format", "json") == "form":
            # Traditional VM -‐> application/x-www-form-urlencoded
            self.client.post("/login", data=creds, name="login_form")
        else:
            # K8s microservices -‐> application/json
            self.client.post("/login", json=creds, name="login_json")

    @task(2)
    def view_products(self):
        self.client.get("/")

    @task(1)
    def add_to_cart(self):
        self.client.post("/cart/add/1")

    @task(1)
    def checkout(self):
        self.client.post("/cart/checkout")


class MonolithUser(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 5)
    tasks = [ShopFlow]
    login_format = "form"           


#class MicroUser(HttpUser):
#    host = "http://shop.example.com"  # Istio Ingress
#    wait_time = between(1, 5)
#    tasks = [ShopFlow]
#    login_format = "json"            # default, could be omitted
