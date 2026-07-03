import { useEffect, useState } from 'react';
import { Edit, Plus, Save, XCircle } from 'lucide-react';
import apiClient from '../../api/axios';
import type { Deposito } from '../../types/index';

export const DepositosView = () => {
  const [depositos, setDepositos] = useState<Deposito[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ id_deposito: '', nombre: '', activo: true });

  const fetchDepositos = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/admin/depositos');
      setDepositos(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDepositos();
  }, []);

  const resetForm = () => {
    setEditingId(null);
    setForm({ id_deposito: '', nombre: '', activo: true });
  };

  const editDeposito = (deposito: Deposito) => {
    setEditingId(deposito.id_deposito);
    setForm({
      id_deposito: deposito.id_deposito,
      nombre: deposito.nombre || '',
      activo: deposito.activo,
    });
  };

  const saveDeposito = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      id_deposito: form.id_deposito.trim().toUpperCase(),
      nombre: form.nombre.trim() || null,
      activo: form.activo,
    };

    if (editingId) {
      await apiClient.put(`/admin/depositos/${editingId}`, {
        nombre: payload.nombre,
        activo: payload.activo,
      });
    } else {
      await apiClient.post('/admin/depositos', payload);
    }
    resetForm();
    fetchDepositos();
  };

  const deactivateDeposito = async (deposito: Deposito) => {
    if (!confirm(`Deseas desactivar ${deposito.id_deposito}?`)) return;
    await apiClient.delete(`/admin/depositos/${deposito.id_deposito}`);
    fetchDepositos();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Depositos</h2>
        <p className="text-slate-500 text-sm mt-1">Administra ubicaciones y asignaciones de inventario.</p>
      </div>

      <form onSubmit={saveDeposito} className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">ID Deposito</label>
          <input
            required
            disabled={Boolean(editingId)}
            value={form.id_deposito}
            onChange={(e) => setForm({ ...form, id_deposito: e.target.value.toUpperCase() })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black disabled:bg-slate-100 font-bold"
            placeholder="DEP001"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Nombre</label>
          <input
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black"
            placeholder="Principal, Bodega Norte..."
          />
        </div>
        <div className="flex gap-2 items-center">
          <label className="flex items-center gap-2 text-sm font-bold text-slate-700">
            <input type="checkbox" checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />
            Activo
          </label>
          <button type="submit" className="ml-auto bg-black text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2">
            {editingId ? <Save size={16} /> : <Plus size={16} />}
            {editingId ? 'Guardar' : 'Crear'}
          </button>
          {editingId && (
            <button type="button" onClick={resetForm} className="px-3 py-2 rounded-lg bg-slate-100 text-slate-700 font-bold">
              Cancelar
            </button>
          )}
        </div>
      </form>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Cargando depositos...</div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="p-4">ID</th>
                <th className="p-4">Nombre</th>
                <th className="p-4">Estado</th>
                <th className="p-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {depositos.map((deposito) => (
                <tr key={deposito.id_deposito}>
                  <td className="p-4 font-bold text-slate-900">{deposito.id_deposito}</td>
                  <td className="p-4 text-slate-700">{deposito.nombre || 'Sin nombre'}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${deposito.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {deposito.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button onClick={() => editDeposito(deposito)} className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm font-bold mr-2">
                      <Edit size={14} className="inline mr-1" /> Editar
                    </button>
                    <button onClick={() => deactivateDeposito(deposito)} className="px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-sm font-bold">
                      <XCircle size={14} className="inline mr-1" /> Desactivar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
