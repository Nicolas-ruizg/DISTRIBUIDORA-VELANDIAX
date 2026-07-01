import { NavLink, Outlet } from 'react-router-dom';
import type { ReactNode } from 'react';
import {
  Bell,
  LayoutDashboard,
  LogOut,
  Package,
  ShoppingCart,
  Tags,
  UserCircle,
  Users,
} from 'lucide-react';
import { clearAuth, getAuthUser, type UserRole } from '../../utils/auth';

const menuItems: Array<{
  name: string;
  path: string;
  icon: ReactNode;
  roles: UserRole[];
}> = [
  { name: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard size={20} />, roles: ['ADMINISTRADOR'] },
  { name: 'Categorias', path: '/admin/categorias', icon: <Tags size={20} />, roles: ['ADMINISTRADOR', 'INVENTARIO'] },
  { name: 'Productos', path: '/admin/productos', icon: <Package size={20} />, roles: ['ADMINISTRADOR', 'INVENTARIO'] },
  { name: 'Registrar Venta', path: '/admin/pedidos/nuevo', icon: <ShoppingCart size={20} />, roles: ['ADMINISTRADOR', 'VENDEDOR'] },
  { name: 'Historial de Ventas', path: '/admin/pedidos', icon: <Users size={20} />, roles: ['ADMINISTRADOR'] },
];

export const AdminLayout = () => {
  const user = getAuthUser();
  const visibleMenuItems = menuItems.filter((item) => user && item.roles.includes(user.rol));

  const handleLogout = () => {
    clearAuth();
    window.location.href = '/admin/login';
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl z-20 hidden md:flex">
        <div className="h-16 flex items-center px-6 bg-slate-950 border-b border-slate-800">
          <span className="text-xl font-bold text-white tracking-wider">VELANDIAX</span>
          <span className="ml-2 text-xs bg-black text-white border border-slate-700 px-2 py-0.5 rounded-full">
            {user?.rol || 'PANEL'}
          </span>
        </div>

        <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
          {visibleMenuItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-black text-white font-medium shadow-md ring-1 ring-slate-700'
                    : 'hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-4">
            <UserCircle size={32} className="text-slate-400" />
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">{user?.nombre || 'Usuario'}</span>
              <span className="text-xs text-slate-500">{user?.email || user?.rol}</span>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm font-bold text-slate-300 hover:bg-white hover:text-black transition-colors cursor-pointer"
          >
            <LogOut size={16} />
            Cerrar sesion
          </button>
        </div>
      </aside>

      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 shadow-sm flex items-center justify-between px-8 z-10">
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-slate-700">Panel de Administracion</h1>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 text-slate-400 hover:text-black transition-colors cursor-pointer">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
