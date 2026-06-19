# Distribuidora Velandiax - API Backend

Backend FastAPI conectado a Supabase/PostgreSQL.

## Estado Actual

La API queda preparada para un panel en React con un unico administrador inicial.

El admin puede iniciar sesion, recibir un token JWT y administrar:

- Categorias
- Productos
- Variantes de productos
- Pedidos
- Envios y seguimiento simulado
- Usuarios administradores
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
envios
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
| `POST` | `/admin/productos/{id}/imagenes` | Crear imagen de producto |
| `POST` | `/admin/productos/{id}/imagenes/upload` | Subir archivo de imagen y registrarlo |
| `PUT` | `/admin/productos/imagenes/{id}` | Editar imagen de producto |
| `POST` | `/admin/productos/{id}/variantes` | Crear variante |
| `PUT` | `/admin/variantes/{id}` | Editar variante |
| `POST` | `/admin/variantes/{id}/imagenes` | Crear imagen de variante |
| `POST` | `/admin/variantes/{id}/imagenes/upload` | Subir archivo de imagen de variante |
| `PUT` | `/admin/variantes/imagenes/{id}` | Editar imagen de variante |
| `GET` | `/admin/pedidos` | Listar pedidos |
| `POST` | `/admin/pedidos` | Crear pedido manual |
| `GET` | `/admin/pedidos/{id}` | Obtener pedido con items |
| `PUT` | `/admin/pedidos/{id}` | Editar pedido |
| `DELETE` | `/admin/pedidos/{id}` | Eliminar pedido |
| `POST` | `/admin/pedidos/{id}/envio` | Crear un envio e iniciar la simulacion |
| `GET` | `/admin/pedidos/{id}/envio` | Consultar el envio de un pedido |
| `GET` | `/admin/envios` | Listar todos los envios |
| `GET` | `/envios/seguimiento/{guia}` | Seguimiento publico por numero de guia |
| `GET` | `/admin/usuarios` | Listar usuarios |
| `POST` | `/admin/usuarios` | Crear usuario |
| `GET` | `/admin/usuarios/{id}` | Obtener usuario |
| `PUT` | `/admin/usuarios/{id}` | Editar usuario |
| `DELETE` | `/admin/usuarios/{id}` | Desactivar usuario |

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
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ENVIO_INTERVALO_SEGUNDOS=30
```

## Simulacion De Envios

Al crear un envio, su estado y el del pedido avanzan automaticamente mientras la API esta encendida:

```text
PENDIENTE -> PREPARANDO -> DESPACHADO -> EN_TRANSITO -> ENTREGADO
```

## Crear Pedidos Manuales

La API permite crear pedidos desde admin sin flujo de pago transaccional.
Puedes usar un cliente existente con `id_cliente` o enviar datos de cliente nuevo.

Ejemplo para `POST /admin/pedidos`:

```json
{
  "cliente": {
    "nombre": "Laura Perez",
    "celular": "3005557788"
  },
  "es_mayorista": false,
  "precio_envio": 8000,
  "items": [
    {
      "id_variante": 3,
      "cantidad": 2
    }
  ]
}
```

Si no envias `precio_unitario`, la API usa el precio minorista o mayorista de la variante.
El pedido solo se puede crear con productos y variantes `ACTIVO`.

## Imagenes De Productos

Las imagenes se guardan como URLs asociadas al producto. Esto permite usar Supabase Storage,
Cloudinary u otro almacenamiento y guardar en la API solo la URL publica.

Ejemplo para `POST /admin/productos/1/imagenes`:

```json
{
  "url": "https://cdn.velandiax.com/productos/camiseta-frente.jpg",
  "alt_text": "Camiseta Dry-Fit vista frontal",
  "es_principal": true,
  "orden": 0
}
```

Para subir el archivo directamente, usa `POST /admin/productos/1/imagenes/upload`
como `multipart/form-data`:

```text
archivo: archivo JPG, PNG, WEBP o GIF
alt_text: texto alternativo opcional
es_principal: true / false
orden: 0
estado: ACTIVO
```

Para desactivar una imagen se usa `PUT /admin/productos/imagenes/{id}`:

```json
{
  "estado": "INACTIVO"
}
```

Las rutas publicas solo devuelven imagenes `ACTIVO`. Las rutas admin devuelven activas e inactivas.

Las variantes tambien pueden tener imagenes propias. Para subir una imagen directa:

```text
POST /admin/variantes/3/imagenes/upload
```

Campos `multipart/form-data`:

```text
archivo: archivo JPG, PNG, WEBP o GIF
alt_text: texto alternativo opcional
es_principal: true / false
orden: 0
estado: ACTIVO
```

## Estado De Productos Y Variantes

Los productos y variantes no se borran fisicamente porque pueden tener historial en pedidos y facturacion.
Para desactivar o reactivar se usa `PUT`, cambiando el campo `estado`.

Producto:

```json
{
  "estado": "INACTIVO"
}
```

Variante:

```json
{
  "estado": "INACTIVO"
}
```

Las rutas publicas solo muestran productos `ACTIVO` y variantes `ACTIVO`. Las rutas admin pueden consultar
productos y variantes activas e inactivas para administrarlas desde el panel.

Cada paso tarda 30 segundos. Desde `PENDIENTE` hasta `ENTREGADO` tarda aproximadamente 2 minutos.

Ejemplo para `POST /admin/pedidos/1/envio`:

```json
{
  "transportadora": "VELANDIAX EXPRESS",
  "nombre_destinatario": "Carlos Perez",
  "celular_destinatario": "3001234567",
  "direccion": "Calle 10 # 20-30",
  "ciudad": "Bogota",
  "departamento": "Cundinamarca",
  "costo": 12000
}
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
