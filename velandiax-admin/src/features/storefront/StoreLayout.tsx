import { useEffect, useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import {
  Heart,
  Camera,
  Mail,
  MapPin,
  MapPinned,
  Music2,
  Package,
  Percent,
  Phone,
  Search,
  ShoppingBag,
  Truck,
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useFavorites } from '../../context/FavoritesContext';
import { CartModal } from './components/CartModal';
import apiClient from '../../api/axios';
import type { Categoria } from '../../types/index';

const ANNOUNCEMENTS = [
  'ENVIO GRATIS EN COMPRAS SELECCIONADAS',
  'NUEVAS PACAS Y REFERENCIAS DISPONIBLES',
  'VENTA POR UNIDAD Y POR PACA',
  'ASESORIA POR WHATSAPP PARA TU PEDIDO',
];

const CONTACT = {
  email: 'ventas@velandiax.com.co',
  phone: '+57 304 217 6422',
  whatsapp: '573042176422',
  tiktok: 'https://www.tiktok.com/@velandiaxsas?_r=1&_t=ZS-98IsDKl2Asu',
  instagram: 'https://www.instagram.com/velandiax',
};

const ADDRESSES = [
  'Calle 11 #11-56 centro comercial El Legado, 4 piso',
  'Calle 21 #10-07 centro comercial Milán local 121-122 oficina 203',
];

const WhatsAppLogo = ({ className = 'h-8 w-8' }: { className?: string }) => (
  <svg viewBox="0 0 32 32" className={className} fill="currentColor" aria-hidden="true">
    <path d="M16.01 3.2C8.96 3.2 3.23 8.91 3.23 15.93c0 2.42.68 4.7 1.87 6.63L3.2 28.8l6.42-1.83a12.77 12.77 0 0 0 6.39 1.71c7.05 0 12.78-5.71 12.78-12.75S23.06 3.2 16.01 3.2Zm0 23.1a10.38 10.38 0 0 1-5.48-1.57l-.39-.24-3.81 1.09 1.12-3.69-.25-.4a10.27 10.27 0 0 1-1.59-5.56c0-5.7 4.66-10.34 10.4-10.34 5.73 0 10.39 4.64 10.39 10.34 0 5.72-4.66 10.37-10.39 10.37Zm5.7-7.76c-.31-.16-1.84-.9-2.13-1-.28-.1-.49-.16-.7.16-.2.3-.8 1-.98 1.2-.18.2-.36.23-.67.08-.31-.16-1.31-.48-2.5-1.54a9.35 9.35 0 0 1-1.73-2.15c-.18-.31-.02-.48.14-.63.14-.14.31-.36.47-.54.16-.18.2-.31.31-.52.1-.2.05-.39-.03-.54-.08-.16-.7-1.68-.95-2.3-.25-.6-.5-.51-.7-.52h-.6c-.2 0-.54.08-.82.39-.28.31-1.08 1.06-1.08 2.57 0 1.52 1.11 2.99 1.27 3.2.15.2 2.18 3.32 5.28 4.65.74.32 1.31.51 1.76.65.74.23 1.41.2 1.94.12.59-.09 1.84-.75 2.1-1.47.26-.72.26-1.34.18-1.47-.08-.13-.29-.2-.6-.36Z" />
  </svg>
);

const getCategoryInitial = (name: string) => name.trim().charAt(0).toUpperCase() || 'V';

export const StoreLayout = () => {
  const navigate = useNavigate();
  const { totalItems } = useCart();
  const { favorites } = useFavorites();

  const [isCartOpen, setIsCartOpen] = useState(false);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [announcementIndex, setAnnouncementIndex] = useState(0);

  useEffect(() => {
    const fetchCategorias = async () => {
      try {
        const res = await apiClient.get('/categorias');
        setCategorias(res.data);
      } catch (err) {
        console.error('Error cargando categorias para la tienda', err);
      }
    };

    fetchCategorias();

    const interval = setInterval(() => {
      setAnnouncementIndex((prev) => (prev + 1) % ANNOUNCEMENTS.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-white font-sans">
      <div className="bg-black text-white text-[11px] sm:text-xs text-center py-2.5 font-bold tracking-widest uppercase overflow-hidden relative">
        <div key={announcementIndex} className="animate-fade-in-up absolute inset-0 flex items-center justify-center w-full h-full">
          {ANNOUNCEMENTS[announcementIndex]}
        </div>
        <div className="invisible">{ANNOUNCEMENTS[0]}</div>
      </div>

      <header className="border-b border-slate-100 sticky top-0 bg-white z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20 gap-4 lg:gap-8">
            <Link to="/" className="text-2xl sm:text-3xl font-black tracking-tighter text-slate-900 uppercase">
              VELANDIAX
            </Link>

            <div className="hidden lg:flex flex-1 max-w-2xl relative group">
              <input
                type="text"
                placeholder="Buscar referencias, colores, pacas..."
                className="w-full bg-slate-50 text-slate-900 px-4 py-2.5 rounded-full pl-11 focus:outline-none focus:ring-2 focus:ring-slate-300 border border-slate-200 text-sm font-medium transition-all group-hover:bg-white"
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-slate-600 transition-colors" size={18} />
              <button className="absolute right-1 top-1/2 -translate-y-1/2 bg-black text-white px-5 py-1.5 rounded-full text-xs font-bold uppercase hover:bg-slate-800 transition-colors cursor-pointer">
                Buscar
              </button>
            </div>

            <div className="flex items-center gap-5 sm:gap-7 text-slate-900">
              <button onClick={() => navigate('/favoritos')} className="hover:text-red-500 transition-colors relative cursor-pointer">
                <Heart size={24} strokeWidth={1.5} />
                {favorites.length > 0 && (
                  <span className="absolute -top-1.5 -right-2 bg-slate-900 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                    {favorites.length}
                  </span>
                )}
              </button>

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

          <nav className="border-t border-slate-100 py-3">
            <div className="flex items-center gap-3 overflow-x-auto hide-scrollbar">
              <Link
                to="/arma-tu-paca"
                className="shrink-0 flex items-center gap-2 rounded-full bg-black text-white px-4 py-2 text-xs font-black uppercase tracking-wide hover:bg-slate-800 transition-colors"
              >
                <Package size={16} /> Arma tu paca
              </Link>

              <Link
                to="/sale"
                className="shrink-0 flex items-center gap-2 rounded-full bg-red-50 text-red-600 border border-red-100 px-4 py-2 text-xs font-black uppercase tracking-wide hover:bg-red-100 transition-colors"
              >
                <Percent size={16} /> Sale
              </Link>

              {categorias.map((cat) => (
                <Link
                  key={cat.id_categoria}
                  to={`/categoria/${cat.id_categoria}`}
                  className="shrink-0 flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-black uppercase tracking-wide text-slate-700 hover:border-black hover:text-black transition-colors"
                >
                  <span className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center text-[11px] font-black">
                    {getCategoryInitial(cat.nombre)}
                  </span>
                  {cat.nombre}
                </Link>
              ))}

              <Link
                to="/seguimiento"
                className="shrink-0 flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-xs font-black uppercase tracking-wide text-slate-700 hover:border-black hover:text-black transition-colors"
              >
                <Truck size={16} /> Seguimiento
              </Link>
            </div>
          </nav>
        </div>
      </header>

      <main className="flex-grow">
        <Outlet />
      </main>

      <footer className="bg-black text-white mt-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 grid grid-cols-1 lg:grid-cols-4 gap-10">
          <div className="lg:col-span-1">
            <h2 className="text-3xl font-black tracking-tighter uppercase">VELANDIAX</h2>
            <p className="text-sm text-slate-300 mt-4 leading-relaxed">
              Distribuidora de ropa por unidad y por paca. Referencias seleccionadas para venta presencial y web.
            </p>
            <div className="flex gap-3 mt-6">
              <a href={CONTACT.instagram} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white text-black flex items-center justify-center hover:bg-slate-200 transition-colors" aria-label="Instagram">
                <Camera size={18} />
              </a>
              <a href={CONTACT.tiktok} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white text-black flex items-center justify-center hover:bg-slate-200 transition-colors" aria-label="TikTok">
                <Music2 size={18} />
              </a>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-widest mb-4">Contacto</h3>
            <div className="space-y-3 text-sm text-slate-300">
              <a href={`mailto:${CONTACT.email}`} className="flex items-center gap-3 hover:text-white transition-colors">
                <Mail size={16} /> {CONTACT.email}
              </a>
              <a href={`tel:${CONTACT.phone.replace(/\s/g, '')}`} className="flex items-center gap-3 hover:text-white transition-colors">
                <Phone size={16} /> {CONTACT.phone}
              </a>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-widest mb-4">Enlaces</h3>
            <div className="space-y-3 text-sm text-slate-300">
              <Link to="/arma-tu-paca" className="block hover:text-white transition-colors">Arma tu paca</Link>
              <Link to="/seguimiento" className="block hover:text-white transition-colors">Seguimiento del pedido</Link>
              <Link to="/sale" className="block hover:text-white transition-colors">Ofertas</Link>
              <Link to="/favoritos" className="block hover:text-white transition-colors">Favoritos</Link>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-widest mb-4 flex items-center gap-2">
              <MapPinned size={16} /> Mapa de operacion
            </h3>
            <div className="relative h-48 rounded-2xl overflow-hidden border border-white/10 bg-[radial-gradient(circle_at_25%_35%,rgba(255,255,255,0.22),transparent_18%),radial-gradient(circle_at_70%_65%,rgba(255,255,255,0.18),transparent_16%),linear-gradient(135deg,#111827,#020617)]">
              <div className="absolute inset-0 opacity-25 bg-[linear-gradient(90deg,transparent_24%,rgba(255,255,255,.16)_25%,rgba(255,255,255,.16)_26%,transparent_27%,transparent_74%,rgba(255,255,255,.16)_75%,rgba(255,255,255,.16)_76%,transparent_77%),linear-gradient(0deg,transparent_24%,rgba(255,255,255,.16)_25%,rgba(255,255,255,.16)_26%,transparent_27%,transparent_74%,rgba(255,255,255,.16)_75%,rgba(255,255,255,.16)_76%,transparent_77%)] bg-[length:48px_48px]" />
              <div className="absolute left-[25%] top-[36%]">
                <MapPin className="text-white drop-shadow-lg" size={34} fill="white" />
                <span className="absolute left-7 top-1 whitespace-nowrap text-[10px] font-black uppercase bg-white text-black px-2 py-1 rounded-full">El Legado</span>
              </div>
              <div className="absolute left-[66%] top-[62%]">
                <MapPin className="text-white drop-shadow-lg" size={34} fill="white" />
                <span className="absolute right-7 top-1 whitespace-nowrap text-[10px] font-black uppercase bg-white text-black px-2 py-1 rounded-full">Milán</span>
              </div>
            </div>
            <div className="text-xs text-slate-400 mt-3 space-y-1">
              {ADDRESSES.map((address) => (
                <p key={address}>{address}</p>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 py-4 text-center text-[11px] text-slate-400 uppercase tracking-widest">
          Velandiax Store - Todos los derechos reservados
        </div>
      </footer>

      <a
        href={`https://wa.me/${CONTACT.whatsapp}`}
        target="_blank"
        rel="noreferrer"
        className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] text-white shadow-2xl hover:bg-[#1DA851] hover:scale-105 transition-all"
        aria-label="Contactar por WhatsApp"
      >
        <WhatsAppLogo />
      </a>

      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </div>
  );
};
