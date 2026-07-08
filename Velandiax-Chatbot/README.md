# Velandiax WhatsApp Chatbot

Chatbot comercial en Python para WhatsApp Cloud API. Incluye menús interactivos,
catálogo con fotos y variantes, categorías, ofertas, favoritos, compra por volumen,
selector de cantidades, carrito, Gemini, checkout y seguimiento. El precio especial
se calcula internamente desde `VOLUME_MIN_QUANTITY` y no se expone al cliente.

## Puesta en marcha

1. Crea el entorno e instala dependencias:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   ```

2. Copia `.env.example` como `.env` y completa los datos de Meta. Nunca subas el
   archivo `.env` al repositorio.

3. Reemplaza los ejemplos de `data/products.json` por los productos reales. Los
   precios se guardan como pesos enteros, sin puntos ni comas.

4. Ejecuta el servidor:

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

5. Expón temporalmente el puerto con un túnel HTTPS (por ejemplo, Cloudflare
   Tunnel o ngrok) y configura en Meta esta URL:

   ```text
   https://tu-dominio.com/webhook
   ```

   El token de verificación debe coincidir con `WHATSAPP_VERIFY_TOKEN`. Suscribe el
   campo `messages` del objeto de WhatsApp Business Account.

## Pruebas

```powershell
pytest -q
```

Los pedidos confirmados quedan en `data/orders.jsonl`, uno por línea. Para una sola
instancia pequeña esto sirve como arranque; en producción con varios procesos se
debe reemplazar el almacenamiento de sesiones y pedidos por Redis y una base de
datos. `SalesBot` y `OrderRepository` están separados precisamente para facilitar
ese cambio o conectar métodos Python existentes.

## Integración con el backend existente

Configura `BACKEND_API_URL` para cargar productos y variantes reales desde
`GET /productos` y `GET /productos/{id}`. La opción de seguimiento consulta
`GET /pedidos/seguimiento` usando el mismo número que escribe por WhatsApp.

La creación remota usa `POST /admin/login` y `POST /admin/pedidos`, por lo que la
cuenta indicada debe tener rol `VENDEDOR` o `ADMINISTRADOR`. Para replicar el
storefront, crea el pedido como `PENDIENTE` con `estado_pago=CANCELADO` hasta que
un asesor coordine y registre el pago. Activa `BACKEND_CREATE_ORDERS=true` solo
después de configurar `BACKEND_API_EMAIL` y `BACKEND_API_PASSWORD`.

## Gemini

Configura `GEMINI_API_KEY` con una clave de Google AI Studio. Gemini interpreta
lenguaje natural y recomienda productos, pero no ejecuta directamente compras ni
inventa datos: todas las acciones se validan contra el catálogo y el flujo del bot.
