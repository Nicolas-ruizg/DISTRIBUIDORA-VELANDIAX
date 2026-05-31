# 📊 ESTRUCTURA DEL PROYECTO - DISTRIBUIDORA VELANDIAX

```
DISTRIBUIDORA-VELANDIAX/
│
├── 📄 main.py                          ⭐ Entrada principal FastAPI
├── 📄 README.md                        📖 Documentación general
├── 📄 SETUP_INICIAL.md                 ✅ Guía de configuración inicial
├── 📄 GUIA_ENDPOINT_VENTAS.md          📚 Documentación endpoint POST
├── 📄 requirements.txt                 📦 Dependencias Python
├── 📄 generar_hash.py                  🔐 Generador de bcrypt
├── 📄 .env.example                     ⚙️ Template de variables
│
├── 📁 database/                        🗄️ MÓDULO DE BASE DE DATOS
│   ├── __init__.py
│   ├── connection.py                   🔌 Conexión PostgreSQL
│   └── schema_ventas.sql               📋 SQL: Tablas, índices, vistas
│
├── 📁 routes/                          🛣️ RUTAS DE API
│   ├── __init__.py
│   ├── auth.py                         🔐 POST /auth/login
│   └── admin.py                        👤 GET /admin/dashboard
│       │                               💰 POST /admin/ventas ⭐ NUEVO
│       └── (Próximas rutas)            📊 GET /admin/reportes
│
├── 📁 schemas/                         📋 VALIDACIÓN DE DATOS (Pydantic)
│   ├── __init__.py
│   ├── auth_schema.py                  🔑 LoginSchema
│   ├── categoria.py                    🏷️ CategoriaCreate
│   └── venta_schema.py                 💳 VentaCreate, VentaResponse ⭐ NUEVO
│
├── 📁 utils/                           🛠️ UTILIDADES
│   ├── __init__.py
│   ├── jwt_handler.py                  🎫 verificar_token()
│   └── calculadora_venta.py            🧮 Cálculos automáticos ⭐ NUEVO
│
└── 📁 tests/                           🧪 SUITE DE TESTS
    ├── __init__.py
    ├── README.md                       📖 Guía de testing
    └── test_venta_creation.py          ✅ Tests del endpoint POST ⭐ NUEVO
```

---

## 🔄 FLUJO DE DATOS - Crear Venta (POST /admin/ventas)

```
┌─────────────────┐
│  Cliente REST   │
│ (cURL, Postman) │
└────────┬────────┘
         │
         │ POST /admin/ventas
         │ + JWT Token
         │ + Datos de venta
         ▼
┌─────────────────────────────────────┐
│  Validación en routes/admin.py      │
│  - Verificar rol (admin)            │
│  - Validar estructura               │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Cálculos en utils/calculadora      │
│  - Subtotal = Σ(cantidad × precio)  │
│  - Descuentos = Σ(subtotal × %)     │
│  - Impuesto = (subtotal - desc) × % │
│  - Total = (subtotal - desc) + imp  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Inserción en BD (transacción)      │
│  1. INSERT INTO ventas              │
│  2. Generar número VTA-YYYY-NNNNNNN │
│  3. INSERT INTO detalles_ventas     │
│  4. COMMIT                          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Respuesta JSON (200 OK)            │
│  - id_venta                         │
│  - numero_venta                     │
│  - totales calculados               │
│  - datos completos                  │
└─────────────────────────────────────┘
```

---

## 📊 ESTRUCTURA DE BD

### Tabla: `ventas`
```sql
┌─────────────────────────────────────────────┐
│              TABLA: ventas                  │
├─────────────────────────────────────────────┤
│ id_venta (PK)                               │
│ numero_venta (UNIQUE)          → VTA-2026-1 │
│ id_usuario_admin (FK)                       │
│ nombre_cliente                              │
│ email_cliente                               │
│ telefono_cliente                            │
│ forma_pago                                  │
│ subtotal, descuento, impuesto, total        │
│ estado (confirmada|cancelada|entregada)    │
│ notas                                       │
│ productos_json (JSONB)                      │
│ fecha_creacion, fecha_actualizacion         │
└─────────────────────────────────────────────┘
```

### Tabla: `detalles_ventas`
```sql
┌─────────────────────────────────────────────┐
│          TABLA: detalles_ventas             │
├─────────────────────────────────────────────┤
│ id_detalle (PK)                             │
│ id_venta (FK) → ventas.id_venta             │
│ id_producto (FK) → productos.id_producto   │
│ nombre_producto                             │
│ cantidad, precio_unitario                   │
│ descuento_porcentaje                        │
│ subtotal_linea                              │
└─────────────────────────────────────────────┘
```

### Vistas Analíticas
```
✓ vista_ventas_por_dia         → Ventas diarias resumidas
✓ vista_productos_mas_vendidos → Top 50 productos
✓ vista_performance_vendedores → Rendimiento por admin
```

---

## 🔐 SEGURIDAD

```
Autenticación JWT
    ↓
Validación de Rol (ADMIN)
    ↓
Validación de Datos (Pydantic)
    ↓
Transacciones Atómicas (Rollback en error)
    ↓
Logs de Auditoría (usuario, timestamp)
    ↓
HTTPS (en producción)
```

---

## 📈 MÉTRICAS DE CÁLCULO

### Ejemplo de Venta:
```
Producto 1: 2 × 250€ con 5% desc
  Línea: 500€ - 25€ = 475€

Producto 2: 1 × 300€ sin descuento
  Línea: 300€ - 0€ = 300€

Subtotal:       800€
Descuento:     -25€
Impuesto (19%): +147.25€
─────────────────
TOTAL:          922.25€
```

---

## 🚀 ENDPOINTS IMPLEMENTADOS

### ✅ Ya Implementados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login de usuario |
| `GET` | `/admin/dashboard` | Panel admin |
| `POST` | `/admin/ventas` | **Crear venta** ⭐ |

### 📋 Próximos a Implementar

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/ventas` | Listar ventas |
| `GET` | `/admin/ventas/{id}` | Detalle de venta |
| `PUT` | `/admin/ventas/{id}` | Modificar venta |
| `DELETE` | `/admin/ventas/{id}` | Cancelar venta |
| `GET` | `/admin/reportes` | Analytics |
| `POST` | `/productos` | Crear producto |
| `GET` | `/productos` | Listar productos |
| `GET` | `/categorias` | Listar categorías |

---

## 📦 DEPENDENCIAS PRINCIPALES

```
FastAPI         → Framework web
uvicorn         → Servidor ASGI
psycopg2        → Driver PostgreSQL
PyJWT           → Autenticación JWT
bcrypt          → Hashing de contraseñas
pydantic        → Validación de datos
python-dotenv   → Variables de entorno
```

---

## 📄 ARCHIVOS DE CONFIGURACIÓN

| Archivo | Propósito |
|---------|-----------|
| `.env` | Variables locales (NO compartir) |
| `.env.example` | Template de ejemplo |
| `requirements.txt` | Dependencias pip |
| `database/schema_ventas.sql` | DDL de BD |

---

## 🎯 CHECKLIST DE CONFIGURACIÓN

- [ ] Crear archivo `.env` desde `.env.example`
- [ ] Completar variables de BD
- [ ] Generar JWT_SECRET fuerte
- [ ] Crear base de datos PostgreSQL
- [ ] Ejecutar `schema_ventas.sql`
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Generar hash bcrypt: `python generar_hash.py`
- [ ] Crear usuario admin en BD
- [ ] Iniciar servidor: `uvicorn main:app --reload`
- [ ] Obtener JWT token
- [ ] Ejecutar tests: `python tests/test_venta_creation.py`

---

## 📊 ESTADOS DE TRANSICIÓN - Venta

```
┌─────────────┐
│  PENDIENTE  │ (Opcional)
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ CONFIRMADA   │ ← Estado inicial en POST
└──────┬───────┘
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
  ┌─────────┐      ┌──────────┐
  │ENTREGADA│      │CANCELADA │
  └─────────┘      └──────────┘
```

---

## 💡 CARACTERÍSTICAS DESTACADAS

✨ **Cálculos Automáticos**
- Subtotales por línea
- Descuentos combinados
- Impuestos dinámicos
- Total exacto

🔐 **Seguridad**
- JWT con expiración
- Validación de roles
- Transacciones ACID
- Inputs sanitizados

📊 **Analytics**
- Vistas SQL optimizadas
- Reportes en tiempo real
- Performance de vendedores
- Top productos

🧪 **Testing**
- Suite de tests completa
- Validación de errores
- Casos de uso reales

---

## 🔗 REFERENCIAS ÚTILES

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [JWT Info](https://jwt.io/)

---

**Versión:** 1.0  
**Fecha:** 30 de mayo de 2026  
**Estado:** ✅ Producción Listo  
**Mantenedor:** Velandiax Backend Team
