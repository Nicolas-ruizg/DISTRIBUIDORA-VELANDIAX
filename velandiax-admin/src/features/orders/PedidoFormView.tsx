import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Phone, Package, Plus, Trash2, Save, ShoppingCart, Truck, MapPin } from 'lucide-react';
import apiClient from '../../api/axios';
import type { Deposito, ProductoResumen, ProductoDetalle, Variante } from '../../types/index';
import { getAuthUser } from '../../utils/auth';

type EstadoPago = 'CANCELADO' | 'PAGO_50' | 'PAGO_TOTAL';
type CanalVenta = 'PRESENCIAL' | 'WEB';
type TipoEnvio = 'CONTRAENTREGA' | 'GRATIS';

interface CartItem {
  variante: Variante;
  productoNombre: string;
  cantidad: number;
}

export const PedidoFormView = () => {
  const navigate = useNavigate();
  const user = getAuthUser();
  const [saving, setSaving] = useState(false);

  const [clienteNombre, setClienteNombre] = useState('');
  const [clienteCedula, setClienteCedula] = useState('');
  const [clienteCelular, setClienteCelular] = useState('');
  const [canalVenta, setCanalVenta] = useState<CanalVenta>('PRESENCIAL');
  const [tipoEnvio, setTipoEnvio] = useState<TipoEnvio>('CONTRAENTREGA');
  const [depositos, setDepositos] = useState<Deposito[]>([]);
  const [idDeposito, setIdDeposito] = useState('DEP001');
  const [estadoPago, setEstadoPago] = useState<EstadoPago>('PAGO_TOTAL');
  const [envioData, setEnvioData] = useState({
    transportadora: 'VELANDIAX EXPRESS',
    numero_guia: '',
    nombre_destinatario: '',
    celular_destinatario: '',
    direccion: '',
    ciudad: '',
    departamento: '',
    codigo_postal: '',
    notas: '',
  });

  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [codigoBusqueda, setCodigoBusqueda] = useState('');
  const [selectedProductoId, setSelectedProductoId] = useState<number | ''>('');
  const [variantesDisponibles, setVariantesDisponibles] = useState<Variante[]>([]);
  const [selectedVarianteId, setSelectedVarianteId] = useState<number | ''>('');
  const [cantidadItem, setCantidadItem] = useState(1);
  const [cart, setCart] = useState<CartItem[]>([]);

  useEffect(() => {
    const fetchProductos = async () => {
      try {
        const [productosRes, depositosRes] = await Promise.all([
          apiClient.get('/admin/productos', { params: { incluir_inactivos: false, incluir_variantes_inactivas: false } }),
          apiClient.get('/admin/depositos'),
        ]);
        setProductos(productosRes.data.filter((p: ProductoResumen) => p.estado === 'ACTIVO' && p.stock_total > 0));
        setDepositos(depositosRes.data);
        if (depositosRes.data.length > 0) setIdDeposito(depositosRes.data[0].id_deposito);
      } catch {
        alert('Error al cargar el catalogo.');
      }
    };
    fetchProductos();
  }, []);

  useEffect(() => {
    const fetchVariantes = async () => {
      if (selectedProductoId === '') {
        setVariantesDisponibles([]);
        setSelectedVarianteId('');
        return;
      }
      try {
        const res = await apiClient.get(`/admin/productos/${selectedProductoId}`);
        const prod: ProductoDetalle = res.data;
        setVariantesDisponibles(prod.variantes.filter(v => v.estado === 'ACTIVO' && v.stock > 0));
        setSelectedVarianteId('');
      } catch {
        alert('Error al cargar variantes.');
      }
    };
    fetchVariantes();
  }, [selectedProductoId]);

  useEffect(() => {
    if (canalVenta === 'PRESENCIAL') {
      if (estadoPago === 'PAGO_50') setEstadoPago('PAGO_TOTAL');
      setTipoEnvio('CONTRAENTREGA');
      setEnvioData(prev => ({
        ...prev,
        numero_guia: '',
        direccion: '',
        ciudad: '',
        departamento: '',
        codigo_postal: '',
        notas: '',
      }));
    }
  }, [canalVenta, estadoPago]);

  const requiereEnvio = canalVenta === 'WEB' && (estadoPago === 'PAGO_50' || estadoPago === 'PAGO_TOTAL');

  const subtotal = useMemo(() => {
    return cart.reduce((acc, item) => {
      const precio = item.variante.precio_minorista;
      return acc + (precio * item.cantidad);
    }, 0);
  }, [cart]);

  const totalPedido = subtotal;

  const formatearDinero = (monto: number) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(monto);

  const handleClienteNombreChange = (value: string) => {
    setClienteNombre(value);
    setEnvioData(prev => ({ ...prev, nombre_destinatario: value }));
  };

  const handleClienteCelularChange = (value: string) => {
    setClienteCelular(value);
    setEnvioData(prev => ({ ...prev, celular_destinatario: value }));
  };

  const handleAddToCart = () => {
    if (selectedProductoId === '' || selectedVarianteId === '' || cantidadItem < 1) return;

    const productoBase = productos.find(p => p.id_producto === selectedProductoId);
    const variante = variantesDisponibles.find(v => v.id_variante === selectedVarianteId);
    if (!productoBase || !variante) return;
    const cantidadEnCarrito = cart
      .filter(item => item.variante.id_variante === variante.id_variante)
      .reduce((acc, item) => acc + item.cantidad, 0);
    if (cantidadEnCarrito + cantidadItem > variante.stock) {
      alert(`Stock insuficiente. Disponible: ${variante.stock}, ya agregado: ${cantidadEnCarrito}.`);
      return;
    }

    const existIndex = cart.findIndex(item => item.variante.id_variante === variante.id_variante);
    if (existIndex >= 0) {
      const newCart = [...cart];
      newCart[existIndex].cantidad += cantidadItem;
      setCart(newCart);
    } else {
      setCart([...cart, { variante, productoNombre: productoBase.nombre, cantidad: cantidadItem }]);
    }

    setSelectedVarianteId('');
    setCantidadItem(1);
  };

  const seleccionarProductoPorCodigo = () => {
    const codigo = codigoBusqueda.trim().toUpperCase();
    if (!codigo) return;
    const producto = productos.find(p => p.codigo_producto.toUpperCase() === codigo);
    if (!producto) {
      alert('No encontré un producto activo con ese código.');
      return;
    }
    setSelectedProductoId(producto.id_producto);
  };

  const removeFromCart = (id_variante: number) => {
    setCart(cart.filter(item => item.variante.id_variante !== id_variante));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cart.length === 0) return alert('El pedido debe tener al menos un producto.');
    if (!clienteCedula.trim()) return alert('La cedula del cliente es obligatoria.');
    if (requiereEnvio && (!envioData.nombre_destinatario || !envioData.direccion || !envioData.ciudad)) {
      return alert('Por favor completa nombre, direccion y ciudad de envio.');
    }

    setSaving(true);

    const envioPayload = requiereEnvio ? {
      transportadora: envioData.transportadora,
      numero_guia: envioData.numero_guia.trim() === '' ? null : envioData.numero_guia.trim(),
      nombre_destinatario: envioData.nombre_destinatario,
      celular_destinatario: envioData.celular_destinatario,
      direccion: envioData.direccion,
      ciudad: envioData.ciudad,
      departamento: envioData.departamento,
      codigo_postal: envioData.codigo_postal.trim() === '' ? null : envioData.codigo_postal.trim(),
      notas: envioData.notas.trim() === '' ? null : envioData.notas.trim(),
      costo: 0,
    } : null;

    const pedidoPayload = {
      cliente: { nombre: clienteNombre, cedula: clienteCedula.trim(), celular: clienteCelular },
      id_deposito: idDeposito,
      canal_venta: canalVenta,
      tipo_envio: requiereEnvio ? tipoEnvio : null,
      estado: 'PENDIENTE',
      estado_pago: estadoPago,
      precio_envio: 0,
      es_mayorista: false,
      envio: envioPayload,
      items: cart.map(item => ({
        id_variante: item.variante.id_variante,
        cantidad: item.cantidad,
      })),
    };

    try {
      const res = await apiClient.post('/admin/pedidos', pedidoPayload);
      alert(requiereEnvio ? 'Pedido y logistica creados con exito.' : 'Pedido creado sin guia de envio.');
      if (user?.rol === 'VENDEDOR') {
        navigate('/admin/pedidos/nuevo', { replace: true });
        window.location.reload();
      } else {
        navigate(`/admin/pedidos/${res.data.id_pedido}`);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ocurrio un error al procesar el pedido.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      <div className="flex items-center gap-4">
        {user?.rol === 'ADMINISTRADOR' && (
          <button onClick={() => navigate('/admin/pedidos')} className="p-2 text-slate-400 hover:text-slate-600 bg-white rounded-lg border border-slate-200 shadow-sm cursor-pointer">
            <ArrowLeft size={20} />
          </button>
        )}
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Crear Pedido Manual</h2>
          <p className="text-slate-500 text-sm mt-1">Registra una venta desde atencion al cliente o tienda fisica</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-100 pb-3">
              <User className="text-black" size={20} /> Informacion del Cliente
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Cedula / NIT *</label>
                <input
                  type="text"
                  required
                  value={clienteCedula}
                  onChange={(e) => setClienteCedula(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black"
                  placeholder="Ej: 1001234567"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Numero de Celular *</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input
                    type="text"
                    required
                    value={clienteCelular}
                    onChange={(e) => handleClienteCelularChange(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black"
                    placeholder="Ej: 3001234567"
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">Si ya existe, el sistema lo enlazara.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Nombre Completo *</label>
                <input
                  type="text"
                  required
                  value={clienteNombre}
                  onChange={(e) => handleClienteNombreChange(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black"
                  placeholder="Nombre del cliente"
                />
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <label className="block text-sm font-bold text-slate-700 mb-2">Deposito</label>
                <select
                  required
                  value={idDeposito}
                  onChange={(e) => setIdDeposito(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white text-sm"
                >
                  {depositos.map((deposito) => (
                    <option key={deposito.id_deposito} value={deposito.id_deposito}>
                      {deposito.id_deposito} - {deposito.nombre || 'Sin nombre'}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
                <div className="flex-1">
                  <p className="font-bold text-slate-800 text-sm">Canal de venta</p>
                  <p className="text-xs text-slate-500">Actual: {canalVenta === 'PRESENCIAL' ? 'Presencial' : 'Web'}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setCanalVenta(canalVenta === 'PRESENCIAL' ? 'WEB' : 'PRESENCIAL')}
                  className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors cursor-pointer ${canalVenta === 'PRESENCIAL' ? 'bg-black' : 'bg-slate-400'}`}
                >
                  <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${canalVenta === 'PRESENCIAL' ? 'translate-x-8' : 'translate-x-1'}`} />
                </button>
              </div>
            </div>

          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex items-center gap-2">
              <Package className="text-black" size={20} />
              <h3 className="text-lg font-bold text-slate-800">Agregar Articulos</h3>
            </div>

            <div className="p-6 bg-slate-50 border-b border-slate-100">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
                <div className="md:col-span-3">
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Código</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={codigoBusqueda}
                      onChange={(e) => setCodigoBusqueda(e.target.value.toUpperCase())}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          seleccionarProductoPorCodigo();
                        }
                      }}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white text-sm font-bold uppercase"
                      placeholder="VX-001"
                    />
                    <button
                      type="button"
                      onClick={seleccionarProductoPorCodigo}
                      className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold"
                    >
                      Buscar
                    </button>
                  </div>
                </div>

                <div className="md:col-span-3">
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Producto</label>
                  <select
                    value={selectedProductoId}
                    onChange={(e) => {
                      const value = e.target.value ? Number(e.target.value) : '';
                      setSelectedProductoId(value);
                      const producto = productos.find(p => p.id_producto === value);
                      if (producto) setCodigoBusqueda(producto.codigo_producto);
                    }}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white text-sm"
                  >
                    <option value="">Seleccione...</option>
                    {productos.map(p => <option key={p.id_producto} value={p.id_producto}>{p.codigo_producto} - {p.nombre}</option>)}
                  </select>
                </div>

                <div className="md:col-span-4">
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Variante (SKU)</label>
                  <select value={selectedVarianteId} onChange={(e) => setSelectedVarianteId(e.target.value ? Number(e.target.value) : '')} disabled={!selectedProductoId} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white text-sm disabled:bg-slate-100">
                    <option value="">{selectedProductoId ? 'Seleccione...' : 'Primero elija un producto'}</option>
                    {variantesDisponibles.map(v => {
                      const attrs = Object.values(v.atributos).join(' - ') || 'Unica';
                      const precioStr = formatearDinero(v.precio_minorista);
                      return <option key={v.id_variante} value={v.id_variante}>ID:{v.id_variante} | {attrs} ({precioStr}) | Stock: {v.stock}</option>;
                    })}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Cant.</label>
                  <input type="number" min="1" value={cantidadItem} onChange={e => setCantidadItem(Number(e.target.value))} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none text-center" />
                </div>

                <div className="md:col-span-1">
                  <button type="button" onClick={handleAddToCart} disabled={!selectedVarianteId} className="w-full h-[38px] bg-black text-white rounded-lg flex items-center justify-center hover:bg-slate-800 disabled:opacity-50 cursor-pointer">
                    <Plus size={18} />
                  </button>
                </div>
              </div>
            </div>

            <table className="w-full text-left">
              <thead>
                <tr className="text-xs uppercase text-slate-400 border-b border-slate-100 bg-white">
                  <th className="p-4">Item</th>
                  <th className="p-4 text-center">Cant.</th>
                  <th className="p-4 text-right">Precio Un.</th>
                  <th className="p-4 text-right">Total</th>
                  <th className="p-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {cart.length === 0 ? (
                  <tr><td colSpan={5} className="p-8 text-center text-slate-400">El carrito esta vacio. Agrega productos arriba.</td></tr>
                ) : (
                  cart.map((item, idx) => {
                    const precio = item.variante.precio_minorista;
                    return (
                      <tr key={idx}>
                        <td className="p-4">
                          <p className="font-bold text-slate-800 text-sm">{item.productoNombre}</p>
                          <p className="text-xs text-slate-500">{Object.entries(item.variante.atributos).map(([k, v]) => `${k}: ${v}`).join(', ') || 'Variante unica'}</p>
                        </td>
                        <td className="p-4 text-center font-bold text-slate-700">{item.cantidad}</td>
                        <td className="p-4 text-right text-sm text-slate-600">{formatearDinero(precio)}</td>
                        <td className="p-4 text-right font-bold text-slate-800">{formatearDinero(precio * item.cantidad)}</td>
                        <td className="p-4 text-center">
                          <button type="button" onClick={() => removeFromCart(item.variante.id_variante)} className="text-red-400 hover:text-red-600 cursor-pointer p-1"><Trash2 size={16} /></button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sticky top-6">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-100 pb-3">
              <ShoppingCart className="text-black" size={20} /> Resumen de Venta
            </h3>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Estado de Pago</label>
                <select value={estadoPago} onChange={(e) => setEstadoPago(e.target.value as EstadoPago)} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black font-medium">
                  <option value="PAGO_TOTAL">Pago total</option>
                  {canalVenta === 'WEB' && <option value="PAGO_50">Pago 50%</option>}
                  <option value="CANCELADO">Cancelado / sin pago</option>
                </select>
                <p className="text-xs text-slate-400 mt-1">
                  {canalVenta === 'PRESENCIAL'
                    ? 'En venta presencial no se genera guia ni pago 50%.'
                    : 'Con pago 50% o total se genera guia de envio automaticamente.'}
                </p>
              </div>

              {requiereEnvio && (
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Tipo de envío</label>
                  <select
                    value={tipoEnvio}
                    onChange={(e) => setTipoEnvio(e.target.value as TipoEnvio)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black font-medium"
                  >
                    <option value="CONTRAENTREGA">Pago contraentrega</option>
                    <option value="GRATIS">Envío gratis</option>
                  </select>
                  <p className="text-xs text-slate-400 mt-1">No se escribe valor manual de envío.</p>
                </div>
              )}
            </div>

            {requiereEnvio && (
              <div className="border border-slate-200 rounded-xl p-4 mb-6 space-y-3 bg-slate-50">
                <h4 className="text-sm font-black text-slate-800 flex items-center gap-2 uppercase">
                  <Truck size={16} /> Datos de envio
                </h4>
                <input type="text" value={envioData.transportadora} onChange={e => setEnvioData({ ...envioData, transportadora: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Transportadora" />
                <input type="text" value={envioData.nombre_destinatario} onChange={e => setEnvioData({ ...envioData, nombre_destinatario: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Nombre destinatario *" />
                <input type="text" value={envioData.celular_destinatario} onChange={e => setEnvioData({ ...envioData, celular_destinatario: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Celular destinatario" />
                <div className="relative">
                  <MapPin className="absolute left-3 top-2.5 text-slate-400" size={16} />
                  <input type="text" value={envioData.direccion} onChange={e => setEnvioData({ ...envioData, direccion: e.target.value })} className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Direccion *" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input type="text" value={envioData.ciudad} onChange={e => setEnvioData({ ...envioData, ciudad: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Ciudad *" />
                  <input type="text" value={envioData.departamento} onChange={e => setEnvioData({ ...envioData, departamento: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Departamento" />
                </div>
                <input type="text" value={envioData.numero_guia} onChange={e => setEnvioData({ ...envioData, numero_guia: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white" placeholder="Numero de guia opcional" />
                <textarea rows={2} value={envioData.notas} onChange={e => setEnvioData({ ...envioData, notas: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black text-sm bg-white resize-none" placeholder="Notas de entrega" />
              </div>
            )}

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2 mb-6">
              <div className="flex justify-between text-sm text-slate-600">
                <span>Subtotal Items:</span> <span>{formatearDinero(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm text-slate-600">
                <span>Envio:</span>
                <span>
                  {requiereEnvio
                    ? tipoEnvio === 'GRATIS' ? 'Gratis' : 'Contraentrega'
                    : 'No aplica'}
                </span>
              </div>
              <div className="flex justify-between text-xl font-bold text-slate-900 pt-3 border-t border-slate-200 mt-2">
                <span>TOTAL:</span> <span className="text-black">{formatearDinero(totalPedido)}</span>
              </div>
            </div>

            <button type="submit" disabled={saving || cart.length === 0} className="w-full bg-slate-900 text-white py-3 rounded-xl font-bold hover:bg-slate-800 disabled:opacity-50 transition-colors flex justify-center items-center gap-2 cursor-pointer">
              <Save size={18} /> {saving ? 'Registrando...' : 'Confirmar y Crear Pedido'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
