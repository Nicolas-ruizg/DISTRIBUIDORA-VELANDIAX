import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, MapPin, Truck, RefreshCcw, CheckCircle } from 'lucide-react';
import apiClient from '../../api/axios';
import type { PedidoDetalle, Envio } from '../../types/index';

// Lista de estados sugeridos para la tienda
const ESTADOS_PEDIDO = [
  "PENDIENTE", "PAGADO", "PREPARANDO", "ENVIADO", "ENTREGADO", "CANCELADO", "REEMBOLSADO"
];

export const PedidoDetalleView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [pedido, setPedido] = useState<PedidoDetalle | null>(null);
  const [envio, setEnvio] = useState<Envio | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [nuevoEstado, setNuevoEstado] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      // Traemos el pedido
      const res = await apiClient.get(`/admin/pedidos/${id}`);
      setPedido(res.data);
      setNuevoEstado(res.data.estado);

      // Intentamos traer la info de envío si existe
      try {
        const envioRes = await apiClient.get(`/admin/pedidos/${id}/envio`);
        setEnvio(envioRes.data);
      } catch (err) {
        setEnvio(null); // Si da 404, significa que aún no tiene envío generado
      }
    } catch (err) {
      alert('Error al cargar el detalle del pedido.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const formatearDinero = (monto: number) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  // LA FUNCIÓN ESTRELLA: Actualizar estado manualmente
  const handleActualizarEstado = async () => {
    if (!pedido || nuevoEstado === pedido.estado) return;
    
    setUpdating(true);
    try {
      // Tu backend usa model_dump(exclude_none=True), así que enviarle solo el estado actualizará únicamente ese campo
      await apiClient.put(`/admin/pedidos/${id}`, { estado: nuevoEstado });
      setPedido({ ...pedido, estado: nuevoEstado });
      alert(`El estado del pedido ha sido actualizado a ${nuevoEstado}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al actualizar el estado.');
      setNuevoEstado(pedido.estado); // Revertimos en caso de error
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Cargando detalles...</div>;
  if (!pedido) return null;

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      
      {/* Encabezado */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/admin/pedidos')} className="p-2 text-slate-400 hover:text-slate-600 bg-white rounded-lg border border-slate-200 shadow-sm cursor-pointer"><ArrowLeft size={20} /></button>
        <div>
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
            Pedido #{pedido.id_pedido}
            <span className="bg-slate-800 text-white text-xs px-3 py-1 rounded-full">{pedido.estado}</span>
          </h2>
          <p className="text-slate-500 text-sm mt-1">{new Date(pedido.fecha).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* COLUMNA IZQUIERDA (Items y Resumen) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Tabla de Artículos Comprados */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50"><h3 className="font-bold text-slate-800">Artículos del Pedido</h3></div>
            <table className="w-full text-left">
              <thead>
                <tr className="text-xs uppercase text-slate-400 border-b border-slate-100">
                  <th className="p-4">Producto</th>
                  <th className="p-4 text-center">Cant.</th>
                  <th className="p-4 text-right">Precio Un.</th>
                  <th className="p-4 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pedido.items_detalle.map(item => (
                  <tr key={item.id_item_pedido}>
                    <td className="p-4">
                      <p className="font-bold text-slate-800 text-sm">{item.producto}</p>
                      <div className="flex gap-2 mt-1">
                        {Object.entries(item.atributos).map(([k, v]) => (
                          <span key={k} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">{k}: {v}</span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 text-center font-medium text-slate-700">{item.cantidad}</td>
                    <td className="p-4 text-right text-sm text-slate-600">{formatearDinero(item.precio_unitario)}</td>
                    <td className="p-4 text-right font-bold text-slate-800">{formatearDinero(item.precio_unitario * item.cantidad)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* Totales */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col items-end gap-2">
              <div className="flex justify-between w-64 text-sm text-slate-600">
                <span>Subtotal:</span> <span>{formatearDinero(pedido.total - pedido.precio_envio)}</span>
              </div>
              <div className="flex justify-between w-64 text-sm text-slate-600">
                <span>Envío:</span> <span>{formatearDinero(pedido.precio_envio)}</span>
              </div>
              <div className="flex justify-between w-64 text-lg font-bold text-slate-900 pt-2 border-t border-slate-200">
                <span>Total:</span> <span>{formatearDinero(pedido.total)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* COLUMNA DERECHA (Acciones, Cliente, Logística) */}
        <div className="space-y-6">
          
          {/* PANEL DE CAMBIO DE ESTADO MANUAL */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 border-l-4 border-l-blue-600">
            <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2"><RefreshCcw size={18} className="text-blue-600"/> Actualizar Estado</h3>
            <p className="text-xs text-slate-500 mb-4">Modifica el estado del pedido manualmente. El cliente podrá ver este cambio.</p>
            
            <div className="flex flex-col gap-3">
              <select 
                value={nuevoEstado} 
                onChange={(e) => setNuevoEstado(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-600 text-sm font-medium"
              >
                {/* Permito escribir cualquier estado, pero doy los comunes */}
                {ESTADOS_PEDIDO.map(est => <option key={est} value={est}>{est}</option>)}
              </select>
              
              <button 
                onClick={handleActualizarEstado}
                disabled={updating || nuevoEstado === pedido.estado}
                className="w-full bg-slate-900 text-white py-2 rounded-lg text-sm font-bold hover:bg-slate-800 disabled:opacity-50 transition-colors flex justify-center items-center gap-2 cursor-pointer"
              >
                {updating ? 'Actualizando...' : <><CheckCircle size={16}/> Guardar Estado</>}
              </button>
            </div>
          </div>

          {/* Información del Cliente */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2"><User size={18} className="text-slate-400"/> Cliente</h3>
            <div className="text-sm space-y-2">
              <p><span className="text-slate-500">Nombre:</span> <span className="font-bold text-slate-800">{pedido.cliente}</span></p>
              <p><span className="text-slate-500">Cedula/NIT:</span> <span className="font-medium text-slate-800">{pedido.cedula_cliente || 'N/A'}</span></p>
              <p><span className="text-slate-500">Celular:</span> <span className="font-medium text-slate-800">{pedido.celular}</span></p>
              <p><span className="text-slate-500">Tipo:</span> {pedido.es_mayorista ? <span className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-xs font-bold">Mayorista</span> : <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold">Minorista</span>}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <h3 className="font-bold text-slate-800 mb-4">Trazabilidad</h3>
            <div className="text-sm space-y-2">
              <p><span className="text-slate-500">Deposito:</span> <span className="font-bold text-slate-800">{pedido.id_deposito}</span> {pedido.deposito && <span className="text-slate-500">({pedido.deposito})</span>}</p>
              <p><span className="text-slate-500">Canal:</span> <span className="font-bold text-slate-800">{pedido.canal_venta}</span></p>
              <p><span className="text-slate-500">Tipo envio:</span> <span className="font-bold text-slate-800">{pedido.tipo_envio || 'No aplica'}</span></p>
              <p><span className="text-slate-500">Vendedor:</span> <span className="font-bold text-slate-800">{pedido.codigo_cuenta_vendedor || 'N/A'}</span> {pedido.vendedor && <span className="text-slate-500">- {pedido.vendedor}</span>}</p>
              <p><span className="text-slate-500">Inventario:</span> <span className="font-bold text-slate-800">{pedido.codigo_cuenta_inventario || 'N/A'}</span> {pedido.inventario && <span className="text-slate-500">- {pedido.inventario}</span>}</p>
            </div>
          </div>

          {/* Información Logística (Envío) */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2"><Truck size={18} className="text-slate-400"/> Logística y Envío</h3>
            
            {envio ? (
              <div className="text-sm space-y-3">
                <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                  <p className="text-xs text-blue-600 font-bold uppercase tracking-wider mb-1">Guía de Seguimiento</p>
                  <p className="font-mono font-bold text-slate-800 text-lg">{envio.numero_guia}</p>
                  <p className="text-xs text-slate-500 mt-1">{envio.transportadora}</p>
                </div>
                <p><span className="text-slate-500">Estado logístico:</span> <span className="font-bold text-slate-800">{envio.estado}</span></p>
              </div>
            ) : (
              <div className="text-center py-4">
                <MapPin size={32} className="mx-auto text-slate-300 mb-2"/>
                <p className="text-sm text-slate-500 mb-4">No se ha generado guía de envío para este pedido.</p>
                <button className="bg-blue-50 text-blue-600 border border-blue-200 px-4 py-2 rounded-lg text-sm font-bold w-full hover:bg-blue-100 transition-colors">
                  Generar Envío
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};
