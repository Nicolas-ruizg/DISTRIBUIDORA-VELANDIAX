-- Inventario por variante de producto.
-- Permite controlar disponibilidad por talla/color/referencia.

ALTER TABLE variantes_producto
ADD COLUMN IF NOT EXISTS stock INTEGER NOT NULL DEFAULT 0;

ALTER TABLE variantes_producto
DROP CONSTRAINT IF EXISTS ck_variante_producto_stock_orm;

ALTER TABLE variantes_producto
ADD CONSTRAINT ck_variante_producto_stock_orm CHECK (stock >= 0);
