# Plan de trabajo - Distribuidora Velandiax

## Objetivo del MVP

Construir un backend administrativo confiable para autenticar usuarios, gestionar
catalogo e inventario, registrar ventas y consultar reportes basicos.

## Fase 1 - Estabilizacion de la base

- [x] Proteger archivos locales y secretos con `.gitignore`.
- [x] Normalizar roles de administrador.
- [x] Agregar expiracion a los JWT.
- [x] Corregir la generacion del numero de venta.
- [x] Preparar pruebas automatizadas con aserciones reales.
- [ ] Rotar credenciales que estuvieron expuestas en Git.

## Fase 2 - Catalogo e inventario

- [x] Crear endpoints CRUD de categorias.
- [ ] Crear endpoints CRUD de productos.
- [ ] Definir precios minorista y mayorista en el flujo de venta.
- [ ] Validar productos contra base de datos al registrar una venta.
- [ ] Descontar stock dentro de la misma transaccion de venta.

## Fase 3 - Gestion de ventas

- [ ] Listar ventas con paginacion y filtros.
- [ ] Consultar el detalle de una venta.
- [ ] Actualizar el estado de una venta.
- [ ] Cancelar ventas con trazabilidad.
- [ ] Reintegrar stock al cancelar cuando corresponda.

## Fase 4 - Clientes y reportes

- [ ] Crear CRUD de clientes.
- [ ] Exponer resumen de ventas por periodo.
- [ ] Exponer productos mas vendidos.
- [ ] Exponer indicadores del dashboard.

## Fase 5 - Preparacion para entrega

- [ ] Agregar migraciones de base de datos.
- [ ] Separar configuracion por ambiente.
- [ ] Agregar logs estructurados.
- [ ] Ejecutar pruebas de integracion en una base aislada.
- [ ] Documentar despliegue y respaldo.
