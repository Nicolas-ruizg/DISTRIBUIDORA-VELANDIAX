import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Search, X } from 'lucide-react';
import apiClient from '../../api/axios';
import type { Categoria } from '../../types/index';

export const CategoriasView = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Estados para el Modal y Formulario
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ nombre: '', descripcion: '' });
  const [formLoading, setFormLoading] = useState(false);

  // 1. Cargar Categorías (Read)
  const fetchCategorias = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/categorias');
      setCategorias(response.data);
      setError(null);
    } catch (err: any) {
      setError('No se pudieron cargar las categorías. Verifica la conexión.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategorias();
  }, []);

  // 2. Controladores del Modal
  const openModal = (categoria?: Categoria) => {
    if (categoria) {
      setEditingId(categoria.id_categoria);
      setFormData({ 
        nombre: categoria.nombre, 
        descripcion: categoria.descripcion || '' 
      });
    } else {
      setEditingId(null);
      setFormData({ nombre: '', descripcion: '' });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setFormData({ nombre: '', descripcion: '' });
    setEditingId(null);
  };

  // 3. Crear / Actualizar (Create / Update)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      if (editingId) {
        // Actualizar
        await apiClient.put(`/admin/categorias/${editingId}`, formData);
      } else {
        // Crear
        await apiClient.post('/admin/categorias', formData);
      }
      closeModal();
      fetchCategorias(); // Refrescamos la tabla
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ocurrió un error al guardar la categoría.');
    } finally {
      setFormLoading(false);
    }
  };

  // 4. Eliminar (Delete)
  const handleDelete = async (id: number, nombre: string) => {
    if (window.confirm(`¿Estás seguro de que deseas eliminar la categoría "${nombre}"?`)) {
      try {
        await apiClient.delete(`/admin/categorias/${id}`);
        fetchCategorias(); // Refrescamos la tabla
      } catch (err: any) {
        alert(err.response?.data?.detail || 'Error al eliminar. Es posible que tenga productos asociados.');
      }
    }
  };

  return (
    <div className="space-y-6 relative">
      {/* Encabezado */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Categorías</h2>
          <p className="text-slate-500 text-sm mt-1">Gestiona las agrupaciones de tus productos</p>
        </div>
        <button 
          onClick={() => openModal()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm font-medium cursor-pointer shadow-sm"
        >
          <Plus size={18} />
          Nueva Categoría
        </button>
      </div>

      {/* Contenedor Principal (Tabla) */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Buscar categoría..." 
              className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
            />
          </div>
        </div>

        {loading && <div className="p-8 text-center text-slate-500">Cargando categorías...</div>}
        {error && !loading && <div className="p-8 text-center text-red-500">{error}</div>}

        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                  <th className="p-4 font-medium">ID</th>
                  <th className="p-4 font-medium">Nombre</th>
                  <th className="p-4 font-medium">Descripción</th>
                  <th className="p-4 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {categorias.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-500">
                      No hay categorías registradas.
                    </td>
                  </tr>
                ) : (
                  categorias.map((categoria) => (
                    <tr key={categoria.id_categoria} className="hover:bg-slate-50 transition-colors">
                      <td className="p-4 text-sm font-medium text-slate-900">#{categoria.id_categoria}</td>
                      <td className="p-4 text-sm text-slate-700 font-medium">{categoria.nombre}</td>
                      <td className="p-4 text-sm text-slate-500 truncate max-w-xs">
                        {categoria.descripcion || <span className="text-slate-300 italic">Sin descripción</span>}
                      </td>
                      <td className="p-4 flex items-center justify-end gap-3">
                        <button 
                          onClick={() => openModal(categoria)}
                          className="text-slate-400 hover:text-blue-600 transition-colors cursor-pointer" 
                          title="Editar"
                        >
                          <Edit size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(categoria.id_categoria, categoria.nombre)}
                          className="text-slate-400 hover:text-red-600 transition-colors cursor-pointer" 
                          title="Eliminar"
                        >
                          <Trash2 size={18} />
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

      {/* Modal de Creación/Edición */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-slate-100">
              <h3 className="text-lg font-bold text-slate-800">
                {editingId ? 'Editar Categoría' : 'Nueva Categoría'}
              </h3>
              <button onClick={closeModal} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Nombre de la Categoría *</label>
                <input 
                  type="text" 
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition-colors"
                  placeholder="Ej. Ropa Deportiva"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Descripción (Opcional)</label>
                <textarea 
                  rows={3}
                  value={formData.descripcion}
                  onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition-colors resize-none"
                  placeholder="Breve descripción de los productos..."
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button 
                  type="button" 
                  onClick={closeModal}
                  className="flex-1 px-4 py-2 bg-slate-100 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={formLoading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-70"
                >
                  {formLoading ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};