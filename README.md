# VELANDIAX

Proyecto completo de VELANDIAX:

- `DISTRIBUIDORA-VELANDIAX`: backend FastAPI + SQLAlchemy.
- `velandiax-admin`: frontend React + Vite.

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

## URLs locales

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8001`
- Swagger: `http://127.0.0.1:8001/docs`
