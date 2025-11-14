"""
App ultra-mínima para Vercel - Solo FastAPI básico
"""
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
