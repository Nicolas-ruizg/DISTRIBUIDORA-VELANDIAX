import { useNavigate, Link } from 'react-router-dom';
import { Heart, ShoppingCart, Trash2, ArrowRight } from 'lucide-react';
import { useFavorites } from '../../context/FavoritesContext';

export const FavoritesView = () => {
  const navigate = useNavigate();
  const { favorites, toggleFavorite } = useFavorites();

  const formatearDinero = (monto: number) => 
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  return (
    <div className="min-h-screen bg-white">
      {/* HEADER DE LA SECCIÓN */}
      <div className="bg-slate-50 border-b border-slate-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Heart size={40} className="mx-auto text-red-500 fill-red-500 mb-4" />
          <h1 className="text-3xl md:text-5xl font-black text-slate-900 uppercase tracking-tighter mb-2">
            Mis Favoritos
          </h1>
          <p className="text-slate-500 font-medium">
            {favorites.length === 1 
              ? 'Tienes 1 producto guardado para más tarde.' 
              : `Tienes ${favorites.length} productos guardados para más tarde.`}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {favorites.length === 0 ? (
          /* ESTADO VACÍO */
          <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
            <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-6">
              <Heart size={40} className="text-slate-300" />
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Tu lista de deseos está vacía</h2>
            <p className="text-slate-500 mb-8 max-w-md mx-auto">
              Aún no has guardado ningún producto. Explora nuestro catálogo y presiona el corazón en los artículos que más te gusten.
            </p>
            <Link 
              to="/" 
              className="bg-black text-white px-8 py-4 rounded-full font-bold uppercase tracking-wide flex items-center gap-2 hover:bg-slate-800 transition-transform transform hover:-translate-y-1 shadow-lg"
            >
              Explorar la tienda <ArrowRight size={18} />
            </Link>
          </div>
        ) : (
          /* GRILLA DE PRODUCTOS FAVORITOS */
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 md:gap-6">
            {favorites.map((prod) => (
              <div key={prod.id_producto} className="group flex flex-col relative border border-transparent hover:border-slate-100 rounded-xl p-2 transition-colors">
                
                {/* Botón de Eliminar de Favoritos */}
                <button 
                  onClick={(e) => { e.stopPropagation(); toggleFavorite(prod); }}
                  className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur p-2 rounded-full shadow-sm hover:bg-red-50 hover:text-red-500 text-slate-400 transition-all cursor-pointer"
                  title="Quitar de favoritos"
                >
                  <Trash2 size={16} />
                </button>

                {/* Imagen del Producto */}
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
                    <div className="w-full h-full flex items-center justify-center text-slate-300 text-sm">Sin foto</div>
                  )}
                  {prod.paquete_estatico && (
                    <div className="absolute top-2 left-2 bg-black text-white text-[10px] font-bold uppercase px-2 py-1 rounded shadow-md">
                      Por paca
                    </div>
                  )}
                  
                  {/* Botón rápido "Ver Opciones" */}
                  <div className="absolute bottom-2 left-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button className="w-full bg-white/95 backdrop-blur text-black text-sm font-bold py-2 rounded shadow-lg hover:bg-black hover:text-white transition-colors flex items-center justify-center gap-2">
                      <ShoppingCart size={16} /> Ver Opciones
                    </button>
                  </div>
                </div>

                {/* Información del Producto */}
                <div className="flex flex-col flex-grow cursor-pointer px-1" onClick={() => navigate(`/producto/${prod.id_producto}`)}>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">
                    {prod.categoria}
                  </span>
                  <h3 className="text-sm font-medium text-slate-800 line-clamp-2 leading-tight mb-2 group-hover:underline">
                    {prod.nombre}
                  </h3>
                  <div className="mt-auto flex items-end justify-between">
                    <div>
                      {prod.precio_desde ? (
                        <p className="text-lg font-black text-slate-900">{formatearDinero(prod.precio_desde)}</p>
                      ) : (
                        <p className="text-sm text-slate-400 italic">No disponible</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
