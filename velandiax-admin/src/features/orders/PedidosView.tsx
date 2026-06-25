import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, ShoppingBag, Plus } from 'lucide-react';
import apiClient from '../../api/axios';
import type { PedidoResumen } from '../../types/index';


export const PedidosView = () => {
  const [pedidos, setPedidos] = useState<PedidoResumen[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPedidos = async () => {
      try {
        const response = await apiClient.get('/admin/pedidos');
        setPedidos(response.data);
      } catch (err) {
        alert('Error al cargar los pedidos');
      } finally {
        setLoading(false);
      }
    };
    fetchPedidos();
  }, []);

  const formatearDinero = (monto: number) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);
  const formatearFecha = (fecha: string) => new Date(fecha).toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  // Función para asignar colores a los badges según el estado
  const getEstadoBadge = (estado: string) => {
    const est = estado.toUpperCase();
    if (est === 'PAGADO' || est === 'COMPLETADO' || est === 'ENTREGADO') return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    if (est === 'PENDIENTE' || est === 'PROCESANDO') return 'bg-amber-100 text-amber-700 border-amber-200';
    if (est === 'ENVIADO' || est === 'DESPACHADO') return 'bg-blue-100 text-blue-700 border-blue-200';
    if (est === 'CANCELADO' || est === 'REEMBOLSADO') return 'bg-red-100 text-red-700 border-red-200';
    return 'bg-slate-100 text-slate-700 border-slate-200';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Gestión de Pedidos</h2>
        <p className="text-slate-500 text-sm mt-1">Supervisa y actualiza el estado de las ventas</p>
        <div className="flex justify-between items-center">
            <button 
            onClick={() => navigate('/admin/pedidos/nuevo')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm font-medium shadow-sm cursor-pointer"
            >
            <Plus size={18} /> Nuevo Pedido Manual
            </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">

        {loading ? <div className="p-8 text-center text-slate-500">Cargando pedidos...</div> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                  <th className="p-4 font-medium">Pedido</th>
                  <th className="p-4 font-medium">Fecha</th>
                  <th className="p-4 font-medium">Cliente</th>
                  <th className="p-4 font-medium">Estado</th>
                  <th className="p-4 font-medium text-right">Total</th>
                  <th className="p-4 font-medium text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pedidos.map((pedido) => (
                  <tr key={pedido.id_pedido} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 text-sm font-bold text-slate-900 flex items-center gap-2">
                      <ShoppingBag size={16} className="text-slate-400"/> #{pedido.id_pedido}
                    </td>
                    <td className="p-4 text-sm text-slate-600">{formatearFecha(pedido.fecha)}</td>
                    <td className="p-4 text-sm">
                      <div className="font-bold text-slate-800">{pedido.cliente}</div>
                      <div className="text-xs text-slate-500">{pedido.celular} {pedido.es_mayorista && <span className="text-black font-bold ml-1">(Mayorista)</span>}</div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getEstadoBadge(pedido.estado)}`}>
                        {pedido.estado}
                      </span>
                    </td>
                    <td className="p-4 text-sm font-bold text-slate-900 text-right">{formatearDinero(pedido.total)}</td>
                    <td className="p-4 text-center">
                      <button 
                        onClick={() => navigate(`/admin/pedidos/${pedido.id_pedido}`)}
                        className="bg-white border border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-200 px-3 py-1.5 rounded-lg flex items-center gap-2 text-xs font-bold transition-all shadow-sm mx-auto cursor-pointer"
                      >
                        <Eye size={14} /> Ver Detalle
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};