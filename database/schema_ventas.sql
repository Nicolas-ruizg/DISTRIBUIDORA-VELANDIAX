-- Modulo de ventas para Distribuidora Velandiax.
-- Las tablas base se crean primero para que las llaves foraneas sean validas.

CREATE TABLE IF NOT EXISTS usuarios_backoffice (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'VENDEDOR',
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre_categoria VARCHAR(100) UNIQUE NOT NULL,
    activa BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    id_categoria INTEGER,
    nombre_prenda VARCHAR(150) NOT NULL,
    descripcion TEXT,
    url_imagen TEXT,
    modalidad_venta VARCHAR(20) DEFAULT 'AMBAS',
    precio_lista DECIMAL(10, 2) NOT NULL,
    precio_minorista DECIMAL(10, 2) NOT NULL,
    precio_mayorista DECIMAL(10, 2) NOT NULL,
    activo BOOLEAN DEFAULT true,
    url_producto TEXT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta SERIAL PRIMARY KEY,
    numero_venta VARCHAR(20) UNIQUE NOT NULL,
    id_usuario_admin INTEGER NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    email_cliente VARCHAR(100) NOT NULL,
    telefono_cliente VARCHAR(20),
    empresa_cliente VARCHAR(150),
    forma_pago VARCHAR(20) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    descuento_total DECIMAL(10, 2) DEFAULT 0,
    impuesto DECIMAL(10, 2) NOT NULL,
    impuesto_porcentaje DECIMAL(5, 2) DEFAULT 19,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'confirmada',
    referencia_externa VARCHAR(50),
    notas TEXT,
    productos_json JSONB,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario_admin) REFERENCES usuarios_backoffice(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS detalles_ventas (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    nombre_producto VARCHAR(150) NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL,
    descuento_porcentaje DECIMAL(5, 2) DEFAULT 0,
    subtotal_linea DECIMAL(10, 2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(id_usuario_admin);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente_email ON ventas(email_cliente);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_ventas_estado ON ventas(estado);
CREATE INDEX IF NOT EXISTS idx_detalles_venta ON detalles_ventas(id_venta);
CREATE INDEX IF NOT EXISTS idx_detalles_producto ON detalles_ventas(id_producto);

CREATE OR REPLACE VIEW vista_ventas_por_dia AS
SELECT
    DATE(fecha_creacion) AS fecha,
    COUNT(*) AS total_ventas,
    SUM(total) AS total_monto,
    AVG(total) AS promedio_venta,
    COUNT(DISTINCT nombre_cliente) AS clientes_unicos
FROM ventas
WHERE estado != 'cancelada'
GROUP BY DATE(fecha_creacion)
ORDER BY fecha DESC;

CREATE OR REPLACE VIEW vista_productos_mas_vendidos AS
SELECT
    id_producto,
    nombre_producto,
    COUNT(*) AS veces_vendido,
    SUM(cantidad) AS cantidad_total,
    SUM(subtotal_linea) AS monto_total
FROM detalles_ventas
GROUP BY id_producto, nombre_producto
ORDER BY cantidad_total DESC
LIMIT 50;

CREATE OR REPLACE VIEW vista_performance_vendedores AS
SELECT
    v.id_usuario_admin,
    u.nombre AS vendedor,
    COUNT(v.id_venta) AS total_ventas,
    SUM(v.total) AS monto_total,
    AVG(v.total) AS ticket_promedio,
    MAX(v.fecha_creacion) AS ultima_venta
FROM ventas v
JOIN usuarios_backoffice u ON v.id_usuario_admin = u.id_usuario
WHERE v.estado != 'cancelada'
GROUP BY v.id_usuario_admin, u.nombre
ORDER BY monto_total DESC;

CREATE OR REPLACE FUNCTION actualizar_fecha_venta()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_venta ON ventas;
CREATE TRIGGER trigger_actualizar_venta
    BEFORE UPDATE ON ventas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_venta();
