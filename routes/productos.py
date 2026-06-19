import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from database.connection import get_db
from database.models import (
    ImagenProducto,
    ImagenVarianteProducto,
    Producto,
    VarianteProducto,
)
from routes.admin import verificar_admin
from schemas.producto import (
    ImagenProductoCreate,
    ImagenProductoResponse,
    ImagenProductoUpdate,
    ImagenVarianteCreate,
    ImagenVarianteResponse,
    ImagenVarianteUpdate,
    ProductoCreate,
    ProductoDetalleResponse,
    ProductoResumenResponse,
    ProductoUpdate,
    VarianteCreate,
    VarianteProductoResponse,
    VarianteUpdate,
)

router = APIRouter(tags=["productos"])

TIPOS_IMAGEN_PERMITIDOS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGEN_BYTES = int(os.getenv("MAX_IMAGEN_BYTES", str(5 * 1024 * 1024)))


def _variantes_visibles(
    producto: Producto,
    incluir_variantes_inactivas: bool = False,
):
    variantes = producto.variantes
    if not incluir_variantes_inactivas:
        variantes = [
            variante for variante in variantes
            if variante.estado == "ACTIVO"
        ]
    return sorted(variantes, key=lambda item: item.id_variante)


def _imagenes_producto_visibles(
    producto: Producto,
    incluir_imagenes_inactivas: bool = False,
):
    imagenes = producto.imagenes
    if not incluir_imagenes_inactivas:
        imagenes = [imagen for imagen in imagenes if imagen.estado == "ACTIVO"]
    return sorted(
        imagenes,
        key=lambda item: (not item.es_principal, item.orden, item.id_imagen),
    )


def _imagenes_variante_visibles(
    variante: VarianteProducto,
    incluir_imagenes_inactivas: bool = False,
):
    imagenes = variante.imagenes
    if not incluir_imagenes_inactivas:
        imagenes = [imagen for imagen in imagenes if imagen.estado == "ACTIVO"]
    return sorted(
        imagenes,
        key=lambda item: (not item.es_principal, item.orden, item.id_imagen_variante),
    )


def _serializar_imagen_producto(imagen: ImagenProducto):
    return {
        "id_imagen": imagen.id_imagen,
        "url": imagen.url,
        "alt_text": imagen.alt_text,
        "es_principal": imagen.es_principal,
        "orden": imagen.orden,
        "estado": imagen.estado,
    }


def _serializar_imagen_variante(imagen: ImagenVarianteProducto):
    return {
        "id_imagen_variante": imagen.id_imagen_variante,
        "url": imagen.url,
        "alt_text": imagen.alt_text,
        "es_principal": imagen.es_principal,
        "orden": imagen.orden,
        "estado": imagen.estado,
    }


def _config_storage():
    supabase_url = os.getenv("SUPABASE_URL")
    storage_key = os.getenv("SUPABASE_STORAGE_KEY")
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "productos")

    if not supabase_url or not storage_key:
        raise HTTPException(
            status_code=500,
            detail="Faltan SUPABASE_URL o SUPABASE_STORAGE_KEY en el entorno",
        )

    return supabase_url.rstrip("/"), storage_key, bucket


def _extension_imagen(content_type: str | None) -> str:
    if content_type not in TIPOS_IMAGEN_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Use JPG, PNG, WEBP o GIF",
        )
    return TIPOS_IMAGEN_PERMITIDOS[content_type]


def _subir_imagen_storage(
    carpeta: str,
    id_entidad: int,
    contenido: bytes,
    content_type: str | None,
) -> str:
    if not contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo esta vacio",
        )
    if len(contenido) > MAX_IMAGEN_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La imagen supera el tamano maximo permitido",
        )

    extension = _extension_imagen(content_type)
    supabase_url, storage_key, bucket = _config_storage()
    object_path = f"{carpeta}/{id_entidad}/{uuid.uuid4().hex}{extension}"
    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{object_path}"

    request = Request(
        upload_url,
        data=contenido,
        method="POST",
        headers={
            "Authorization": f"Bearer {storage_key}",
            "apikey": storage_key,
            "Content-Type": content_type,
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            if response.status not in (200, 201):
                raise HTTPException(
                    status_code=502,
                    detail="Supabase Storage no pudo guardar la imagen",
                )
    except HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=502,
            detail=f"Error de Supabase Storage: {detalle}",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible conectar con Supabase Storage",
        ) from exc

    return f"{supabase_url}/storage/v1/object/public/{bucket}/{object_path}"


def _imagen_principal(producto: Producto):
    imagenes = _imagenes_producto_visibles(producto)
    return imagenes[0].url if imagenes else None


def _imagen_principal_variante(variante: VarianteProducto):
    imagenes = _imagenes_variante_visibles(variante)
    return imagenes[0].url if imagenes else None


def _serializar_producto_resumen(
    producto: Producto,
    incluir_variantes_inactivas: bool = False,
):
    variantes = _variantes_visibles(producto, incluir_variantes_inactivas)
    precios = [variante.precio_minorista for variante in variantes]
    return {
        "id_producto": producto.id_producto,
        "id_categoria": producto.id_categoria,
        "categoria": producto.categoria.nombre,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "paquete_estatico": producto.paquete_estatico,
        "estado": producto.estado,
        "variantes": len(variantes),
        "precio_desde": min(precios) if precios else None,
        "imagen_principal": _imagen_principal(producto),
    }


def _serializar_variante(
    variante: VarianteProducto,
    incluir_imagenes_inactivas: bool = False,
):
    return {
        "id_variante": variante.id_variante,
        "estado": variante.estado,
        "precio_costo": variante.precio_costo,
        "precio_minorista": variante.precio_minorista,
        "precio_mayorista": variante.precio_mayorista,
        "peso": variante.peso,
        "aplica_paquete": variante.aplica_paquete,
        "atributos": variante.atributos or {},
        "imagen_principal": _imagen_principal_variante(variante),
        "imagenes": [
            _serializar_imagen_variante(imagen)
            for imagen in _imagenes_variante_visibles(
                variante,
                incluir_imagenes_inactivas,
            )
        ],
    }


def _serializar_producto_detalle(
    producto: Producto,
    incluir_variantes_inactivas: bool = False,
    incluir_imagenes_inactivas: bool = False,
):
    return {
        "id_producto": producto.id_producto,
        "id_categoria": producto.id_categoria,
        "categoria": producto.categoria.nombre,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "paquete_estatico": producto.paquete_estatico,
        "estado": producto.estado,
        "imagenes": [
            _serializar_imagen_producto(imagen)
            for imagen in _imagenes_producto_visibles(
                producto,
                incluir_imagenes_inactivas,
            )
        ],
        "variantes": [
            _serializar_variante(variante, incluir_imagenes_inactivas)
            for variante in _variantes_visibles(
                producto,
                incluir_variantes_inactivas,
            )
        ],
    }


def _consultar_producto(
    db: Session,
    id_producto: int,
    incluir_inactivo: bool = False,
) -> Producto:
    consulta = (
        select(Producto)
        .options(
            joinedload(Producto.categoria),
            selectinload(Producto.variantes).selectinload(VarianteProducto.imagenes),
            selectinload(Producto.imagenes),
        )
        .where(Producto.id_producto == id_producto)
    )
    if not incluir_inactivo:
        consulta = consulta.where(Producto.estado == "ACTIVO")

    producto = db.scalar(consulta)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto


def _listar_productos(
    db: Session,
    id_categoria: int | None = None,
    incluir_paquetes: bool = True,
    incluir_inactivos: bool = False,
    incluir_variantes_inactivas: bool = False,
):
    consulta = (
        select(Producto)
        .options(
            joinedload(Producto.categoria),
            selectinload(Producto.variantes).selectinload(VarianteProducto.imagenes),
            selectinload(Producto.imagenes),
        )
        .order_by(Producto.nombre)
    )
    if id_categoria is not None:
        consulta = consulta.where(Producto.id_categoria == id_categoria)
    if not incluir_paquetes:
        consulta = consulta.where(Producto.paquete_estatico.is_(False))
    if not incluir_inactivos:
        consulta = consulta.where(Producto.estado == "ACTIVO")

    productos = db.scalars(consulta).all()
    return [
        _serializar_producto_resumen(producto, incluir_variantes_inactivas)
        for producto in productos
    ]


@router.get("/productos", response_model=list[ProductoResumenResponse])
def listar_productos(
    id_categoria: int | None = None,
    incluir_paquetes: bool = True,
    db: Session = Depends(get_db),
):
    return _listar_productos(
        db=db,
        id_categoria=id_categoria,
        incluir_paquetes=incluir_paquetes,
    )


@router.get("/admin/productos", response_model=list[ProductoResumenResponse])
def listar_productos_admin(
    id_categoria: int | None = None,
    incluir_paquetes: bool = True,
    incluir_inactivos: bool = True,
    incluir_variantes_inactivas: bool = True,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    return _listar_productos(
        db=db,
        id_categoria=id_categoria,
        incluir_paquetes=incluir_paquetes,
        incluir_inactivos=incluir_inactivos,
        incluir_variantes_inactivas=incluir_variantes_inactivas,
    )


@router.get("/productos/{id_producto}", response_model=ProductoDetalleResponse)
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    return _serializar_producto_detalle(_consultar_producto(db, id_producto))


@router.get("/admin/productos/{id_producto}", response_model=ProductoDetalleResponse)
def obtener_producto_admin(
    id_producto: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    return _serializar_producto_detalle(
        _consultar_producto(db, id_producto, incluir_inactivo=True),
        incluir_variantes_inactivas=True,
        incluir_imagenes_inactivas=True,
    )


@router.post(
    "/admin/productos",
    response_model=ProductoDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    producto: ProductoCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    producto_db = Producto(**producto.model_dump())
    db.add(producto_db)
    try:
        db.commit()
        db.refresh(producto_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible crear el producto",
        ) from exc
    return _serializar_producto_detalle(
        _consultar_producto(db, producto_db.id_producto, incluir_inactivo=True),
        incluir_variantes_inactivas=True,
        incluir_imagenes_inactivas=True,
    )


@router.put("/admin/productos/{id_producto}", response_model=ProductoDetalleResponse)
def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = producto.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    producto_db = db.get(Producto, id_producto)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in cambios.items():
        setattr(producto_db, campo, valor)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible actualizar el producto",
        ) from exc
    return _serializar_producto_detalle(
        _consultar_producto(db, id_producto, incluir_inactivo=True),
        incluir_variantes_inactivas=True,
        incluir_imagenes_inactivas=True,
    )


def _desmarcar_imagenes_principales(db: Session, id_producto: int):
    imagenes = db.scalars(
        select(ImagenProducto).where(
            ImagenProducto.id_producto == id_producto,
            ImagenProducto.es_principal.is_(True),
        )
    ).all()
    for imagen in imagenes:
        imagen.es_principal = False


@router.post(
    "/admin/productos/{id_producto}/imagenes",
    response_model=ImagenProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_imagen_producto(
    id_producto: int,
    imagen: ImagenProductoCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    producto_db = db.get(Producto, id_producto)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if imagen.es_principal:
        _desmarcar_imagenes_principales(db, id_producto)

    imagen_db = ImagenProducto(id_producto=id_producto, **imagen.model_dump())
    db.add(imagen_db)
    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible crear la imagen del producto",
        ) from exc
    return _serializar_imagen_producto(imagen_db)


@router.post(
    "/admin/productos/{id_producto}/imagenes/upload",
    response_model=ImagenProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def subir_imagen_producto(
    id_producto: int,
    archivo: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    es_principal: bool = Form(default=False),
    orden: int = Form(default=0),
    estado: str = Form(default="ACTIVO"),
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    if orden < 0:
        raise HTTPException(status_code=400, detail="El orden no puede ser negativo")
    if estado not in {"ACTIVO", "INACTIVO"}:
        raise HTTPException(status_code=400, detail="Estado de imagen invalido")

    producto_db = db.get(Producto, id_producto)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    contenido = archivo.file.read()
    url_publica = _subir_imagen_storage(
        carpeta="productos",
        id_entidad=id_producto,
        contenido=contenido,
        content_type=archivo.content_type,
    )

    if es_principal:
        _desmarcar_imagenes_principales(db, id_producto)

    imagen_db = ImagenProducto(
        id_producto=id_producto,
        url=url_publica,
        alt_text=alt_text,
        es_principal=es_principal,
        orden=orden,
        estado=estado,
    )
    db.add(imagen_db)
    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La imagen se subio, pero no fue posible registrarla",
        ) from exc
    return _serializar_imagen_producto(imagen_db)


@router.put(
    "/admin/productos/imagenes/{id_imagen}",
    response_model=ImagenProductoResponse,
)
def actualizar_imagen_producto(
    id_imagen: int,
    imagen: ImagenProductoUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = imagen.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    imagen_db = db.get(ImagenProducto, id_imagen)
    if not imagen_db:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    if cambios.get("es_principal") is True:
        _desmarcar_imagenes_principales(db, imagen_db.id_producto)

    for campo, valor in cambios.items():
        setattr(imagen_db, campo, valor)

    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible actualizar la imagen del producto",
        ) from exc
    return _serializar_imagen_producto(imagen_db)


def _desmarcar_imagenes_principales_variante(db: Session, id_variante: int):
    imagenes = db.scalars(
        select(ImagenVarianteProducto).where(
            ImagenVarianteProducto.id_variante == id_variante,
            ImagenVarianteProducto.es_principal.is_(True),
        )
    ).all()
    for imagen in imagenes:
        imagen.es_principal = False


@router.post(
    "/admin/variantes/{id_variante}/imagenes",
    response_model=ImagenVarianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_imagen_variante(
    id_variante: int,
    imagen: ImagenVarianteCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    variante_db = db.get(VarianteProducto, id_variante)
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    if imagen.es_principal:
        _desmarcar_imagenes_principales_variante(db, id_variante)

    imagen_db = ImagenVarianteProducto(id_variante=id_variante, **imagen.model_dump())
    db.add(imagen_db)
    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible crear la imagen de la variante",
        ) from exc
    return _serializar_imagen_variante(imagen_db)


@router.post(
    "/admin/variantes/{id_variante}/imagenes/upload",
    response_model=ImagenVarianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def subir_imagen_variante(
    id_variante: int,
    archivo: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    es_principal: bool = Form(default=False),
    orden: int = Form(default=0),
    estado: str = Form(default="ACTIVO"),
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    if orden < 0:
        raise HTTPException(status_code=400, detail="El orden no puede ser negativo")
    if estado not in {"ACTIVO", "INACTIVO"}:
        raise HTTPException(status_code=400, detail="Estado de imagen invalido")

    variante_db = db.get(VarianteProducto, id_variante)
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    contenido = archivo.file.read()
    url_publica = _subir_imagen_storage(
        carpeta="variantes",
        id_entidad=id_variante,
        contenido=contenido,
        content_type=archivo.content_type,
    )

    if es_principal:
        _desmarcar_imagenes_principales_variante(db, id_variante)

    imagen_db = ImagenVarianteProducto(
        id_variante=id_variante,
        url=url_publica,
        alt_text=alt_text,
        es_principal=es_principal,
        orden=orden,
        estado=estado,
    )
    db.add(imagen_db)
    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La imagen se subio, pero no fue posible registrarla",
        ) from exc
    return _serializar_imagen_variante(imagen_db)


@router.put(
    "/admin/variantes/imagenes/{id_imagen_variante}",
    response_model=ImagenVarianteResponse,
)
def actualizar_imagen_variante(
    id_imagen_variante: int,
    imagen: ImagenVarianteUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = imagen.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    imagen_db = db.get(ImagenVarianteProducto, id_imagen_variante)
    if not imagen_db:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    if cambios.get("es_principal") is True:
        _desmarcar_imagenes_principales_variante(db, imagen_db.id_variante)

    for campo, valor in cambios.items():
        setattr(imagen_db, campo, valor)

    try:
        db.commit()
        db.refresh(imagen_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible actualizar la imagen de la variante",
        ) from exc
    return _serializar_imagen_variante(imagen_db)


@router.post(
    "/admin/productos/{id_producto}/variantes",
    response_model=VarianteProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_variante(
    id_producto: int,
    variante: VarianteCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    if not db.get(Producto, id_producto):
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    variante_db = VarianteProducto(id_producto=id_producto, **variante.model_dump())
    db.add(variante_db)
    try:
        db.commit()
        db.refresh(variante_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible crear la variante",
        ) from exc
    return _serializar_variante(variante_db, incluir_imagenes_inactivas=True)


@router.put("/admin/variantes/{id_variante}", response_model=VarianteProductoResponse)
def actualizar_variante(
    id_variante: int,
    variante: VarianteUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = variante.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    variante_db = db.get(VarianteProducto, id_variante)
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
    for campo, valor in cambios.items():
        setattr(variante_db, campo, valor)

    try:
        db.commit()
        db.refresh(variante_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible actualizar la variante",
        ) from exc
    return _serializar_variante(variante_db, incluir_imagenes_inactivas=True)
