import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.categorias import router as categorias_router
from routes.productos import router as productos_router
from routes.pedidos import router as pedidos_router
from routes.usuarios import router as usuarios_router
from routes.envios import router as envios_router
from services.simulador_envios import ejecutar_simulador


@asynccontextmanager
async def lifespan(app: FastAPI):
    intervalo = int(os.getenv("ENVIO_INTERVALO_SEGUNDOS", "30"))
    tarea_simulador = asyncio.create_task(ejecutar_simulador(intervalo))
    try:
        yield
    finally:
        tarea_simulador.cancel()
        try:
            await tarea_simulador
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173", # Puerto por defecto de Vite
    # Puedes agregar otros si tu frontend cambia de puerto
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(pedidos_router)
app.include_router(usuarios_router)
app.include_router(envios_router)


@app.get("/")
def home():
    return {
        "message": "Velandiax API"
    }
