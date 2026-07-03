import { useState, useEffect } from 'react';
import { X, Trash2, ShoppingBag, ArrowLeft, MessageCircle } from 'lucide-react';
import { useCart } from '../../../context/CartContext';
import apiClient from '../../../api/axios'; // Asegúrate de tener tu cliente axios importado

interface CartModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CartModal = ({ isOpen, onClose }: CartModalProps) => {
  const { items, totalItems, esMayorista, subtotal, updateQuantity, removeFromCart, clearCart } = useCart();
  
  // Estado para controlar en qué paso estamos dentro del carrito
  const [step, setStep] = useState<'cart' | 'checkout'>('cart');
  const [saving, setSaving] = useState(false);
  
  // Datos del cliente para la creación del pedido
  const [formData, setFormData] = useState({
    nombre: '',
    cedula: '',
    celular: '',
    direccion: '',
    notas: ''
  });

  // Si se cierra el modal, reseteamos al paso inicial
  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => setStep('cart'), 300);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const formatearDinero = (monto: number) => 
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  const prendasFaltantes = Math.max(0, 6 - totalItems);
  const porcentajeProgreso = Math.min(100, (totalItems / 6) * 100);

  // --- REGISTRO EN BASE DE DATOS Y REDIRECCIÓN A WHATSAPP ---
  const handleProcessOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) return;
    
    setSaving(true);

    // 1. Armamos el payload exacto que espera tu endpoint POST /admin/pedidos
    // Tu backend espera un PedidoCreate con el objeto 'cliente' y la lista de 'items'
    const pedidoPayload = {
      cliente: { nombre: formData.nombre.trim(), cedula: formData.cedula.trim(), celular: formData.celular.trim() },
      id_deposito: 'DEP001',
      canal_venta: 'WEB',
      tipo_envio: null,
      estado: 'PENDIENTE',
      estado_pago: 'CANCELADO',
      precio_envio: 0,
      es_mayorista: esMayorista,
      total: subtotal,
      envio: null, // Sin envío generado aún, se habla por WhatsApp
      items: items.map(item => ({ id_variante: item.variante.id_variante, cantidad: item.cantidad }))
    };

    try {
      // PASO 1: Guardar en la base de datos a través de tu API de FastAPI
      // Nota: Si este endpoint público no requiere token de admin, asegúrate de que no use la dependencia verificar_admin, 
      // o ajusta la cabecera según corresponda. Aquí usamos tu estructura de persistencia.
      const res = await apiClient.post('/admin/pedidos', pedidoPayload);
      const pedidoGuardado = res.data; // Extraemos la respuesta con el id_pedido asignado por Postgres
      
      // PASO 2: Construir el mensaje estructurado de WhatsApp incluyendo el # de Pedido real de la BD
      const telefonoVelandiax = "573194215464";
      let mensaje = `¡Hola Velandiax! 🚀 Acabo de registrar el *Pedido #${pedidoGuardado.id_pedido}* en la web.\n\n`;
      mensaje += `👤 *Mis Datos:*\n`;
      mensaje += `- Nombre: ${formData.nombre}\n`;
      mensaje += `- Cedula/NIT: ${formData.cedula}\n`;
      mensaje += `- Celular: ${formData.celular}\n`;
      mensaje += `- Dirección: ${formData.direccion}\n`;
      if (formData.notas) mensaje += `- Notas: ${formData.notas}\n`;

      mensaje += `\n🛍️ *Detalle del Pedido:*\n`;
      items.forEach(item => {
        const precioUnitario = esMayorista ? item.variante.precio_mayorista : item.variante.precio_minorista;
        const atributos = Object.values(item.variante.atributos).join(' - ');
        const attrString = atributos ? ` (${atributos})` : '';
        mensaje += `▫️ ${item.cantidad}x ${item.producto.nombre}${attrString} - ${formatearDinero(precioUnitario * item.cantidad)}\n`;
      });

      mensaje += `\n📊 *Resumen de Compra:*\n`;
      mensaje += `- Tipo: ${esMayorista ? 'Por Mayor 📦' : 'Al Detal 🛍️'}\n`;
      mensaje += `- Total Neto: *${formatearDinero(subtotal)}*\n\n`;
      mensaje += `Quedo atento para coordinar el pago y confirmar el despacho del Pedido #${pedidoGuardado.id_pedido}. 👍`;

      // PASO 3: Abrir la ventana de WhatsApp
      const url = `https://wa.me/${telefonoVelandiax}?text=${encodeURIComponent(mensaje)}`;
      window.open(url, '_blank');

      // PASO 4: Limpiar estado local del carrito y cerrar
      clearCart();
      onClose();

    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || 'No fue posible registrar tu pedido en la base de datos. Inténtalo de nuevo.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={onClose} />

      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white flex flex-col shadow-2xl animate-slideLeft">
          
          {/* ENCABEZADO */}
          <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            {step === 'cart' ? (
              <h2 className="text-lg font-black text-slate-900 uppercase tracking-tight flex items-center gap-2">
                <ShoppingBag size={20} /> Tu Carrito ({totalItems})
              </h2>
            ) : (
              <div className="flex items-center gap-3">
                <button type="button" onClick={() => setStep('cart')} className="text-slate-400 hover:text-black transition-colors cursor-pointer">
                  <ArrowLeft size={20} />
                </button>
                <h2 className="text-lg font-black text-slate-900 uppercase tracking-tight">
                  Datos de Envío
                </h2>
              </div>
            )}
            
            <button onClick={onClose} className="text-slate-400 hover:text-black transition-colors p-1 cursor-pointer">
              <X size={24} />
            </button>
          </div>

          {/* PASO 1: REVISIÓN DEL CARRITO */}
          {step === 'cart' && (
            <>
              {/* INDICADOR DE MAYORISTA */}
              <div className="p-4 bg-slate-900 text-white text-xs border-b border-slate-800">
                {esMayorista ? (
                  <p className="font-bold text-center text-emerald-400 uppercase tracking-wider animate-pulse">
                    ¡Felicidades! Has desbloqueado el PRECIO MAYORISTA 🎉
                  </p>
                ) : (
                  <div className="space-y-2">
                    <p className="text-center font-medium">
                      Agrega <span className="font-black text-amber-400 text-sm">{prendasFaltantes}</span> {prendasFaltantes === 1 ? 'prenda más' : 'prendas más'} para llevarte todo a <span className="font-bold text-slate-400">Precio Mayorista</span>.
                    </p>
                    <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div className="bg-gradient-to-r from-slate-500 to-slate-500 h-full transition-all duration-500" style={{ width: `${porcentajeProgreso}%` }} />
                    </div>
                  </div>
                )}
              </div>

              {/* LISTA DE ITEMS */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 hide-scrollbar">
                {items.length === 0 ? (
                  <div className="text-center py-20 text-slate-400">
                    <ShoppingBag size={48} className="mx-auto mb-4 opacity-30" />
                    <p className="font-bold text-slate-600">Tu carrito está vacío</p>
                    <p className="text-sm mt-1">Explora nuestra tienda y añade las mejores prendas.</p>
                  </div>
                ) : (
                  items.map((item) => {
                    const precioUnidad = esMayorista ? item.variante.precio_mayorista : item.variante.precio_minorista;
                    const totalItem = precioUnidad * item.cantidad;
                    const fotoMostrar = item.variante.imagen_principal || item.variante.imagenes?.find(img => img.es_principal)?.url || item.variante.imagenes?.[0]?.url || item.producto.imagenes.find(img => img.es_principal)?.url || item.producto.imagenes[0]?.url;

                    return (
                      <div key={item.variante.id_variante} className="flex gap-4 border-b border-slate-100 pb-6 items-start">
                        <div className="w-20 h-26 bg-slate-50 rounded-lg overflow-hidden border border-slate-100 shrink-0">
                          {fotoMostrar ? <img src={fotoMostrar} alt={item.producto.nombre} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-slate-300 text-xs">Sin foto</div>}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-bold text-sm text-slate-800 uppercase tracking-tight line-clamp-1">{item.producto.nombre}</h4>
                          <div className="flex flex-wrap gap-1.5 mt-1">
                            {Object.entries(item.variante.atributos).map(([k, v]) => (
                              <span key={k} className="bg-slate-100 text-[10px] text-slate-600 px-2 py-0.5 rounded font-medium">{k}: {v}</span>
                            ))}
                          </div>
                          <div className="flex items-center gap-3 mt-3">
                            <div className="flex items-center border border-slate-200 rounded-md h-8 bg-white">
                              <button type="button" onClick={() => updateQuantity(item.variante.id_variante, item.cantidad - 1)} className="w-8 h-full flex items-center justify-center text-slate-500 hover:text-black font-bold cursor-pointer">-</button>
                              <span className="w-8 text-center text-xs font-bold text-slate-800">{item.cantidad}</span>
                              <button type="button" onClick={() => updateQuantity(item.variante.id_variante, item.cantidad + 1)} className="w-8 h-full flex items-center justify-center text-slate-500 hover:text-black font-bold cursor-pointer">+</button>
                            </div>
                            <button type="button" onClick={() => removeFromCart(item.variante.id_variante)} className="text-slate-400 hover:text-red-500 p-1 cursor-pointer transition-colors ml-auto"><Trash2 size={16} /></button>
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="font-black text-sm text-slate-900">{formatearDinero(totalItem)}</p>
                          <p className="text-[10px] text-slate-400 font-medium mt-0.5">{formatearDinero(precioUnidad)} c/u</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* BOTÓN "HACER MI PEDIDO" */}
              {items.length > 0 && (
                <div className="p-6 border-t border-slate-100 bg-slate-50 space-y-4">
                  <div className="space-y-1.5 mb-2">
                    <div className="flex justify-between text-slate-600 text-sm">
                      <span>Tipo de Compra:</span>
                      <span className={`font-bold ${esMayorista ? 'text-black' : 'text-blue-600'}`}>{esMayorista ? 'Por Mayor' : 'Al Detal'}</span>
                    </div>
                    <div className="flex justify-between text-slate-900 font-black text-xl pt-2 border-t border-slate-200">
                      <span>Subtotal:</span>
                      <span className="text-slate-900">{formatearDinero(subtotal)}</span>
                    </div>
                  </div>
                  
                  <button 
                    type="button"
                    onClick={() => setStep('checkout')}
                    className="w-full h-12 bg-[#25D366] text-white font-bold uppercase tracking-wide rounded-lg hover:bg-[#1DA851] transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg hover:shadow-xl hover:-translate-y-0.5"
                  >
                    <MessageCircle size={20} className="fill-white" />
                    Hacer mi pedido
                  </button>
                </div>
              )}
            </>
          )}

          {/* PASO 2: FORMULARIO Y PERSISTENCIA EN BASE DE DATOS */}
          {step === 'checkout' && (
            <form onSubmit={handleProcessOrder} className="flex flex-col h-full">
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                
                <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl text-center mb-2">
                  <MessageCircle size={32} className="mx-auto text-emerald-500 mb-2 fill-emerald-500" />
                  <h3 className="font-bold text-emerald-900 text-sm">Ingresa tus datos</h3>
                  <p className="text-xs text-emerald-700 mt-1">Tu pedido se guardará en el sistema y se generará tu reporte de WhatsApp.</p>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">Nombre Completo *</label>
                  <input type="text" required value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} className="w-full px-4 py-3 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#25D366] text-sm font-medium" placeholder="Ej: Juan Pérez" />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">Cedula / NIT *</label>
                  <input type="text" required value={formData.cedula} onChange={e => setFormData({...formData, cedula: e.target.value})} className="w-full px-4 py-3 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#25D366] text-sm font-medium" placeholder="Ej: 1001234567" />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">Número de Celular (WhatsApp) *</label>
                  <input type="tel" required value={formData.celular} onChange={e => setFormData({...formData, celular: e.target.value})} className="w-full px-4 py-3 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#25D366] text-sm font-medium" placeholder="Ej: 3001234567" />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">Dirección de Entrega *</label>
                  <input type="text" required value={formData.direccion} onChange={e => setFormData({...formData, direccion: e.target.value})} className="w-full px-4 py-3 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#25D366] text-sm font-medium" placeholder="Calle, Carrera, Conjunto, Ciudad" />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">Notas o indicaciones (Opcional)</label>
                  <textarea rows={2} value={formData.notas} onChange={e => setFormData({...formData, notas: e.target.value})} className="w-full px-4 py-3 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#25D366] text-sm font-medium resize-none" placeholder="Ej: Dejar en portería, color de casa..." />
                </div>
              </div>

              {/* BOTÓN FINAL DE REGISTRO SEGURO */}
              <div className="p-6 border-t border-slate-100 bg-slate-50">
                <div className="flex justify-between items-center mb-4">
                  <span className="text-sm font-bold text-slate-600">Total a pagar:</span>
                  <span className="text-xl font-black text-slate-900">{formatearDinero(subtotal)}</span>
                </div>
                <button 
                  type="submit"
                  disabled={saving}
                  className="w-full h-14 bg-[#25D366] text-white font-bold uppercase tracking-wide rounded-lg hover:bg-[#1DA851] transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg disabled:opacity-60"
                >
                  <MessageCircle size={22} className="fill-white" />
                  {saving ? 'Registrando en Base de Datos...' : 'Enviar pedido a WhatsApp'}
                </button>
              </div>
            </form>
          )}

        </div>
      </div>
    </div>
  );
};
