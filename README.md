# DISTRIBUIDORA VELANDIAX

Plataforma integral para la gestion comercial de VELANDIAX, una distribuidora
de ropa con ventas presenciales y por internet. El repositorio reune:

- `DISTRIBUIDORA-VELANDIAX`: API REST con FastAPI, SQLAlchemy y PostgreSQL.
- `velandiax-admin`: tienda y panel administrativo en React, TypeScript y Vite.
- `Velandiax-Chatbot`: asistente de WhatsApp para consultar el catalogo.
- `documentacion`: documentacion tecnica integral en PDF y su generador.

Repositorio oficial:
https://github.com/Nicolas-ruizg/DISTRIBUIDORA-VELANDIAX

## Backend

```bash
cd DISTRIBUIDORA-VELANDIAX
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Crear `.env` desde `.env.example` antes de ejecutar.

## Frontend

```bash
cd velandiax-admin
npm install
npm run dev
```

Crear `.env` desde `.env.example` antes de ejecutar.

## Chatbot

```bash
cd Velandiax-Chatbot
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

Crear `.env` desde `.env.example` antes de ejecutar.

## URLs locales

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8001`
- Swagger: `http://127.0.0.1:8001/docs`
- Chatbot: `http://127.0.0.1:8002`

## Documentacion

La memoria tecnica del proyecto, elaborada con la plantilla institucional SENA
y estructura academica APA, se encuentra en:

`documentacion/Documentacion_Tecnica_Integral_VELANDIAX_APA.pdf`

Incluye arquitectura, modelo de datos, endpoints, interfaces, seguridad,
despliegue, metodologias, pruebas, trazabilidad y evolucion del repositorio Git.
