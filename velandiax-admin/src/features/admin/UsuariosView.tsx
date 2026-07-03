import { useEffect, useState } from 'react';
import { Edit, Plus, Save, XCircle } from 'lucide-react';
import apiClient from '../../api/axios';
import type { Deposito, UsuarioAdmin } from '../../types/index';

type RolUsuario = 'ADMINISTRADOR' | 'VENDEDOR' | 'INVENTARIO';

const emptyForm = {
  nombre: '',
  email: '',
  codigo_cuenta: '',
  password: '',
  rol: 'VENDEDOR' as RolUsuario,
  id_deposito: '',
  activo: true,
};

export const UsuariosView = () => {
  const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([]);
  const [depositos, setDepositos] = useState<Deposito[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usuariosRes, depositosRes] = await Promise.all([
        apiClient.get('/admin/usuarios'),
        apiClient.get('/admin/depositos'),
      ]);
      setUsuarios(usuariosRes.data);
      setDepositos(depositosRes.data.filter((deposito: Deposito) => deposito.activo));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const editUsuario = (usuario: UsuarioAdmin) => {
    setEditingId(usuario.id_usuario);
    setForm({
      nombre: usuario.nombre,
      email: usuario.email,
      codigo_cuenta: usuario.codigo_cuenta || '',
      password: '',
      rol: usuario.rol,
      id_deposito: usuario.id_deposito || '',
      activo: usuario.activo,
    });
  };

  const saveUsuario = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      nombre: form.nombre.trim(),
      email: form.email.trim().toLowerCase(),
      codigo_cuenta: form.codigo_cuenta.trim().toUpperCase() || null,
      rol: form.rol,
      id_deposito: form.id_deposito || null,
      activo: form.activo,
    };
    if (form.password.trim()) payload.password = form.password;

    if (editingId) {
      await apiClient.put(`/admin/usuarios/${editingId}`, payload);
    } else {
      if (!payload.password) {
        alert('La clave es obligatoria al crear un usuario.');
        return;
      }
      await apiClient.post('/admin/usuarios', payload);
    }
    resetForm();
    fetchData();
  };

  const deactivateUsuario = async (usuario: UsuarioAdmin) => {
    if (!confirm(`Deseas desactivar a ${usuario.nombre}?`)) return;
    await apiClient.delete(`/admin/usuarios/${usuario.id_usuario}`);
    fetchData();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Usuarios</h2>
        <p className="text-slate-500 text-sm mt-1">Asigna roles, codigos de cuenta y deposito operativo.</p>
      </div>

      <form onSubmit={saveUsuario} className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-4">
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Nombre</label>
          <input required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black" />
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Email</label>
          <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black" />
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Codigo cuenta</label>
          <input value={form.codigo_cuenta} onChange={(e) => setForm({ ...form, codigo_cuenta: e.target.value.toUpperCase() })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black font-bold" placeholder="VEND001" />
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Clave {editingId ? '(opcional)' : ''}</label>
          <input required={!editingId} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black" />
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Rol</label>
          <select value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value as RolUsuario })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white focus:ring-2 focus:ring-black">
            <option value="ADMINISTRADOR">Administrador</option>
            <option value="VENDEDOR">Vendedor</option>
            <option value="INVENTARIO">Inventario</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Deposito</label>
          <select value={form.id_deposito} onChange={(e) => setForm({ ...form, id_deposito: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none bg-white focus:ring-2 focus:ring-black">
            <option value="">Sin deposito / acceso admin</option>
            {depositos.map((deposito) => (
              <option key={deposito.id_deposito} value={deposito.id_deposito}>
                {deposito.id_deposito} - {deposito.nombre || 'Sin nombre'}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2 pt-6">
          <label className="flex items-center gap-2 text-sm font-bold text-slate-700">
            <input type="checkbox" checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />
            Activo
          </label>
        </div>
        <div className="flex gap-2 items-end">
          <button type="submit" className="bg-black text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2">
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
          <div className="p-8 text-center text-slate-500">Cargando usuarios...</div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="p-4">Usuario</th>
                <th className="p-4">Rol</th>
                <th className="p-4">Cuenta</th>
                <th className="p-4">Deposito</th>
                <th className="p-4">Estado</th>
                <th className="p-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {usuarios.map((usuario) => (
                <tr key={usuario.id_usuario}>
                  <td className="p-4">
                    <div className="font-bold text-slate-900">{usuario.nombre}</div>
                    <div className="text-xs text-slate-500">{usuario.email}</div>
                  </td>
                  <td className="p-4 text-sm font-bold text-slate-700">{usuario.rol}</td>
                  <td className="p-4 text-sm text-slate-600">{usuario.codigo_cuenta || 'N/A'}</td>
                  <td className="p-4 text-sm text-slate-600">{usuario.id_deposito ? `${usuario.id_deposito} - ${usuario.deposito || 'Sin nombre'}` : 'Todos / admin'}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${usuario.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {usuario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button onClick={() => editUsuario(usuario)} className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm font-bold mr-2">
                      <Edit size={14} className="inline mr-1" /> Editar
                    </button>
                    <button onClick={() => deactivateUsuario(usuario)} className="px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-sm font-bold">
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
