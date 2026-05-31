# ✅ CHECKLIST - CONFIGURACIÓN INICIAL

Pasos necesarios para que el proyecto funcione correctamente.

## 📦 PASO 1: Instalar Dependencias

```bash
# 1. Crear ambiente virtual (opcional pero recomendado)
python -m venv venv

# 2. Activar ambiente virtual
# Windows:
venv\Scripts\activate
# MacOS/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

**Verificar instalación:**
```bash
pip list
```

---

## 🗄️ PASO 2: Configurar Base de Datos

### 2.1 Crear Base de Datos PostgreSQL

```sql
-- En PostgreSQL (psql o PgAdmin)
CREATE DATABASE velandiax_db;
```

### 2.2 Crear Tablas

```bash
# Opción 1: Ejecutar script SQL
psql -U postgres -d velandiax_db -f database/schema_ventas.sql

# Opción 2: Copiar y pegar en PgAdmin o psql
-- Ir a: database/schema_ventas.sql
-- Copiar todo el contenido
-- Pegar en consola de PostgreSQL
```

### 2.3 Crear Usuario Admin (Opcional)

```sql
-- En base de datos PostgreSQL
INSERT INTO usuarios_backoffice (nombre, email, password_hash, rol)
VALUES (
    'Admin Velandiax',
    'admin@velandiax.com',
    -- Hash bcrypt de "Admin123*" - Generar con generar_hash.py
    '$2b$12$...',  
    'admin'
);
```

---

## 🔐 PASO 3: Configurar Variables de Entorno

### 3.1 Crear archivo `.env`

```bash
# Copiar .env.example a .env
cp .env.example .env
# O en Windows:
copy .env.example .env
```

### 3.2 Editar `.env` con datos reales

```bash
# Editar con tu editor favorito
nano .env          # Linux/Mac
notepad .env       # Windows
```

**Campos CRÍTICOS a completar:**

```env
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=velandiax_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_postgres

# JWT
JWT_SECRET=una_clave_muy_segura_minimo_32_caracteres_aqui

# Otros
ENVIRONMENT=development
DEBUG=True
```

**⚠️ NUNCA compartir `.env` en git!**

---

## 🔑 PASO 4: Generar Hash de Contraseña

Para crear usuarios, necesitas generar hashes bcrypt seguros:

```bash
# Ejecutar script
python generar_hash.py

# Ingresa la contraseña cuando pida
# Ejemplo output: $2b$12$abc123...

# Copiar este hash a la base de datos
```

---

## 🚀 PASO 5: Iniciar el Servidor

```bash
# Opción 1: Desarrollo (con auto-reload)
uvicorn main:app --reload

# Opción 2: Producción
uvicorn main:app --host 0.0.0.0 --port 8000

# Verificar que esté corriendo:
# Ir a: http://localhost:8000/docs
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Application startup complete
```

---

## 🧪 PASO 6: Obtener Token JWT

### 6.1 Mediante la API

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@velandiax.com",
    "password": "Admin123*"
  }'

# Response:
# {
#   "success": true,
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "usuario": {...}
# }
```

### 6.2 Copiar Token

```bash
# Guardar el token para usar en los tests
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📝 PASO 7: Probar Endpoint POST /admin/ventas

### 7.1 Actualizar archivo de tests

Editar `tests/test_venta_creation.py`:
```python
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Pegar token aquí
```

### 7.2 Ejecutar tests

```bash
python tests/test_venta_creation.py
```

**Resultado esperado:** ✅ Todos los tests pasan

---

## 📊 PASO 8: Verificar Datos en BD

```bash
# Conectarse a PostgreSQL
psql -U postgres -d velandiax_db

# Listar ventas creadas
SELECT * FROM ventas;

# Ver detalles de una venta
SELECT * FROM detalles_ventas WHERE id_venta = 1;

# Ver rendimiento de vendedores
SELECT * FROM vista_performance_vendedores;
```

---

## 🌐 PASO 9: Acceder a la Documentación Interactiva

Abrir en navegador:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Aquí puedes:
- ✅ Ver todos los endpoints
- ✅ Probar endpoints directamente
- ✅ Ver esquemas de request/response

---

## 📚 PASO 10: Revisar Documentación

Lee estos archivos en este orden:
1. **README.md** - Descripción general
2. **GUIA_ENDPOINT_VENTAS.md** - Uso del endpoint POST
3. **tests/README.md** - Cómo ejecutar tests
4. **database/schema_ventas.sql** - Estructura de BD

---

## ⚠️ TROUBLESHOOTING

### Error: `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements.txt
```

### Error: `could not connect to server: Connection refused`
- PostgreSQL no está corriendo
- Servicio PostgreSQL no iniciado

### Error: `password authentication failed`
- Contraseña de PostgreSQL incorrecta en `.env`
- Usuario no existe

### Error: `Token inválido`
- Generar nuevo token
- Verificar JWT_SECRET en `.env`
- Comprobar que no expiró

### Error: `Acceso denegado`
- Usuario no tiene rol 'admin'
- Modificar base de datos: `UPDATE usuarios_backoffice SET rol='admin'`

---

## 📋 RESUMEN DE ARCHIVOS CRÍTICOS

| Archivo | Descripción |
|---------|-----------|
| `.env` | Variables de entorno (CREAR desde .env.example) |
| `main.py` | Entrada principal de FastAPI |
| `routes/admin.py` | Endpoints de admin |
| `routes/auth.py` | Endpoint de login |
| `schemas/venta_schema.py` | Validación de datos de ventas |
| `utils/calculadora_venta.py` | Cálculos automáticos |
| `database/schema_ventas.sql` | Script de base de datos |

---

## 🎯 PRÓXIMOS PASOS

Después de completar este checklist:

- [ ] Crear más usuarios (admin, vendedores)
- [ ] Implementar GET /admin/ventas (listar ventas)
- [ ] Implementar PUT /admin/ventas/{id} (modificar venta)
- [ ] Crear endpoint de reportes
- [ ] Implementar módulo E-Commerce
- [ ] Implementar bot WhatsApp

---

## 📞 AYUDA

Si encuentras problemas:

1. **Revisar logs del servidor**
2. **Revisar archivo `.env`**
3. **Verificar conexión BD:** `psql -U postgres -d velandiax_db`
4. **Limpiar caché:** `rm -rf __pycache__` y `rm -rf .pytest_cache`
5. **Reinstalar dependencias:** `pip install --upgrade -r requirements.txt`

---

**Estado:** ✅ Listo para desarrollar  
**Última actualización:** 30 de mayo de 2026  
**Versión:** 1.0
