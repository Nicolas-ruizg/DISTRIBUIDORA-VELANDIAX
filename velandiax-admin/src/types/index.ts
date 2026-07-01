// --- CATEGORÍAS ---
export interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string | null;
}

// --- IMÁGENES ---
export interface ImagenProducto {
  id_imagen: number;
  url: string;
  alt_text: string | null;
  es_principal: boolean;
  orden: number;
  estado: string;
}

export interface ImagenVariante {
  id_imagen_variante: number;
  url: string;
  alt_text: string | null;
  es_principal: boolean;
  orden: number;
  estado: string;
}

// --- VARIANTES ---
export interface Variante {
  id_variante: number;
  estado: string;
  precio_costo: number;
  precio_minorista: number;
  precio_mayorista: number;
  peso: number | null;
  aplica_paquete: boolean;
  atributos: Record<string, string>;
  imagen_principal?: string | null;
  imagenes?: ImagenVariante[];
}

// --- PRODUCTOS ---
export interface ProductoResumen {
  id_producto: number;
  codigo_producto: string;
  id_categoria: number;
  categoria: string;
  nombre: string;
  descripcion: string | null;
  paquete_estatico: boolean;
  en_oferta: boolean;          // Nuevo campo de tu backend
  precio_anterior: number | null; // Nuevo campo de tu backend
  estado: string;
  variantes: number;           // Cantidad de variantes totales
  precio_desde: number | null;
  imagen_principal: string | null;
}

export interface ProductoDetalle {
  id_producto: number;
  codigo_producto: string;
  id_categoria: number;
  categoria: string;
  nombre: string;
  descripcion: string | null;
  paquete_estatico: boolean;
  en_oferta: boolean;
  precio_anterior: number | null;
  estado: string;
  imagenes: ImagenProducto[];
  variantes: Variante[];
}

// --- PEDIDOS ---
export interface PedidoResumenResponse {
  id_pedido: number;
  id_cliente: number;
  cliente: string;
  celular: string;
  estado: string;
  estado_pago: string;
  numero_guia: string | null;
  total: number;
  precio_envio: number;
  es_mayorista: boolean;
  fecha: string;
  items: number;
}

// Interfaz para detalles extendidos del pedido
export interface ItemPedidoDetalle {
  id_item_pedido: number;
  id_variante: number;
  id_producto: number;
  producto: string;
  cantidad: number;
  precio_unitario: number;
  atributos: Record<string, string>;
}

export interface PedidoDetalleResponse extends PedidoResumenResponse {
  items_detalle: ItemPedidoDetalle[];
}

export type PedidoResumen = PedidoResumenResponse;
export type PedidoDetalle = PedidoDetalleResponse;

// --- ENVÍOS ---
export interface EnvioResponse {
  id_envio: number;
  id_pedido: number;
  transportadora: string;
  numero_guia: string;
  estado: string;
  nombre_destinatario: string;
  celular_destinatario: string;
  direccion: string;
  ciudad: string;
  departamento: string;
  codigo_postal: string | null;
  notas: string | null;
  costo: number;
  fecha_despacho: string | null;
  fecha_entrega: string | null;
  fecha_creacion: string;
}

export type Envio = EnvioResponse;

export interface PedidoSeguimiento {
  id_pedido: number;
  estado: string;
  estado_pago: string;
  numero_guia: string | null;
  estado_envio: string | null;
  transportadora: string | null;
  total: number;
  fecha: string;
  items: number;
}
