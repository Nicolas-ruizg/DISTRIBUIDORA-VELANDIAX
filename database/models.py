from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False, default="ADMINISTRADOR")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime)


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'INACTIVO')", name="ck_producto_estado_orm"),
    )

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_categoria: Mapped[int] = mapped_column(
        ForeignKey("categoria.id_categoria"),
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    paquete_estatico: Mapped[bool] = mapped_column(Boolean, default=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")

    categoria: Mapped[Categoria] = relationship(back_populates="productos")
    variantes: Mapped[list["VarianteProducto"]] = relationship(
        back_populates="producto",
        cascade="all, delete-orphan",
    )
    imagenes: Mapped[list["ImagenProducto"]] = relationship(
        back_populates="producto",
        cascade="all, delete-orphan",
    )


class ImagenProducto(Base):
    __tablename__ = "imagenes_producto"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('ACTIVO', 'INACTIVO')",
            name="ck_imagen_producto_estado_orm",
        ),
        CheckConstraint("orden >= 0", name="ck_imagen_producto_orden_orm"),
    )

    id_imagen: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200))
    es_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    producto: Mapped[Producto] = relationship(back_populates="imagenes")


class VarianteProducto(Base):
    __tablename__ = "variantes_producto"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('ACTIVO', 'INACTIVO')",
            name="ck_variante_producto_estado_orm",
        ),
    )

    id_variante: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto"),
        nullable=False,
    )
    precio_costo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    precio_minorista: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    precio_mayorista: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    peso: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    aplica_paquete: Mapped[bool] = mapped_column(Boolean, default=False)
    atributos: Mapped[dict | None] = mapped_column(JSONB)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")

    producto: Mapped[Producto] = relationship(back_populates="variantes")
    items_pedido: Mapped[list["ItemPedido"]] = relationship(back_populates="variante")
    imagenes: Mapped[list["ImagenVarianteProducto"]] = relationship(
        back_populates="variante",
        cascade="all, delete-orphan",
    )


class ImagenVarianteProducto(Base):
    __tablename__ = "imagenes_variante_producto"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('ACTIVO', 'INACTIVO')",
            name="ck_imagen_variante_producto_estado_orm",
        ),
        CheckConstraint("orden >= 0", name="ck_imagen_variante_producto_orden_orm"),
    )

    id_imagen_variante: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_variante: Mapped[int] = mapped_column(
        ForeignKey("variantes_producto.id_variante", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200))
    es_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    variante: Mapped[VarianteProducto] = relationship(back_populates="imagenes")


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True)
    celular: Mapped[str | None] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("clientes.id_cliente"),
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    precio_envio: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    es_mayorista: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
    items: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
    )
    envio: Mapped[Envio | None] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id_item_pedido: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pedido: Mapped[int] = mapped_column(
        ForeignKey("pedido.id_pedido", ondelete="CASCADE"),
        nullable=False,
    )
    id_variante: Mapped[int] = mapped_column(
        ForeignKey("variantes_producto.id_variante"),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship(back_populates="items")
    variante: Mapped[VarianteProducto] = relationship(back_populates="items_pedido")


class PaqueteEstaticoItem(Base):
    __tablename__ = "paquetes_estaticos_items"

    id_paquete: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto", ondelete="CASCADE"),
        primary_key=True,
    )
    id_variante: Mapped[int] = mapped_column(
        ForeignKey("variantes_producto.id_variante", ondelete="CASCADE"),
        primary_key=True,
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)


class Envio(Base):
    __tablename__ = "envios"
    __table_args__ = (
        CheckConstraint("costo >= 0", name="ck_envios_costo_orm"),
    )

    id_envio: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pedido: Mapped[int] = mapped_column(
        ForeignKey("pedido.id_pedido", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    transportadora: Mapped[str | None] = mapped_column(String(120))
    numero_guia: Mapped[str | None] = mapped_column(String(120), unique=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDIENTE")
    nombre_destinatario: Mapped[str] = mapped_column(String(200), nullable=False)
    celular_destinatario: Mapped[str | None] = mapped_column(String(20))
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str | None] = mapped_column(String(100))
    codigo_postal: Mapped[str | None] = mapped_column(String(20))
    notas: Mapped[str | None] = mapped_column(Text)
    costo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    fecha_despacho: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    pedido: Mapped[Pedido] = relationship(back_populates="envio")
