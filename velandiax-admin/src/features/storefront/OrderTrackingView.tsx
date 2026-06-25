import { useState } from 'react';
import { Search, ShoppingBag, Truck, CalendarClock, Phone, PackageCheck } from 'lucide-react';
import apiClient from '../../api/axios';
import type { PedidoSeguimiento } from '../../types/index';

const getEstadoClass = (estado: string | null) => {
  const value = (estado || '').toUpperCase();
  if (value === 'PENDIENTE') return 'bg-amber-50 text-amber-700 border-amber-200';
  if (value === 'PREPARANDO') return 'bg-blue-50 text-blue-700 border-blue-200';
  if (value === 'DESPACHADO' || value === 'EN_TRANSITO') return 'bg-slate-100 text-slate-800 border-slate-200';
  if (value === 'PAGO_50') return 'bg-amber-50 text-amber-700 border-amber-200';
  if (value === 'PAGO_TOTAL') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  return 'bg-slate-50 text-slate-700 border-slate-200';
};

export const OrderTrackingView = () => {
  const [celular, setCelular] = useState('');
  const [pedidos, setPedidos] = useState<PedidoSeguimiento[]>([]);
  const [loading, setLoading] = useState(false);
  const [consultado, setConsultado] = useState(false);
  const [error, setError] = useState('');

  const formatearDinero = (monto: number) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  const formatearFecha = (fecha: string) =>
    new Date(fecha).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const celularLimpio = celular.replace(/\D/g, '');
    if (celularLimpio.length < 7) {
      setError('Ingresa un numero de celular valido.');
      return;
    }

    setLoading(true);
    setError('');
    setConsultado(true);

    try {
      const response = await apiClient.get('/pedidos/seguimiento', {
        params: { celular: celularLimpio },
      });
      setPedidos(response.data);
    } catch (err: any) {
      setPedidos([]);
      setError(err.response?.data?.detail || 'No fue posible consultar tus pedidos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-slate-950 text-white py-14 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="w-14 h-14 rounded-full bg-white text-black flex items-center justify-center mx-auto mb-5">
            <Truck size={28} />
          </div>
          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter mb-3">
            Seguimiento del Pedido
          </h1>
          <p className="text-slate-300 font-medium">
            Ingresa el numero de celular con el que hiciste tu pedido y consulta los pedidos que siguen en proceso.
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-10">
        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 md:p-6 -mt-20 relative z-10">
          <label className="block text-xs font-black text-slate-500 uppercase tracking-widest mb-2">
            Numero de celular
          </label>
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="tel"
                value={celular}
                onChange={(e) => setCelular(e.target.value)}
                className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-black font-bold"
                placeholder="Ej: 3001234567"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-black text-white px-7 py-3 rounded-xl font-black uppercase tracking-wide hover:bg-slate-800 disabled:opacity-60 transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <Search size={18} /> {loading ? 'Consultando...' : 'Consultar'}
            </button>
          </div>
          {error && <p className="text-sm text-red-600 font-bold mt-3">{error}</p>}
        </form>

        <div className="mt-8 space-y-4">
          {loading && (
            <div className="text-center py-12">
              <div className="w-10 h-10 border-4 border-slate-200 border-t-black rounded-full animate-spin mx-auto"></div>
            </div>
          )}

          {!loading && consultado && pedidos.length === 0 && !error && (
            <div className="text-center py-16 border border-dashed border-slate-200 rounded-2xl bg-slate-50">
              <PackageCheck size={44} className="mx-auto text-slate-300 mb-3" />
              <h2 className="text-xl font-black text-slate-800">No tienes pedidos activos</h2>
              <p className="text-slate-500 mt-1">Si tu pedido ya fue entregado, no aparecera en esta lista.</p>
            </div>
          )}

          {!loading && pedidos.map((pedido) => (
            <div key={pedido.id_pedido} className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 hover:shadow-md transition-shadow">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Pedido</p>
                  <h2 className="text-2xl font-black text-slate-900 flex items-center gap-2">
                    <ShoppingBag size={22} /> #{pedido.id_pedido}
                  </h2>
                  <p className="text-sm text-slate-500 flex items-center gap-2 mt-2">
                    <CalendarClock size={15} /> {formatearFecha(pedido.fecha)}
                  </p>
                </div>

                <div className="text-left md:text-right">
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Total</p>
                  <p className="text-xl font-black text-slate-900">{formatearDinero(pedido.total)}</p>
                  <p className="text-xs text-slate-500">{pedido.items} item(s)</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5">
                <div className="border border-slate-100 rounded-xl p-3 bg-slate-50">
                  <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Estado pedido</p>
                  <span className={`inline-flex px-3 py-1 rounded-full border text-xs font-black ${getEstadoClass(pedido.estado)}`}>
                    {pedido.estado}
                  </span>
                </div>
                <div className="border border-slate-100 rounded-xl p-3 bg-slate-50">
                  <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Pago</p>
                  <span className={`inline-flex px-3 py-1 rounded-full border text-xs font-black ${getEstadoClass(pedido.estado_pago)}`}>
                    {pedido.estado_pago === 'PAGO_50' ? 'Pago 50%' : pedido.estado_pago === 'PAGO_TOTAL' ? 'Pago total' : pedido.estado_pago}
                  </span>
                </div>
                <div className="border border-slate-100 rounded-xl p-3 bg-slate-50">
                  <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Envio</p>
                  {pedido.numero_guia ? (
                    <>
                      <span className={`inline-flex px-3 py-1 rounded-full border text-xs font-black ${getEstadoClass(pedido.estado_envio)}`}>
                        {pedido.estado_envio}
                      </span>
                      <p className="text-xs text-slate-500 mt-2">{pedido.transportadora} - {pedido.numero_guia}</p>
                    </>
                  ) : (
                    <p className="text-sm font-bold text-slate-500">Sin guia generada</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
