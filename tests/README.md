# Tests - Distribuidora Velandiax

Ejecutar desde la raiz del proyecto:

```bash
python -m pytest tests -q
```

La suite valida calculos monetarios, consecutivos de venta, validaciones,
expiracion JWT, roles administrativos y el orden de insercion de una venta.

Las pruebas usan dobles de base de datos donde corresponde. No requieren pegar
tokens reales ni escriben ventas de prueba en la base configurada.

