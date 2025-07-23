import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://auth_user:auth123@auth-db/auth_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
API_KEY = os.getenv("API_KEY", "438b5f7a-7136-4faa-88f7-427f4c940529")
