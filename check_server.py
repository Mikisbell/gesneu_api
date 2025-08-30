import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "¡Servidor de prueba funcionando correctamente!"}

if __name__ == "__main__":
    uvicorn.run("check_server:app", host="0.0.0.0", port=8001, reload=True)
