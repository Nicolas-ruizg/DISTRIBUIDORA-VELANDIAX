import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShoppingCart, Heart, ChevronRight, SlidersHorizontal, Flame, Percent } from 'lucide-react';
import apiClient from '../../api/axios';
import { useFavorites } from '../../context/FavoritesContext';
import type { ProductoResumen } from '../../types/index';



export const SaleView = () => {
  const navigate = useNavigate();
  const { toggleFavorite, isFavorite } = useFavorites();
  
  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('descuento');

  useEffect(() => {
    const fetchSaleProducts = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get('/productos');
        
        // Filtramos usando el campo real de tu base de datos
        const productosEnOferta = res.data.filter((p: ProductoResumen) => p.en_oferta === true);
        setProductos(productosEnOferta);

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSaleProducts();
  }, []);

  const productosOrdenados = useMemo(() => {
    const copia = [...productos];
    if (sortBy === 'precio_asc') return copia.sort((a, b) => (a.precio_desde || 0) - (b.precio_desde || 0));
    if (sortBy === 'precio_desc') return copia.sort((a, b) => (b.precio_desde || 0) - (a.precio_desde || 0));
    return copia; 
  }, [productos, sortBy]);

  const formatearDinero = (monto: number) => 
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  return (
    <div className="min-h-screen bg-white">
      
      {/* HEADER DE SALE (Diseño Rojo / Urgencia) */}
      <div className="bg-red-50 border-b border-red-100 py-12 px-4 relative overflow-hidden">
        {/* Elemento de fondo decorativo */}
        <Percent size={200} className="absolute -top-10 -right-10 text-red-100/50 rotate-12" />
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <nav className="flex justify-center items-center text-xs text-red-400 uppercase tracking-wider mb-4">
            <Link to="/" className="hover:text-red-600 transition-colors">Inicio</Link>
            <ChevronRight size={14} className="mx-2" />
            <span className="text-red-600 font-bold">Ofertas Especiales</span>
          </nav>
          
          <h1 className="text-4xl md:text-5xl font-black text-red-600 uppercase tracking-tighter mb-4 flex items-center justify-center gap-3">
            <Flame size={40} className="fill-red-500" /> SALE HASTA -40%
          </h1>
          <p className="text-red-500/80 font-medium max-w-xl mx-auto">
            Aprovecha nuestros descuentos de temporada. Unidades limitadas. ¡Los productos en esta sección vuelan!
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* BARRA DE FILTROS Y ORDENAMIENTO */}
        <div className="flex flex-col sm:flex-row justify-between items-center pb-6 mb-8 border-b border-slate-100 gap-4">
          <div className="flex items-center gap-2 text-slate-500 font-medium text-sm">
            <SlidersHorizontal size={18} />
            <span>Filtros de oferta</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">Ordenar por:</span>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 text-sm font-bold rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-red-500 transition-shadow cursor-pointer"
            >
              <option value="descuento">Mayor Descuento</option>
              <option value="precio_asc">Precio: Menor a Mayor</option>
              <option value="precio_desc">Precio: Mayor a Menor</option>
            </select>
          </div>
        </div>

        {/* GRILLA DE PRODUCTOS */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-4 border-red-100 border-t-red-600 rounded-full animate-spin"></div>
          </div>
        ) : productosOrdenados.length === 0 ? (
          <div className="text-center py-20">
            <Flame size={48} className="mx-auto text-slate-200 mb-4" />
            <p className="text-slate-400 text-lg font-medium mb-4">No hay productos en oferta en este momento.</p>
            <Link to="/" className="text-red-600 font-bold hover:underline">Volver a la nueva colección</Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 md:gap-6">
            {productosOrdenados.map((prod) => {
              const esFavorito = isFavorite(prod.id_producto);
              
              // Cálculo del porcentaje de descuento (si aplica)
              const descuento = prod.precio_anterior && prod.precio_desde 
                ? Math.round(((prod.precio_anterior - prod.precio_desde) / prod.precio_anterior) * 100)
                : 0;

              return (
                <div key={prod.id_producto} className="group flex flex-col relative border border-transparent hover:border-red-100 rounded-xl p-2 transition-colors">
                  
                  {/* Botón Favorito */}
                  <button 
                    onClick={(e) => { e.stopPropagation(); toggleFavorite(prod); }}
                    className="absolute top-4 right-4 z-10 bg-white/80 backdrop-blur p-2 rounded-full shadow-sm hover:bg-white hover:scale-110 transition-all cursor-pointer"
                  >
                    <Heart size={16} className={`transition-colors ${esFavorito ? 'fill-red-500 text-red-500' : 'text-slate-400 hover:text-red-500'}`} />
                  </button>

                  {/* Imagen */}
                  <div onClick={() => navigate(`/producto/${prod.id_producto}`)} className="relative aspect-[3/4] bg-slate-100 rounded-lg overflow-hidden mb-3 cursor-pointer">
                    {prod.imagen_principal ? (
                      <img src={prod.imagen_principal} alt={prod.nombre} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-300">Sin foto</div>
                    )}
                    
                    {/* ETIQUETA ROJA DE DESCUENTO */}
                    {descuento > 0 && (
                      <div className="absolute top-2 left-2 bg-red-600 text-white text-[11px] font-black uppercase px-2 py-1 rounded shadow-md">
                        -{descuento}% OFF
                      </div>
                    )}
                    
                    <div className="absolute bottom-2 left-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <button className="w-full bg-red-600/90 backdrop-blur text-white text-sm font-bold py-2 rounded shadow-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2">
                        <ShoppingCart size={16} /> Lo Quiero
                      </button>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex flex-col flex-grow cursor-pointer px-1" onClick={() => navigate(`/producto/${prod.id_producto}`)}>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">{prod.categoria}</span>
                    <h3 className="text-sm font-medium text-slate-800 line-clamp-2 leading-tight mb-2 group-hover:underline">{prod.nombre}</h3>
                    <div className="mt-auto flex items-end gap-2">
                      {/* PRECIO ACTUAL (ROJO) */}
                      {prod.precio_desde ? (
                        <p className="text-lg font-black text-red-600">{formatearDinero(prod.precio_desde)}</p>
                      ) : null}
                      
                      {/* PRECIO ANTERIOR (TACHADO) */}
                      {prod.precio_anterior && (
                        <p className="text-xs font-bold text-slate-400 line-through mb-1">
                          {formatearDinero(prod.precio_anterior)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};