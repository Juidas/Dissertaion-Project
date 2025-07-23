"""
locustfile.py
--------------
One file, two user classes:

  • MonolithUser  → tests the traditional Windows/Flask VM
  • MicroUser     → tests the Istio-fronted micro-services stack

Run examples
------------

# 150 users, 25 rps spawn, 10 min, traditional
locust -f locustfile.py --class-name MonolithUser \
       -u 150 -r 25 -t 10m --headless --csv monolith_S1

# 150 users, micro-services
locust -f locustfile.py --class-name MicroUser \
       -u 150 -r 25 -t 10m --headless --csv micro_S1
"""

from random import randint
from locust import HttpUser, TaskSet, task, between


# ---------- SHARED USER JOURNEY ----------
class ShopFlow(TaskSet):
    """
    * Logs in once per simulated user.
    * Browses products twice as often as it adds to cart or checks out.
    """

    def on_start(self):
        creds = {"username": "hamadadmin", "password": "securepassword"}

        if self.user.env == "micro":
            # Micro-services → JSON login, returns JWT
            r = self.client.post("/auth/login", json=creds, name="login_json")
            if r.status_code == 200:
                token = r.json().get("access_token") or r.json().get("token")
                if token:
                    self.client.headers.update({"Authorization": f"Bearer {token}"})
            else:
                r.failure("login failed (micro)")
        else:
            # Monolith → form login, session cookie
            self.client.post("/login", data=creds, name="login_form")

    # ---- main tasks ----
    @task(2)
    def view_products(self):
        self.client.get("/products/", name="view_products")

    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 3)  # simple variability
        if self.user.env == "micro":
            payload = {"product_id": product_id, "quantity": 2}
            self.client.post("/cart/add", json=payload, name="add_to_cart_json")
        else:
            self.client.post(f"/cart/add/{product_id}",
                             name="add_to_cart_path")

    @task(1)
    def checkout(self):
        path = "/orders/checkout" if self.user.env == "micro" else "/cart/checkout"
        self.client.post(path, name="checkout")


# ---------- ENV-SPECIFIC WRAPPERS ----------
#class MonolithUser(HttpUser):
#    host = "http://win-vm.example.local"   # ⬅️ replace with VM address
#    wait_time = between(1, 5)
#    tasks = [ShopFlow]
#    env = "monolith"


class MicroUser(HttpUser):
    host = "http://hamad-wn:30663"         # ⬅️ Istio Ingress/GW host:port
    wait_time = between(1, 5)
    tasks = [ShopFlow]
    env = "micro"

