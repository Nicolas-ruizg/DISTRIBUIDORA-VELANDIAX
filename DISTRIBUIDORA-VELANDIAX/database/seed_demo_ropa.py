from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
import os
import re
import unicodedata
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import bcrypt
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import text

from database.connection import SessionLocal
from database.models import (
    Categoria,
    Cliente,
    Envio,
    ImagenProducto,
    ImagenVarianteProducto,
    ItemPedido,
    PaqueteEstaticoItem,
    Pedido,
    Producto,
    Usuario,
    VarianteProducto,
)


load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
STORAGE_KEY = os.environ["SUPABASE_STORAGE_KEY"]
STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "productos")
RUN_ID = datetime.now().strftime("%Y%m%d%H%M%S")


CATEGORIAS = [
    ("Camisetas", "Camisetas basicas, estampadas y premium."),
    ("Camisas", "Camisas casuales y formales para hombre y mujer."),
    ("Blusas", "Blusas femeninas para uso casual y elegante."),
    ("Jeans", "Jeans en diferentes cortes, tallas y lavados."),
    ("Pantalones", "Pantalones urbanos, cargo y clasicos."),
    ("Vestidos", "Vestidos casuales y para ocasiones especiales."),
    ("Chaquetas", "Chaquetas livianas, denim y urbanas."),
    ("Ropa Deportiva", "Conjuntos y prendas para actividad fisica."),
    ("Buzos", "Buzos y hoodies para clima frio."),
    ("Paquetes", "Combos de prendas para venta mayorista y minorista."),
]


PRODUCTOS = [
    {
        "categoria": "Camisetas",
        "nombre": "Camiseta Basica Premium",
        "descripcion": "Camiseta unisex en algodon peinado de 180 gramos.",
        "color": "#1F2937",
        "variantes": [
            ("Blanco / M", 22000, 45000, 34000, 0.22, {"color": "Blanco", "talla": "M", "material": "Algodon"}),
            ("Negro / L", 22000, 45000, 34000, 0.23, {"color": "Negro", "talla": "L", "material": "Algodon"}),
        ],
    },
    {
        "categoria": "Camisas",
        "nombre": "Camisa Oxford Manga Larga",
        "descripcion": "Camisa Oxford de corte moderno para oficina o uso casual.",
        "color": "#2563EB",
        "variantes": [
            ("Azul / M", 39000, 78000, 58000, 0.35, {"color": "Azul", "talla": "M", "manga": "Larga"}),
            ("Blanco / L", 39000, 78000, 58000, 0.36, {"color": "Blanco", "talla": "L", "manga": "Larga"}),
        ],
    },
    {
        "categoria": "Blusas",
        "nombre": "Blusa Satinada Elegance",
        "descripcion": "Blusa satinada de caida suave y acabado elegante.",
        "color": "#EC4899",
        "variantes": [
            ("Rosa / S", 36000, 72000, 54000, 0.20, {"color": "Rosa", "talla": "S", "material": "Satin"}),
            ("Marfil / M", 36000, 72000, 54000, 0.21, {"color": "Marfil", "talla": "M", "material": "Satin"}),
        ],
    },
    {
        "categoria": "Jeans",
        "nombre": "Jean Skinny High Rise",
        "descripcion": "Jean tiro alto con tela stretch y horma ajustada.",
        "color": "#1E3A8A",
        "variantes": [
            ("Azul / 8", 62000, 115000, 89000, 0.65, {"color": "Azul", "talla": "8", "corte": "Skinny"}),
            ("Negro / 10", 62000, 115000, 89000, 0.67, {"color": "Negro", "talla": "10", "corte": "Skinny"}),
        ],
    },
    {
        "categoria": "Pantalones",
        "nombre": "Pantalon Cargo Urban",
        "descripcion": "Pantalon cargo con seis bolsillos y ajuste en tobillo.",
        "color": "#78716C",
        "variantes": [
            ("Beige / 30", 45000, 89000, 66000, 0.55, {"color": "Beige", "talla": "30", "estilo": "Cargo"}),
            ("Verde / 32", 45000, 89000, 66000, 0.57, {"color": "Verde", "talla": "32", "estilo": "Cargo"}),
        ],
    },
    {
        "categoria": "Vestidos",
        "nombre": "Vestido Midi Floral",
        "descripcion": "Vestido midi estampado con cintura ajustable.",
        "color": "#F97316",
        "variantes": [
            ("Coral / S", 72000, 138000, 104000, 0.42, {"color": "Coral", "talla": "S", "largo": "Midi"}),
            ("Lila / M", 72000, 138000, 104000, 0.44, {"color": "Lila", "talla": "M", "largo": "Midi"}),
        ],
    },
    {
        "categoria": "Chaquetas",
        "nombre": "Chaqueta Denim Clasica",
        "descripcion": "Chaqueta denim de corte clasico con bolsillos frontales.",
        "color": "#0F4C81",
        "variantes": [
            ("Azul / M", 68000, 135000, 92000, 0.78, {"color": "Azul", "talla": "M", "material": "Denim"}),
            ("Negro / L", 68000, 135000, 92000, 0.80, {"color": "Negro", "talla": "L", "material": "Denim"}),
        ],
    },
    {
        "categoria": "Ropa Deportiva",
        "nombre": "Conjunto Deportivo Active",
        "descripcion": "Conjunto de camiseta y pantalon en tela de secado rapido.",
        "color": "#059669",
        "variantes": [
            ("Negro / M", 65000, 125000, 95000, 0.58, {"color": "Negro", "talla": "M", "piezas": 2}),
            ("Gris / L", 65000, 125000, 95000, 0.60, {"color": "Gris", "talla": "L", "piezas": 2}),
        ],
    },
    {
        "categoria": "Buzos",
        "nombre": "Hoodie Oversize Essential",
        "descripcion": "Hoodie unisex afelpado de silueta oversize.",
        "color": "#7C3AED",
        "variantes": [
            ("Arena / M", 48000, 95000, 69000, 0.62, {"color": "Arena", "talla": "M", "estilo": "Oversize"}),
            ("Negro / L", 48000, 95000, 69000, 0.65, {"color": "Negro", "talla": "L", "estilo": "Oversize"}),
        ],
    },
    {
        "categoria": "Paquetes",
        "nombre": "Combo Basicos x3",
        "descripcion": "Paquete de tres prendas basicas para iniciar inventario.",
        "color": "#DC2626",
        "paquete_estatico": True,
        "variantes": [
            ("Mixto / M", 68000, 115000, 89000, 0.75, {"color": "Mixto", "talla": "M", "unidades": 3}),
            ("Mixto / L", 68000, 115000, 89000, 0.78, {"color": "Mixto", "talla": "L", "unidades": 3}),
        ],
    },
]


CLIENTES = [
    ("Laura Martinez", "3004101001"),
    ("Moda Centro SAS", "3004101002"),
    ("Camila Rodriguez", "3004101003"),
    ("Boutique Isabella", "3004101004"),
    ("Santiago Gomez", "3004101005"),
    ("Almacen La 14", "3004101006"),
    ("Daniela Torres", "3004101007"),
    ("Distribuciones El Poblado", "3004101008"),
    ("Valentina Castro", "3004101009"),
    ("Comercializadora Andina", "3004101010"),
]


def slug(texto: str) -> str:
    normalized = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


def crear_png(titulo: str, subtitulo: str, color: str) -> bytes:
    image = Image.new("RGB", (800, 1000), color)
    draw = ImageDraw.Draw(image)
    title_font = cargar_fuente(54)
    subtitle_font = cargar_fuente(30)
    brand_font = cargar_fuente(26)

    draw.rectangle((55, 55, 745, 945), outline="white", width=5)
    draw.rectangle((90, 120, 710, 720), fill="#FFFFFF")
    draw.ellipse((260, 240, 540, 520), fill=color)
    draw.text((120, 760), titulo, fill="white", font=title_font)
    draw.text((120, 835), subtitulo, fill="white", font=subtitle_font)
    draw.text((120, 900), "VELANDIAX DISTRIBUIDORA", fill="white", font=brand_font)

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def cargar_fuente(size: int):
    fuentes = [
        "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for fuente in fuentes:
        try:
            return ImageFont.truetype(fuente, size)
        except OSError:
            continue
    return ImageFont.load_default()


def subir_imagen(carpeta: str, nombre: str, titulo: str, subtitulo: str, color: str) -> str:
    object_path = f"demo-ropa/{RUN_ID}/{carpeta}/{slug(nombre)}-{uuid.uuid4().hex[:8]}.png"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{object_path}"
    request = Request(
        upload_url,
        data=crear_png(titulo, subtitulo, color),
        method="POST",
        headers={
            "Authorization": f"Bearer {STORAGE_KEY}",
            "apikey": STORAGE_KEY,
            "Content-Type": "image/png",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Storage respondio {response.status}")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"No se pudo subir {nombre}: {detail}") from exc
    return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{object_path}"


def preparar_imagenes() -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    tasks = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        for producto in PRODUCTOS:
            tasks.append((
                "producto",
                producto["nombre"],
                None,
                executor.submit(
                    subir_imagen,
                    "productos",
                    producto["nombre"],
                    producto["nombre"],
                    "Coleccion de ropa",
                    producto["color"],
                ),
            ))
            for variante in producto["variantes"]:
                etiqueta = variante[0]
                tasks.append((
                    "variante",
                    producto["nombre"],
                    etiqueta,
                    executor.submit(
                        subir_imagen,
                        "variantes",
                        f"{producto['nombre']}-{etiqueta}",
                        producto["nombre"],
                        etiqueta,
                        producto["color"],
                    ),
                ))

    imagenes_producto = {}
    imagenes_variante = {}
    for tipo, producto, etiqueta, future in tasks:
        url = future.result()
        if tipo == "producto":
            imagenes_producto[producto] = url
        else:
            imagenes_variante[(producto, etiqueta)] = url
    return imagenes_producto, imagenes_variante


def cargar_base(imagenes_producto, imagenes_variante):
    ahora = datetime.now()
    db = SessionLocal()
    try:
        db.execute(text("""
            TRUNCATE TABLE
                imagenes_variante_producto,
                imagenes_producto,
                envios,
                paquetes_estaticos_items,
                items_pedido,
                pedido,
                clientes,
                variantes_producto,
                producto,
                categoria,
                usuarios
            RESTART IDENTITY CASCADE
        """))

        usuario = Usuario(
            nombre="Administrador VELANDIAX",
            email="admin@velandiax.com",
            password_hash=bcrypt.hashpw(b"Admin123*", bcrypt.gensalt()).decode(),
            rol="ADMINISTRADOR",
            activo=True,
        )
        db.add(usuario)

        categorias = {}
        for nombre, descripcion in CATEGORIAS:
            categoria = Categoria(nombre=nombre, descripcion=descripcion)
            db.add(categoria)
            categorias[nombre] = categoria
        db.flush()

        productos = {}
        variantes = {}
        for indice, data in enumerate(PRODUCTOS, start=1):
            producto = Producto(
                id_categoria=categorias[data["categoria"]].id_categoria,
                codigo_producto=f"VX-{indice:03d}",
                nombre=data["nombre"],
                descripcion=data["descripcion"],
                paquete_estatico=data.get("paquete_estatico", False),
                estado="ACTIVO",
            )
            db.add(producto)
            db.flush()
            productos[data["nombre"]] = producto
            db.add(ImagenProducto(
                id_producto=producto.id_producto,
                url=imagenes_producto[data["nombre"]],
                alt_text=f"{data['nombre']} - imagen principal",
                es_principal=True,
                orden=0,
                estado="ACTIVO",
            ))

            for etiqueta, costo, minorista, mayorista, peso, atributos in data["variantes"]:
                variante = VarianteProducto(
                    id_producto=producto.id_producto,
                    precio_costo=Decimal(str(costo)),
                    precio_minorista=Decimal(str(minorista)),
                    precio_mayorista=Decimal(str(mayorista)),
                    peso=Decimal(str(peso)),
                    aplica_paquete=data.get("paquete_estatico", False),
                    atributos=atributos,
                    estado="ACTIVO",
                )
                db.add(variante)
                db.flush()
                variantes[(data["nombre"], etiqueta)] = variante
                db.add(ImagenVarianteProducto(
                    id_variante=variante.id_variante,
                    url=imagenes_variante[(data["nombre"], etiqueta)],
                    alt_text=f"{data['nombre']} - {etiqueta}",
                    es_principal=True,
                    orden=0,
                    estado="ACTIVO",
                ))

        clientes = []
        for nombre, celular in CLIENTES:
            cliente = Cliente(nombre=nombre, celular=celular)
            db.add(cliente)
            clientes.append(cliente)
        db.flush()

        paquete = productos["Combo Basicos x3"]
        componentes = [
            ("Camiseta Basica Premium", "Blanco / M"),
            ("Camiseta Basica Premium", "Negro / L"),
            ("Hoodie Oversize Essential", "Arena / M"),
            ("Hoodie Oversize Essential", "Negro / L"),
            ("Conjunto Deportivo Active", "Negro / M"),
            ("Conjunto Deportivo Active", "Gris / L"),
        ]
        for producto_nombre, etiqueta in componentes:
            db.add(PaqueteEstaticoItem(
                id_paquete=paquete.id_producto,
                id_variante=variantes[(producto_nombre, etiqueta)].id_variante,
                cantidad=1,
            ))

        ventas = [
            {
                "cliente": 0,
                "estado": "ENTREGADO",
                "estado_pago": "PAGO_TOTAL",
                "mayorista": False,
                "envio": 12000,
                "fecha": ahora - timedelta(days=4),
                "items": [
                    ("Camiseta Basica Premium", "Blanco / M", 2),
                    ("Jean Skinny High Rise", "Azul / 8", 1),
                    ("Blusa Satinada Elegance", "Rosa / S", 1),
                ],
            },
            {
                "cliente": 1,
                "estado": "EN_TRANSITO",
                "estado_pago": "PAGO_50",
                "mayorista": True,
                "envio": 18000,
                "fecha": ahora - timedelta(days=2),
                "items": [
                    ("Camisa Oxford Manga Larga", "Azul / M", 6),
                    ("Pantalon Cargo Urban", "Beige / 30", 5),
                    ("Chaqueta Denim Clasica", "Azul / M", 4),
                    ("Hoodie Oversize Essential", "Negro / L", 6),
                ],
            },
            {
                "cliente": 2,
                "estado": "PREPARANDO",
                "estado_pago": "PAGO_TOTAL",
                "mayorista": False,
                "envio": 10000,
                "fecha": ahora - timedelta(hours=8),
                "items": [
                    ("Vestido Midi Floral", "Coral / S", 1),
                    ("Conjunto Deportivo Active", "Negro / M", 2),
                    ("Combo Basicos x3", "Mixto / M", 1),
                ],
            },
        ]

        pedidos = []
        for venta in ventas:
            pedido = Pedido(
                id_cliente=clientes[venta["cliente"]].id_cliente,
                estado=venta["estado"],
                estado_pago=venta["estado_pago"],
                total=Decimal("0"),
                precio_envio=Decimal(str(venta["envio"])),
                es_mayorista=venta["mayorista"],
                fecha=venta["fecha"],
            )
            db.add(pedido)
            db.flush()
            total_items = Decimal("0")
            for producto_nombre, etiqueta, cantidad in venta["items"]:
                variante = variantes[(producto_nombre, etiqueta)]
                precio = variante.precio_mayorista if venta["mayorista"] else variante.precio_minorista
                total_items += precio * cantidad
                db.add(ItemPedido(
                    id_pedido=pedido.id_pedido,
                    id_variante=variante.id_variante,
                    cantidad=cantidad,
                    precio_unitario=precio,
                ))
            pedido.total = total_items + pedido.precio_envio
            pedidos.append(pedido)

        envios = [
            Envio(
                id_pedido=pedidos[0].id_pedido,
                transportadora="Coordinadora",
                numero_guia="VEL-DEMO-001",
                estado="ENTREGADO",
                nombre_destinatario=clientes[0].nombre,
                celular_destinatario=clientes[0].celular,
                direccion="Carrera 45 # 10-25",
                ciudad="Medellin",
                departamento="Antioquia",
                codigo_postal="050021",
                notas="Venta minorista entregada satisfactoriamente.",
                costo=Decimal("12000"),
                fecha_despacho=ahora - timedelta(days=3),
                fecha_entrega=ahora - timedelta(days=1),
                fecha_creacion=ahora - timedelta(days=4),
            ),
            Envio(
                id_pedido=pedidos[1].id_pedido,
                transportadora="Servientrega",
                numero_guia="VEL-DEMO-002",
                estado="EN_TRANSITO",
                nombre_destinatario=clientes[1].nombre,
                celular_destinatario=clientes[1].celular,
                direccion="Calle 19 # 7-40 Local 12",
                ciudad="Bogota",
                departamento="Cundinamarca",
                codigo_postal="110311",
                notas="Pedido mayorista para surtir tienda.",
                costo=Decimal("18000"),
                fecha_despacho=ahora - timedelta(days=1),
                fecha_creacion=ahora - timedelta(days=2),
            ),
            Envio(
                id_pedido=pedidos[2].id_pedido,
                transportadora="Inter Rapidisimo",
                numero_guia="VEL-DEMO-003",
                estado="PREPARANDO",
                nombre_destinatario=clientes[2].nombre,
                celular_destinatario=clientes[2].celular,
                direccion="Avenida 6N # 24-18",
                ciudad="Cali",
                departamento="Valle del Cauca",
                codigo_postal="760046",
                notas="Pedido reciente en preparacion.",
                costo=Decimal("10000"),
                fecha_creacion=ahora - timedelta(hours=8),
            ),
        ]
        db.add_all(envios)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    print("Generando y subiendo imagenes de demostracion...")
    imagenes_producto, imagenes_variante = preparar_imagenes()
    print(f"Imagenes listas: {len(imagenes_producto)} productos, {len(imagenes_variante)} variantes")
    print("Vaciando y cargando la base de datos en una transaccion...")
    cargar_base(imagenes_producto, imagenes_variante)
    print("Carga de demostracion completada.")
    print("Admin: admin@velandiax.com / Admin123*")


if __name__ == "__main__":
    main()
