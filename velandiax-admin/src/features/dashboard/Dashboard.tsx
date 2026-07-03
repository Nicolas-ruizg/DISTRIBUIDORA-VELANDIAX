import { useEffect, useState } from 'react';
import {
  Clock,
  DollarSign,
  Package,
  ShoppingCart,
  Users,
} from 'lucide-react';
import apiClient from '../../api/axios';

interface PedidoReciente {
  id_pedido: number;
  cliente: string;
  deposito: string | null;
  vendedor: string | null;
  estado: string;
  total: number;
  fecha: string;
}

interface Metricas {
  clientes: number;
  productos: number;
  variantes: number;
  pedidos: number;
  total_vendido: number;
}

interface VendedorFiltro {
  id_usuario: number;
  nombre: string;
  codigo_cuenta: string | null;
}

interface DepositoFiltro {
  id_deposito: string;
  nombre: string | null;
}

interface ReferenciaFiltro {
  codigo_producto: string;
  nombre: string;
}

interface DashboardData {
  success: boolean;
  metricas: Metricas;
  pedidos_recientes: PedidoReciente[];
  opciones: {
    vendedores: VendedorFiltro[];
    depositos: DepositoFiltro[];
    referencias: ReferenciaFiltro[];
  };
}

const toInputDate = (date: Date) => date.toISOString().slice(0, 10);

const getMonthStart = () => {
  const now = new Date();
  return toInputDate(new Date(now.getFullYear(), now.getMonth(), 1));
};

const getToday = () => toInputDate(new Date());

const getLast7Days = () => {
  const date = new Date();
  date.setDate(date.getDate() - 6);
  return toInputDate(date);
};

export const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [fechaDesde, setFechaDesde] = useState(getMonthStart());
  const [fechaHasta, setFechaHasta] = useState(getToday());
  const [idVendedor, setIdVendedor] = useState('');
  const [idDeposito, setIdDeposito] = useState('');
  const [referencia, setReferencia] = useState('');

  const formatearDinero = (monto: number) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(monto);

  const formatearFecha = (fechaIso: string) =>
    new Date(fechaIso).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  const fetchDashboardData = async (
    desde = fechaDesde,
    hasta = fechaHasta,
    vendedor = idVendedor,
    deposito = idDeposito,
    ref = referencia,
  ) => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/dashboard', {
        params: {
          fecha_desde: desde || undefined,
          fecha_hasta: hasta || undefined,
          id_usuario_venta: vendedor || undefined,
          id_deposito: deposito || undefined,
          referencia: ref.trim() || undefined,
        },
      });
      setData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error cargando el dashboard:', err);
      setError('No se pudo cargar la informacion del panel.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const aplicarRango = (desde: string, hasta: string) => {
    setFechaDesde(desde);
    setFechaHasta(hasta);
    fetchDashboardData(desde, hasta);
  };

  const limpiarFiltros = () => {
    const desde = getMonthStart();
    const hasta = getToday();
    setFechaDesde(desde);
    setFechaHasta(hasta);
    setIdVendedor('');
    setIdDeposito('');
    setReferencia('');
    fetchDashboardData(desde, hasta, '', '', '');
  };

  if (loading && !data) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-slate-500">
          <div className="w-10 h-10 border-4 border-slate-200 border-t-black rounded-full animate-spin" />
          <p className="font-medium">Cargando metricas del negocio...</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-700 p-6 rounded-xl border border-red-200">
          <h3 className="text-lg font-bold mb-2">Error de Conexion</h3>
          <p>{error}</p>
          <button
            onClick={() => fetchDashboardData()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Vision General</h2>
          <p className="text-slate-500 text-sm mt-1">
            Resumen filtrado por periodo, vendedor, deposito y referencia.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-3 xl:items-end">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Desde</label>
              <input
                type="date"
                value={fechaDesde}
                onChange={(e) => setFechaDesde(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-black"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Hasta</label>
              <input
                type="date"
                value={fechaHasta}
                onChange={(e) => setFechaHasta(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-black"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Vendedor</label>
              <select
                value={idVendedor}
                onChange={(e) => setIdVendedor(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none bg-white focus:ring-2 focus:ring-black"
              >
                <option value="">Todos</option>
                {data?.opciones.vendedores.map((vendedor) => (
                  <option key={vendedor.id_usuario} value={vendedor.id_usuario}>
                    {vendedor.codigo_cuenta ? `${vendedor.codigo_cuenta} - ` : ''}{vendedor.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Deposito</label>
              <select
                value={idDeposito}
                onChange={(e) => setIdDeposito(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none bg-white focus:ring-2 focus:ring-black"
              >
                <option value="">Todos</option>
                {data?.opciones.depositos.map((deposito) => (
                  <option key={deposito.id_deposito} value={deposito.id_deposito}>
                    {deposito.id_deposito} - {deposito.nombre || 'Sin nombre'}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Referencia</label>
              <input
                list="referencias-dashboard"
                value={referencia}
                onChange={(e) => setReferencia(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-black"
                placeholder="Codigo o nombre"
              />
              <datalist id="referencias-dashboard">
                {data?.opciones.referencias.map((item) => (
                  <option key={item.codigo_producto} value={item.codigo_producto}>
                    {item.nombre}
                  </option>
                ))}
              </datalist>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => fetchDashboardData()}
                className="flex-1 px-4 py-2 bg-black text-white rounded-lg text-sm font-bold hover:bg-slate-800 transition-colors"
              >
                Aplicar
              </button>
              <button
                onClick={limpiarFiltros}
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-bold hover:bg-slate-200 transition-colors"
              >
                Limpiar
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            <button onClick={() => aplicarRango(getToday(), getToday())} className="px-3 py-1.5 rounded-full bg-slate-100 text-xs font-bold text-slate-700 hover:bg-slate-200">Hoy</button>
            <button onClick={() => aplicarRango(getLast7Days(), getToday())} className="px-3 py-1.5 rounded-full bg-slate-100 text-xs font-bold text-slate-700 hover:bg-slate-200">7 dias</button>
            <button onClick={() => aplicarRango(getMonthStart(), getToday())} className="px-3 py-1.5 rounded-full bg-slate-100 text-xs font-bold text-slate-700 hover:bg-slate-200">Mes actual</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Ingresos del Periodo</p>
              <h3 className="text-2xl font-bold text-slate-900">
                {formatearDinero(data?.metricas.total_vendido || 0)}
              </h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
              <DollarSign size={20} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Pedidos del Periodo</p>
              <h3 className="text-2xl font-bold text-slate-900">{data?.metricas.pedidos || 0}</h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
              <ShoppingCart size={20} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Catalogo Activo</p>
              <h3 className="text-2xl font-bold text-slate-900">{data?.metricas.productos || 0}</h3>
              <p className="text-xs text-slate-400 mt-1">Con {data?.metricas.variantes || 0} variantes</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-black">
              <Package size={20} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Clientes Registrados</p>
              <h3 className="text-2xl font-bold text-slate-900">{data?.metricas.clientes || 0}</h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
              <Users size={20} />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Clock size={20} className="text-slate-400" />
            <h3 className="text-lg font-semibold text-slate-800">Ultimos pedidos del filtro</h3>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4 font-medium">ID Pedido</th>
                <th className="p-4 font-medium">Cliente</th>
                <th className="p-4 font-medium">Deposito</th>
                <th className="p-4 font-medium">Vendedor</th>
                <th className="p-4 font-medium">Fecha</th>
                <th className="p-4 font-medium">Estado</th>
                <th className="p-4 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data?.pedidos_recientes.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    No hay pedidos para estos filtros.
                  </td>
                </tr>
              ) : (
                data?.pedidos_recientes.map((pedido) => (
                  <tr key={pedido.id_pedido} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 text-sm font-bold text-slate-900">#{pedido.id_pedido}</td>
                    <td className="p-4 text-sm font-medium text-slate-700">{pedido.cliente}</td>
                    <td className="p-4 text-sm text-slate-500">{pedido.deposito || 'N/A'}</td>
                    <td className="p-4 text-sm text-slate-500">{pedido.vendedor || 'N/A'}</td>
                    <td className="p-4 text-sm text-slate-500">{formatearFecha(pedido.fecha)}</td>
                    <td className="p-4 text-sm">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium border bg-slate-50 text-slate-700 border-slate-200">
                        {pedido.estado}
                      </span>
                    </td>
                    <td className="p-4 text-sm font-bold text-slate-900 text-right">
                      {formatearDinero(pedido.total)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
