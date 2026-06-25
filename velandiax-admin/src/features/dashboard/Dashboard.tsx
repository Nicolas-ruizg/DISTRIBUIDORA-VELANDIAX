import { useState, useEffect } from 'react';
import { 
  Users, 
  Package, 
  ShoppingCart, 
  DollarSign,
  Clock
} from 'lucide-react';
import apiClient from '../../api/axios';

// 1. Definimos las interfaces basadas en tu backend FastAPI
interface PedidoReciente {
  id_pedido: number;
  cliente: string;
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

interface DashboardData {
  success: boolean;
  usuario: any;
  metricas: Metricas;
  pedidos_recientes: PedidoReciente[];
  timestamp: string;
}

export const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Utilidad para formatear dinero (Puedes ajustarlo a tu moneda local, ej. COP, MXN, USD)
  const formatearDinero = (monto: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(monto);
  };

  // Utilidad para formatear la fecha
  const formatearFecha = (fechaIso: string) => {
    return new Date(fechaIso).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/dashboard');
      setData(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error cargando el dashboard:', err);
      setError('No se pudo cargar la información del panel. Verifica tu conexión.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-slate-500">
          <div className="w-10 h-10 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
          <p className="font-medium">Cargando métricas de tu negocio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-700 p-6 rounded-xl border border-red-200">
          <h3 className="text-lg font-bold mb-2">Error de Conexión</h3>
          <p>{error}</p>
          <button 
            onClick={fetchDashboardData}
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
      {/* Encabezado */}
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Visión General</h2>
        <p className="text-slate-500 text-sm mt-1">
          Resumen de la actividad de tu E-commerce B2B
        </p>
      </div>

      {/* Grid de Métricas (KPIs) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Tarjeta: Total Vendido */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Ingresos Totales</p>
              <h3 className="text-2xl font-bold text-slate-900">
                {formatearDinero(data?.metricas.total_vendido || 0)}
              </h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
              <DollarSign size={20} />
            </div>
          </div>
        </div>

        {/* Tarjeta: Pedidos */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Pedidos Totales</p>
              <h3 className="text-2xl font-bold text-slate-900">
                {data?.metricas.pedidos}
              </h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
              <ShoppingCart size={20} />
            </div>
          </div>
        </div>

        {/* Tarjeta: Catálogo (Productos + Variantes) */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Catálogo Activo</p>
              <h3 className="text-2xl font-bold text-slate-900">
                {data?.metricas.productos}
              </h3>
              <p className="text-xs text-slate-400 mt-1">Con {data?.metricas.variantes} variantes</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-black">
              <Package size={20} />
            </div>
          </div>
        </div>

        {/* Tarjeta: Clientes */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Clientes Registrados</p>
              <h3 className="text-2xl font-bold text-slate-900">
                {data?.metricas.clientes}
              </h3>
            </div>
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
              <Users size={20} />
            </div>
          </div>
        </div>
      </div>

      {/* Sección de Pedidos Recientes */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Clock size={20} className="text-slate-400" />
            <h3 className="text-lg font-semibold text-slate-800">Últimos 5 Pedidos</h3>
          </div>
          <button className="text-sm text-blue-600 font-medium hover:text-blue-700 transition-colors cursor-pointer">
            Ver todos los pedidos
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4 font-medium">ID Pedido</th>
                <th className="p-4 font-medium">Cliente</th>
                <th className="p-4 font-medium">Fecha</th>
                <th className="p-4 font-medium">Estado</th>
                <th className="p-4 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data?.pedidos_recientes.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
                    Aún no hay pedidos registrados.
                  </td>
                </tr>
              ) : (
                data?.pedidos_recientes.map((pedido) => (
                  <tr key={pedido.id_pedido} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 text-sm font-bold text-slate-900">
                      #{pedido.id_pedido}
                    </td>
                    <td className="p-4 text-sm font-medium text-slate-700">
                      {pedido.cliente}
                    </td>
                    <td className="p-4 text-sm text-slate-500">
                      {formatearFecha(pedido.fecha)}
                    </td>
                    <td className="p-4 text-sm">
                      {/* Lógica de colores según estado. Ajusta los estados según tu BD */}
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        pedido.estado.toLowerCase().includes('pendiente') 
                          ? 'bg-amber-50 text-amber-700 border-amber-200' 
                          : pedido.estado.toLowerCase().includes('completado') || pedido.estado.toLowerCase().includes('pagado')
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : 'bg-slate-50 text-slate-700 border-slate-200'
                      }`}>
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