"""
App ultra-mínima para Vercel - Solo FastAPI básico
"""
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Ultra minimal working"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"test": "working", "framework": "fastapi"}

@app.get("/env-test")
def env_test():
    return {
        "has_database_url": bool(os.getenv("DATABASE_URL")),
        "has_app_secret": bool(os.getenv("APP_SECRET_KEY")),
        "has_jwt_secret": bool(os.getenv("JWT_SECRET_KEY")),
        "app_env": os.getenv("APP_ENV", "NOT_SET"),
        "total_env_vars": len(os.environ)
    }
