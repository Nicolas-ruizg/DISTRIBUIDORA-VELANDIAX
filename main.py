from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.categorias import router as categorias_router



app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(categorias_router)
@app.get("/")
def home():

    return {
        "message": "Velandiax API"
    }
