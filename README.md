# Distribuidora Velandiax - API Backend

Backend administrativo desarrollado con FastAPI y PostgreSQL.

## Estado actual

El proyecto esta en desarrollo activo. Ya incluye:

- Login con bcrypt y JWT con expiracion.
- Validacion de roles administrativos.
- Dashboard protegido.
- Registro transaccional de ventas con calculos monetarios.
- CRUD administrativo de categorias.
- Script SQL repetible para preparar el modulo.
- Pruebas automatizadas sin credenciales reales.

La hoja de ruta completa esta en [PLAN_TRABAJO.md](PLAN_TRABAJO.md).

## Endpoints

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/` | Estado basico de la API |
| `POST` | `/auth/login` | Inicio de sesion |
| `GET` | `/admin/dashboard` | Dashboard protegido |
| `POST` | `/admin/ventas` | Registrar venta |
| `GET` | `/admin/categorias` | Listar categorias |
| `POST` | `/admin/categorias` | Crear categoria |
| `PUT` | `/admin/categorias/{id}` | Actualizar categoria |
| `DELETE` | `/admin/categorias/{id}` | Desactivar categoria |

## Configuracion local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Completar en `.env` las credenciales de PostgreSQL y `JWT_SECRET`. El archivo
`.env` es local y no debe subirse al repositorio.

## Verificacion

```bash
python -m compileall -q .
python -m pytest tests -q
```

Swagger esta disponible en `http://localhost:8000/docs`.
