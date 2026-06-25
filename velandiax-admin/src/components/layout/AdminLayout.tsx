import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Tags, 
  Package, 
  ShoppingCart, 
  Users, 
  Bell, 
  UserCircle 
} from 'lucide-react';

// Estructura dinámica del menú (Fácil de escalar y asignar permisos luego)
const menuItems = [
  { name: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard size={20} /> },
  { name: 'Categorías', path: '/admin/categorias', icon: <Tags size={20} /> },
  { name: 'Productos', path: '/admin/productos', icon: <Package size={20} /> },
  { name: 'Pedidos', path: '/admin/pedidos', icon: <ShoppingCart size={20} /> },
  { name: 'Clientes', path: '/admin/clientes', icon: <Users size={20} /> },
];

export const AdminLayout = () => {
  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      
      {/* SIDEBAR (Menú Lateral) */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl z-20 hidden md:flex">
        {/* Logo / Título */}
        <div className="h-16 flex items-center px-6 bg-slate-950 border-b border-slate-800">
          <span className="text-xl font-bold text-white tracking-wider">VELANDIAX</span>
          <span className="ml-2 text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">B2B</span>
        </div>

        {/* Navegación Dinámica */}
        <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'bg-blue-600 text-white font-medium shadow-md' 
                    : 'hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Info de Usuario Inferior */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3">
            <UserCircle size={32} className="text-slate-400" />
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">Admin Principal</span>
              <span className="text-xs text-slate-500">admin@velandiax.com</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ÁREA PRINCIPAL (Header + Contenido) */}
      <div className="flex flex-col flex-1 overflow-hidden">
        
        {/* HEADER SUPERIOR */}
        <header className="h-16 bg-white border-b border-slate-200 shadow-sm flex items-center justify-between px-8 z-10">
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-slate-700">
              Panel de Administración
            </h1>
          </div>
          
          {/* Acciones del Header */}
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-slate-400 hover:text-blue-600 transition-colors cursor-pointer">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
        </header>

        {/* CONTENEDOR DINÁMICO (Aquí renderiza React Router) */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>

      </div>
    </div>
  );
};