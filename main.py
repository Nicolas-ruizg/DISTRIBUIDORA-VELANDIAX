from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.categorias import router as categorias_router
from routes.productos import router as productos_router
from routes.pedidos import router as pedidos_router



app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(pedidos_router)


@app.get("/")
def home():
    return {
        "message": "Velandiax API"
    }
