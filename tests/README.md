# Tests - Distribuidora Velandiax

Ejecutar desde la raiz del proyecto:

```bash
python -m pytest tests -q
```

La suite actual valida los endpoints GET adaptados a la base nueva de Supabase:

- categorias
- productos
- variantes de producto
- pedidos

Las pruebas usan dobles de base de datos. No escriben datos en Supabase.

