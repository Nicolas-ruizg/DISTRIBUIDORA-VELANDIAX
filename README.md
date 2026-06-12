# Distribuidora Velandiax - API Backend

Backend FastAPI conectado a Supabase/PostgreSQL.

## Estado Actual

La API queda preparada para un panel en React con un unico administrador inicial.

El admin puede iniciar sesion, recibir un token JWT y administrar:

- Categorias
- Productos
- Variantes de productos
- Pedidos
- Dashboard administrativo

El esquema activo en Supabase usa estas tablas principales:

```text
categoria
producto
variantes_producto
clientes
pedido
items_pedido
paquetes_estaticos_items
```

## Flujo Para React

1. React envia email y password a `POST /admin/login`.
2. La API responde con un `token`.
3. React guarda el token.
4. React envia el token en cada endpoint protegido:

```http
Authorization: Bearer <token>
```

## Endpoints Actuales

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/` | Estado basico de la API |
| `POST` | `/admin/login` | Login del administrador |
| `GET` | `/categorias` | Listar categorias publico |
| `GET` | `/categorias/{id}` | Obtener categoria publica |
| `GET` | `/productos` | Listar productos publico |
| `GET` | `/productos/{id}` | Obtener producto con variantes |
| `GET` | `/admin/dashboard` | Metricas generales |
| `GET` | `/admin/categorias` | Listar categorias |
| `POST` | `/admin/categorias` | Crear categoria |
| `PUT` | `/admin/categorias/{id}` | Editar categoria |
| `DELETE` | `/admin/categorias/{id}` | Eliminar categoria |
| `GET` | `/admin/productos` | Listar productos |
| `POST` | `/admin/productos` | Crear producto |
| `GET` | `/admin/productos/{id}` | Obtener producto |
| `PUT` | `/admin/productos/{id}` | Editar producto |
| `DELETE` | `/admin/productos/{id}` | Eliminar producto |
| `POST` | `/admin/productos/{id}/variantes` | Crear variante |
| `PUT` | `/admin/variantes/{id}` | Editar variante |
| `DELETE` | `/admin/variantes/{id}` | Eliminar variante |
| `GET` | `/admin/pedidos` | Listar pedidos |
| `GET` | `/admin/pedidos/{id}` | Obtener pedido con items |
| `PUT` | `/admin/pedidos/{id}` | Editar pedido |
| `DELETE` | `/admin/pedidos/{id}` | Eliminar pedido |

## Configuracion Local

Crear `.env` con:

```env
DB_HOST=aws-1-us-east-1.pooler.supabase.com
DB_PORT=5432
DB_SSLMODE=require
DB_NAME=postgres
DB_USER=postgres.TU_PROJECT_REF
DB_PASSWORD=TU_PASSWORD
JWT_SECRET=TU_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ADMIN_EMAIL=admin@velandiax.com
ADMIN_PASSWORD=TU_PASSWORD_ADMIN
```

## Ejecutar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Validar

```bash
python -m compileall -q .
python -m pytest tests -q
```
