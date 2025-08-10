import os

class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service.product-service.svc.cluster.local/products/")