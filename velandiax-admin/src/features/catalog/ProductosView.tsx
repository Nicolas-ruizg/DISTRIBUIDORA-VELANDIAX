import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Search, Package, XCircle, Image as ImageIcon } from 'lucide-react';
import apiClient from '../../api/axios';
import type { ProductoResumen } from '../../types/index';

export const ProductosView = () => {
  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchProductos = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/productos');
      setProductos(response.data);
      setError(null);
    } catch (err: any) {
      setError('No se pudieron cargar los productos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  const formatearDinero = (monto: number) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);
  };

  const handleToggleEstado = async (producto: ProductoResumen) => {
    const nuevoEstado = producto.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    try {
      setProductos(productos.map(p => p.id_producto === producto.id_producto ? { ...p, estado: nuevoEstado } : p));
      await apiClient.put(`/admin/productos/${producto.id_producto}`, { estado: nuevoEstado });
    } catch (err: any) {
      alert('Error al cambiar el estado del producto.');
      fetchProductos(); 
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Catálogo de Productos</h2>
          <p className="text-slate-500 text-sm mt-1">Gestiona tu inventario, paquetes y visibilidad</p>
        </div>
        <button 
          onClick={() => navigate('/admin/productos/nuevo')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm font-medium shadow-sm cursor-pointer"
        >
          <Plus size={18} /> Nuevo Producto
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input type="text" placeholder="Buscar producto..." className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none w-64 bg-white" />
          </div>
        </div>

        {loading && <div className="p-8 text-center text-slate-500">Cargando catálogo...</div>}
        {error && !loading && <div className="p-8 text-center text-red-500">{error}</div>}

        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                  <th className="p-4 font-medium">Codigo</th>
                  <th className="p-4 font-medium">Producto</th>
                  <th className="p-4 font-medium">Categoría</th>
                  <th className="p-4 font-medium text-center">Variantes</th>
                  <th className="p-4 font-medium">Precio Base</th>
                  <th className="p-4 font-medium text-center">Visible</th>
                  <th className="p-4 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {productos.length === 0 ? (
                  <tr><td colSpan={7} className="p-8 text-center text-slate-500">No hay productos registrados.</td></tr>
                ) : (
                  productos.map((producto) => (
                    <tr key={producto.id_producto} className={`transition-colors ${producto.estado === 'INACTIVO' ? 'bg-slate-50 opacity-70' : 'hover:bg-slate-50'}`}>
                      <td className="p-4 text-sm font-bold text-slate-900">{producto.codigo_producto}</td>
                      
                      {/* --- CELDA CON MINIATURA DE IMAGEN --- */}
                      <td className="p-4 text-sm">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center shrink-0">
                            {producto.imagen_principal ? (
                              <img src={producto.imagen_principal} alt={producto.nombre} className="w-full h-full object-cover" />
                            ) : (
                              <ImageIcon className="text-slate-300" size={16} />
                            )}
                          </div>
                          <div className="flex flex-col items-start gap-1">
                            <span className="font-bold text-slate-800">{producto.nombre}</span>
                            <div className="flex flex-wrap gap-2 mt-0.5">
                              {producto.paquete_estatico && <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold text-black bg-slate-100 px-2 py-0.5 rounded-full"><Package size={10} /> Paquete</span>}
                              {producto.estado === 'INACTIVO' && <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full"><XCircle size={10} /> Inactivo</span>}
                            </div>
                          </div>
                        </div>
                      </td>

                      <td className="p-4 text-sm text-slate-600 font-medium">{producto.categoria}</td>
                      <td className="p-4 text-sm text-center">
                        <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full text-xs font-bold ${producto.variantes > 0 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                          {producto.variantes} Vars.
                        </span>
                      </td>
                      <td className="p-4 text-sm font-bold text-slate-800">
                        {producto.precio_desde ? formatearDinero(producto.precio_desde) : <span className="text-slate-400 font-normal italic">Sin precio</span>}
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center">
                          <button 
                            type="button" onClick={() => handleToggleEstado(producto)}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${producto.estado === 'ACTIVO' ? 'bg-emerald-500' : 'bg-slate-300'}`}
                          >
                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${producto.estado === 'ACTIVO' ? 'translate-x-6' : 'translate-x-1'}`} />
                          </button>
                        </div>
                      </td>
                      <td className="p-4 flex items-center justify-end gap-3">
                        <button onClick={() => navigate(`/admin/productos/${producto.id_producto}`)} className="bg-white border border-slate-200 text-slate-600 hover:text-blue-600 px-3 py-1.5 rounded-lg flex items-center gap-2 text-xs font-bold shadow-sm cursor-pointer">
                          <Edit size={14} /> Editar
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
