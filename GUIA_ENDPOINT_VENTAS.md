# Guía de Uso: Endpoint POST de Ventas - Admin

## 📌 Descripción

El endpoint `POST /admin/ventas` permite a los administradores registrar nuevas operaciones comerciales en el sistema BackOffice de Velandiax. Este endpoint incluye:

✅ **Validación automática** de datos del cliente y productos  
✅ **Cálculos automáticos** de subtotal, descuentos, impuestos y total  
✅ **Generación secuencial** de números de venta únicos  
✅ **Trazabilidad completa** con registro del vendedor/admin  
✅ **Transacciones atómicas** en base de datos  

---

## 🔐 Autenticación

**Requisitos:**
- Token JWT válido en header `Authorization: Bearer <token>`
- Rol del usuario debe ser **ADMIN**

**Header requerido:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📋 Estructura de Solicitud

### URL
```
POST http://localhost:8000/admin/ventas
```

### Headers
```json
{
    "Authorization": "Bearer <token_jwt>",
    "Content-Type": "application/json"
}
```

### Body (JSON)
```json
{
    "cliente": {
        "nombre": "Juan Pérez García",
        "email": "juan.perez@empresa.com",
        "telefono": "+34 912 345 678",
        "empresa": "Distribuidora ABC S.L."
    },
    "productos": [
        {
            "id_producto": 1,
            "nombre_producto": "Producto Premium X",
            "cantidad": 5,
            "precio_unitario": 150.00,
            "descuento_porcentaje": 10
        },
        {
            "id_producto": 2,
            "nombre_producto": "Servicio de Instalación",
            "cantidad": 1,
            "precio_unitario": 200.00,
            "descuento_porcentaje": 0
        }
    ],
    "forma_pago": "transferencia",
    "impuesto_porcentaje": 19,
    "notas": "Entrega urgente solicitada para el 31/05/2026",
    "referencia_externa": "OC-2026-001"
}
```

---

## 📊 Cálculos Automáticos

El sistema realiza los siguientes cálculos automáticamente:

### Ejemplo de Cálculo:

**Productos:**
- Producto 1: 5 × 150 = 750 € (descuento 10%) = 675 €
- Producto 2: 1 × 200 = 200 € (descuento 0%) = 200 €

**Totales:**
```
Subtotal:              950.00 €
Descuento total:      -75.00 € (10% en Producto 1)
Subtotal con desc.:   875.00 €
IVA (19%):            +166.25 €
─────────────────────────────
TOTAL:                1041.25 €
```

---

## ✅ Respuesta Exitosa (200 OK)

```json
{
    "success": true,
    "mensaje": "Venta registrada exitosamente",
    "venta": {
        "id_venta": 42,
        "numero_venta": "VTA-2026-0000042",
        "cliente": {
            "nombre": "Juan Pérez García",
            "email": "juan.perez@empresa.com",
            "telefono": "+34 912 345 678",
            "empresa": "Distribuidora ABC S.L."
        },
        "productos": [
            {
                "id_producto": 1,
                "nombre_producto": "Producto Premium X",
                "cantidad": 5,
                "precio_unitario": 150.00,
                "descuento_porcentaje": 10
            },
            {
                "id_producto": 2,
                "nombre_producto": "Servicio de Instalación",
                "cantidad": 1,
                "precio_unitario": 200.00,
                "descuento_porcentaje": 0
            }
        ],
        "forma_pago": "transferencia",
        "estado": "confirmada",
        "subtotal": 950.00,
        "descuento_total": 75.00,
        "impuesto": 166.25,
        "impuesto_porcentaje": 19,
        "total": 1041.25,
        "fecha_creacion": "2026-05-30T14:32:18.123456",
        "vendedor": "Admin User",
        "referencia_externa": "OC-2026-001"
    }
}
```

---

## ❌ Códigos de Error

### 400 - Bad Request (Datos Inválidos)
```json
{
    "detail": "Validación de productos falló: Debe incluir al menos 1 producto"
}
```

**Causas posibles:**
- Cantidad de productos = 0
- Cantidad de productos > 100
- Cantidad total de items > 10,000
- Campos requeridos faltantes
- Email inválido

### 401 - Unauthorized (Token Inválido)
```json
{
    "detail": "Token inválido o expirado"
}
```

### 403 - Forbidden (No es Admin)
```json
{
    "detail": "Acceso denegado. Solo administradores pueden realizar esta acción"
}
```

### 500 - Internal Server Error
```json
{
    "detail": "Error al registrar venta: [descripción del error]"
}
```

---

## 🧪 Ejemplos con cURL

### Crear una venta simple:
```bash
curl -X POST http://localhost:8000/admin/ventas \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nombre": "Cliente Test",
      "email": "cliente@test.com"
    },
    "productos": [
      {
        "id_producto": 1,
        "nombre_producto": "Producto A",
        "cantidad": 2,
        "precio_unitario": 100,
        "descuento_porcentaje": 5
      }
    ],
    "forma_pago": "efectivo",
    "impuesto_porcentaje": 19
  }'
```

---

## 📝 Validaciones Aplicadas

| Campo | Validación |
|-------|-----------|
| `nombre_cliente` | Mínimo 3 caracteres, máximo 100 |
| `email_cliente` | Formato de email válido |
| `telefono_cliente` | Formato internacional (opcional) |
| `cantidad` | Mayor a 0 |
| `precio_unitario` | Mayor a 0 |
| `descuento_porcentaje` | Entre 0 y 100 |
| `impuesto_porcentaje` | Entre 0 y 100 |
| `productos` | Mínimo 1, máximo 100 |
| `forma_pago` | efectivo, transferencia, tarjeta_credito, tarjeta_debito, cheque |

---

## 🗄️ Estructura de Base de Datos Generada

### Tabla `ventas`
Almacena el registro principal de cada venta con totales calculados.

**Campos clave:**
- `numero_venta`: Generado automáticamente (VTA-2026-NNNNNNN)
- `subtotal`, `descuento_total`, `impuesto`, `total`: Calculados automáticamente
- `estado`: Inicialmente "confirmada"
- `fecha_creacion`: Timestamp del servidor

### Tabla `detalles_ventas`
Almacena el detalle de cada línea de producto en la venta.

---

## 📈 Vistas para Reportes (SQL)

El sistema genera automáticamente 3 vistas para análisis:

1. **vista_ventas_por_dia**: Resumen diario de ventas
2. **vista_productos_mas_vendidos**: Top 50 productos
3. **vista_performance_vendedores**: Rendimiento por vendedor

---

## 🔄 Flujo de Proceso

```
1. Cliente envía solicitud POST con datos de venta
   ↓
2. Validar token y rol (debe ser admin)
   ↓
3. Validar estructura de productos
   ↓
4. Calcular automáticamente totales
   ↓
5. Iniciar transacción en BD
   ↓
6. Insertar venta en tabla "ventas"
   ↓
7. Generar número de venta único
   ↓
8. Insertar detalles en tabla "detalles_ventas"
   ↓
9. Confirmar transacción
   ↓
10. Retornar respuesta con datos de venta creada
```

---

## 💡 Próximas Funcionalidades Recomendadas

- ✨ Endpoint GET para listar ventas con filtros
- ✨ Endpoint PUT para modificar estado de venta
- ✨ Endpoint para generar reportes PDF
- ✨ Integración con notificaciones por email
- ✨ Endpoint para consultar analytics en tiempo real
- ✨ Control de inventario (decrementar stock automáticamente)
