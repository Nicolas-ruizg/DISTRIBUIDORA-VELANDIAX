import { useState, useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingBag, Heart, Menu, X, ChevronDown, MapPin, Package, Percent } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useFavorites } from '../../context/FavoritesContext';
import { CartModal } from './components/CartModal';
import apiClient from '../../api/axios';
import type { Categoria } from '../../types/index';

const ANNOUNCEMENTS = [
  "¡ENVÍO GRATIS POR COMPRAS SUPERIORES A $150.000! 🚚",
  "🔥 DESCUENTOS DE HASTA 40% EN LA SECCIÓN SALE",
  "📦 COMPRA AL POR MAYOR DESDE 6 UNIDADES",
  "✨ NUEVA COLECCIÓN DISPONIBLE AHORA"
];

export const StoreLayout = () => {
  const navigate = useNavigate();
  const { totalItems } = useCart();
  const { favorites } = useFavorites();
  
  // Control de Modales Flotantes
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isMobileMenuOpen, setIsCartMobileMenuOpen] = useState(false);
  
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [announcementIndex, setAnnouncementIndex] = useState(0);

  useEffect(() => {
    const fetchCategorias = async () => {
      try {
        const res = await apiClient.get('/categorias');
        setCategorias(res.data);
      } catch (err) { 
        console.error("Error cargando categorías para el menú"); 
      }
    };
    fetchCategorias();

    const interval = setInterval(() => {
      setAnnouncementIndex(prev => (prev + 1) % ANNOUNCEMENTS.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-white font-sans">
      
      {/* 1. TOP BAR DINÁMICA (Slider de Anuncios) */}
      <div className="bg-black text-white text-[11px] sm:text-xs text-center py-2.5 font-bold tracking-widest uppercase overflow-hidden relative">
        <div key={announcementIndex} className="animate-fade-in-up absolute inset-0 flex items-center justify-center w-full h-full">
          {ANNOUNCEMENTS[announcementIndex]}
        </div>
        <div className="invisible">{ANNOUNCEMENTS[0]}</div>
      </div>

      {/* 2. MAIN HEADER */}
      <header className="border-b border-slate-100 sticky top-0 bg-white z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20 gap-4 lg:gap-8">
            
            {/* Menú Hamburguesa Móvil & Logo */}
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setIsCartMobileMenuOpen(true)}
                className="lg:hidden text-slate-900 cursor-pointer hover:text-black transition-colors"
              >
                <Menu size={24} />
              </button>
              <Link to="/" className="text-2xl sm:text-3xl font-black tracking-tighter text-slate-900 uppercase">
                VELANDIAX
              </Link>
            </div>

            {/* Buscador Central */}
            <div className="hidden lg:flex flex-1 max-w-2xl relative group">
              <input 
                type="text" 
                placeholder="Buscar referencias, colores, combos..." 
                className="w-full bg-slate-50 text-slate-900 px-4 py-2.5 rounded-full pl-11 focus:outline-none focus:ring-2 focus:ring-slate-300 border border-slate-200 text-sm font-medium transition-all group-hover:bg-white"
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-slate-600 transition-colors" size={18} />
              <button className="absolute right-1 top-1/2 -translate-y-1/2 bg-black text-white px-5 py-1.5 rounded-full text-xs font-bold uppercase hover:bg-slate-800 transition-colors cursor-pointer">
                Buscar
              </button>
            </div>

            {/* Iconos de Acción */}
            <div className="flex items-center gap-5 sm:gap-7 text-slate-900">
              {/* Favoritos */}
              <button onClick={() => navigate('/favoritos')} className="hover:text-red-500 transition-colors relative cursor-pointer">
                <Heart size={24} strokeWidth={1.5} />
                {favorites.length > 0 && (
                  <span className="absolute -top-1.5 -right-2 bg-slate-900 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                    {favorites.length}
                  </span>
                )}
              </button>
              
              {/* Carrito */}
              <button onClick={() => setIsCartOpen(true)} className="hover:text-black transition-colors relative cursor-pointer">
                <ShoppingBag size={24} strokeWidth={1.5} />
                {totalItems > 0 && (
                  <span className="absolute -top-1.5 -right-2 bg-red-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center animate-bounce shadow-sm">
                    {totalItems}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* 3. NAVEGACIÓN DESKTOP COMPLETA (Estructura Unificada y Centrada) */}
          <nav className="hidden lg:flex items-center justify-center gap-2 h-14 text-sm font-bold text-slate-700 uppercase tracking-wide relative border-t border-slate-50">
            
            {/* MENÚ DESPLEGABLE: CATEGORÍAS */}
            <div className="group h-full flex items-center px-4 relative cursor-pointer">
              <span className="flex items-center gap-1 text-slate-700 group-hover:text-black group-hover:scale-105 transition-all duration-200">
                Categorías <ChevronDown size={14} className="group-hover:rotate-180 transition-transform duration-300" />
              </span>
              
              {/* Dropdown de Categorías Estilo Limpio (Sin Tendencias) */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 w-64 bg-white border border-slate-100 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 rounded-b-xl p-3">
                <ul className="space-y-1 font-bold text-slate-600 capitalize text-sm">
                  {categorias.map(cat => (
                    <li key={cat.id_categoria}>
                      <Link 
                        to={`/categoria/${cat.id_categoria}`} 
                        className="block px-4 py-2.5 rounded-lg hover:bg-slate-50 hover:text-slate-800 hover:translate-x-1 transition-all"
                      >
                        {cat.nombre}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* OPCION EXTRA: ARMA TU PACA */}
            <Link 
              to="/arma-tu-paca" 
              className="px-4 h-full flex items-center text-black hover:text-slate-900 hover:scale-105 hover:bg-slate-50 transition-all duration-200 border-b-2 border-transparent hover:border-black"
            >
              Arma tu Paca
            </Link>

            {/* OPCIÓN EXTRA: SALE % */}
            <Link 
              to="/sale" 
              className="px-4 h-full flex items-center text-red-600 hover:text-red-800 hover:scale-105 hover:bg-red-50/50 transition-all duration-200 border-b-2 border-transparent hover:border-red-600"
            >
              Sale %
            </Link>

            {/* OPCIÓN EXTRA: SEGUIMIENTO DEL PEDIDO */}
            <Link 
              to="/seguimiento" 
              className="px-4 h-full flex items-center text-slate-600 hover:text-black hover:scale-105 hover:bg-slate-50 transition-all duration-200 border-b-2 border-transparent hover:border-black"
            >
              Seguimiento del pedido 📍
            </Link>

          </nav>
        </div>
      </header>

      {/* =======================================
          NUEVO: MENÚ HAMBURGUESA MÓVIL (DRAWER)
          ======================================= */}
      <div className={`fixed inset-0 z-50 overflow-hidden lg:hidden transition-all duration-300 ${isMobileMenuOpen ? 'visible' : 'invisible'}`}>
        {/* Fondo oscuro traslúcido */}
        <div 
          className={`absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 ${isMobileMenuOpen ? 'opacity-100' : 'opacity-0'}`} 
          onClick={() => setIsCartMobileMenuOpen(false)} 
        />

        {/* Panel lateral */}
        <div className={`absolute inset-y-0 left-0 max-w-full flex pr-10 transition-transform duration-300 transform ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="w-screen max-w-xs bg-white flex flex-col shadow-2xl h-full">
            
            {/* Header del menú móvil */}
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <span className="text-xl font-black text-slate-900 tracking-tighter uppercase">Menú</span>
              <button onClick={() => setIsCartMobileMenuOpen(false)} className="text-slate-400 hover:text-black p-1 cursor-pointer">
                <X size={24} />
              </button>
            </div>

            {/* Links del Menú Móvil */}
            <div className="flex-1 overflow-y-auto py-4 px-4 space-y-6">
              
              {/* Sección de Categorías Reales */}
              <div>
                <p className="text-[10px] font-black tracking-widest text-slate-400 uppercase px-3 mb-2">Colecciones</p>
                <div className="space-y-1">
                  {categorias.map(cat => (
                    <Link 
                      key={cat.id_categoria}
                      to={`/categoria/${cat.id_categoria}`}
                      onClick={() => setIsCartMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-3 py-3 rounded-xl font-bold text-sm text-slate-700 hover:bg-slate-50 active:bg-slate-100 transition-colors capitalize"
                    >
                      <span className="w-2 h-2 rounded-full bg-slate-300" />
                      {cat.nombre}
                    </Link>
                  ))}
                </div>
              </div>

              {/* Sección Opciones Extras */}
              <div>
                <p className="text-[10px] font-black tracking-widest text-slate-400 uppercase px-3 mb-2">Especiales</p>
                <div className="space-y-1">
                  <Link 
                    to="/arma-tu-paca"
                    onClick={() => setIsCartMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-3 py-3 rounded-xl font-bold text-sm text-black bg-slate-50 hover:bg-slate-50 transition-colors"
                  >
                    <Package size={18} />
                    Arma tu Paca
                  </Link>

                  <Link 
                    to="/sale"
                    onClick={() => setIsCartMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-3 py-3 rounded-xl font-bold text-sm text-red-600 bg-red-50/50 hover:bg-red-50 transition-colors"
                  >
                    <Percent size={18} />
                    Sale %
                  </Link>

                  <Link 
                    to="/seguimiento"
                    onClick={() => setIsCartMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-3 py-3 rounded-xl font-bold text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    <MapPin size={18} className="text-slate-400" />
                    Seguimiento del pedido
                  </Link>
                </div>
              </div>

            </div>

            {/* Footer inferior del menú móvil */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Velandiax Store
            </div>

          </div>
        </div>
      </div>

      {/* CONTENIDO DE LAS VISTAS */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* CART MODAL DESPLEGABLE */}
      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />

    </div>
  );
};
