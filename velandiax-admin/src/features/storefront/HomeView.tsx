import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Heart, ShoppingCart } from 'lucide-react';
import apiClient from '../../api/axios';
import { useFavorites } from '../../context/FavoritesContext';
import type { ProductoResumen } from '../../types/index';

const HERO_SLIDES = [
  {
    image: 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?q=80&w=2070&auto=format&fit=crop',
    badge: 'Nueva Coleccion',
    title: 'Renueva tu Estilo',
    desc: 'Descubre las ultimas tendencias con calidad premium.',
  },
  {
    image: 'https://images.unsplash.com/photo-1489987707023-afc824781ef1?q=80&w=2070&auto=format&fit=crop',
    badge: 'Ventas al por mayor',
    title: 'Impulsa tu Negocio',
    desc: 'Precios especiales a partir de 6 unidades mezclando como quieras.',
  },
];

export const HomeView = () => {
  const navigate = useNavigate();
  const { toggleFavorite, isFavorite } = useFavorites();

  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [slideIndex, setSlideIndex] = useState(0);
  const productSliderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchProductos = async () => {
      try {
        const res = await apiClient.get('/productos');
        setProductos(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProductos();

    const sliderInterval = setInterval(() => {
      setSlideIndex((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 5000);

    return () => clearInterval(sliderInterval);
  }, []);

  const formatearDinero = (monto: number) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(monto);

  const moverProductos = (direction: 'left' | 'right') => {
    const slider = productSliderRef.current;
    if (!slider) return;

    const distance = Math.max(slider.clientWidth * 0.8, 280);
    slider.scrollBy({
      left: direction === 'left' ? -distance : distance,
      behavior: 'smooth',
    });
  };

  return (
    <div className="w-full">
      <div className="relative w-full h-[60vh] md:h-[75vh] bg-slate-900 overflow-hidden group">
        {HERO_SLIDES.map((slide, idx) => (
          <div
            key={slide.title}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
              slideIndex === idx ? 'opacity-100 z-10' : 'opacity-0 z-0'
            }`}
          >
            <img
              src={slide.image}
              alt={slide.title}
              className="absolute inset-0 w-full h-full object-cover opacity-50"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className={`text-center text-white px-4 transition-transform duration-1000 ${
                  slideIndex === idx ? 'translate-y-0 scale-100' : 'translate-y-10 scale-95'
                }`}
              >
                <span className="bg-black text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest mb-4 inline-block shadow-lg">
                  {slide.badge}
                </span>
                <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter mb-4 drop-shadow-xl">
                  {slide.title}
                </h1>
                <p className="text-lg md:text-xl font-medium mb-8 max-w-xl mx-auto drop-shadow-md">
                  {slide.desc}
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => navigate('/categoria/1')}
                    className="bg-white text-black px-8 py-4 rounded-full font-bold uppercase tracking-wide hover:bg-slate-100 transition-transform transform hover:scale-105 shadow-xl cursor-pointer"
                  >
                    Ver Catalogo
                  </button>
                  <button
                    onClick={() => navigate('/arma-tu-paca')}
                    className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-full font-bold uppercase tracking-wide hover:bg-white hover:text-black transition-all shadow-xl cursor-pointer"
                  >
                    Arma tu Paca
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}

        <div className="absolute bottom-6 left-0 right-0 z-20 flex justify-center gap-2">
          {HERO_SLIDES.map((slide, idx) => (
            <button
              key={slide.title}
              onClick={() => setSlideIndex(idx)}
              className={`w-3 h-3 rounded-full transition-all cursor-pointer shadow-md ${
                slideIndex === idx ? 'bg-white scale-110' : 'bg-white/40 hover:bg-white/60'
              }`}
              aria-label={`Ver banner ${idx + 1}`}
            />
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12 md:py-16 mb-20">
        <div className="flex justify-between items-end mb-8 border-b border-slate-200 pb-4">
          <div>
            <h2 className="text-2xl md:text-3xl font-black uppercase tracking-tight text-slate-900">
              Recomendados
            </h2>
            <p className="text-slate-500 mt-1">Nuevos ingresos a precio especial.</p>
          </div>
          <button className="text-sm font-bold uppercase flex items-center hover:text-black transition-colors cursor-pointer">
            Ver todo <ChevronRight size={16} />
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-4 border-slate-200 border-t-black rounded-full animate-spin" />
          </div>
        ) : productos.length === 0 ? (
          <div className="text-center py-20 text-slate-500">No hay productos disponibles.</div>
        ) : (
          <div className="relative">
            <button
              type="button"
              onClick={() => moverProductos('left')}
              className="hidden md:flex absolute -left-4 top-[38%] z-20 h-11 w-11 items-center justify-center rounded-full bg-white text-black shadow-lg ring-1 ring-slate-200 hover:bg-black hover:text-white transition-colors"
              aria-label="Ver productos anteriores"
            >
              <ChevronLeft size={22} />
            </button>
            <button
              type="button"
              onClick={() => moverProductos('right')}
              className="hidden md:flex absolute -right-4 top-[38%] z-20 h-11 w-11 items-center justify-center rounded-full bg-white text-black shadow-lg ring-1 ring-slate-200 hover:bg-black hover:text-white transition-colors"
              aria-label="Ver mas productos"
            >
              <ChevronRight size={22} />
            </button>

            <div
              ref={productSliderRef}
              className="grid grid-cols-2 gap-4 md:flex md:gap-6 md:overflow-x-auto md:scroll-smooth md:pb-5 hide-scrollbar"
            >
              {productos.map((prod) => {
                const esFavorito = isFavorite(prod.id_producto);

                return (
                  <div
                    key={prod.id_producto}
                    className="group flex flex-col relative md:min-w-[220px] lg:min-w-[240px] xl:min-w-[250px]"
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavorite(prod);
                      }}
                      className="absolute top-2 right-2 z-10 bg-white/80 backdrop-blur p-2 rounded-full shadow-sm hover:bg-white hover:scale-110 transition-all cursor-pointer"
                      aria-label="Agregar a favoritos"
                    >
                      <Heart
                        size={16}
                        className={`transition-colors ${
                          esFavorito ? 'fill-red-500 text-red-500' : 'text-slate-400 hover:text-red-500'
                        }`}
                      />
                    </button>

                    <div
                      onClick={() => navigate(`/producto/${prod.id_producto}`)}
                      className="relative aspect-[3/4] bg-slate-100 rounded-lg overflow-hidden mb-3 cursor-pointer"
                    >
                      {prod.imagen_principal ? (
                        <img
                          src={prod.imagen_principal}
                          alt={prod.nombre}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-300">
                          Sin foto
                        </div>
                      )}

                      {prod.paquete_estatico && (
                        <div className="absolute top-2 left-2 bg-black text-white text-[10px] font-bold uppercase px-2 py-1 rounded shadow-md">
                          Paquete
                        </div>
                      )}

                      <div className="absolute bottom-2 left-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <button className="w-full bg-white/90 backdrop-blur text-black text-sm font-bold py-2 rounded shadow-lg hover:bg-black hover:text-white transition-colors flex items-center justify-center gap-2">
                          <ShoppingCart size={16} /> Opciones
                        </button>
                      </div>
                    </div>

                    <div
                      className="flex flex-col flex-grow cursor-pointer"
                      onClick={() => navigate(`/producto/${prod.id_producto}`)}
                    >
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">
                        {prod.categoria}
                      </span>
                      <h3 className="text-sm font-medium text-slate-800 line-clamp-2 leading-tight mb-2 group-hover:underline">
                        {prod.nombre}
                      </h3>
                      <div className="mt-auto flex items-end justify-between gap-2">
                        <div>
                          {prod.precio_desde ? (
                            <p className="text-lg font-black text-slate-900">
                              {formatearDinero(prod.precio_desde)}
                            </p>
                          ) : (
                            <p className="text-sm text-slate-400 italic">No disponible</p>
                          )}
                        </div>
                        {prod.variantes > 1 && (
                          <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                            +{prod.variantes} Col.
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
