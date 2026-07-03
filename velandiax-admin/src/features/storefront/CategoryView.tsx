import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ShoppingCart, Heart, ChevronRight, SlidersHorizontal } from 'lucide-react';
import apiClient from '../../api/axios';
import { useFavorites } from '../../context/FavoritesContext';
import type { ProductoResumen, Categoria } from '../../types/index';

export const CategoryView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toggleFavorite, isFavorite } = useFavorites();
  
  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [categoriaNombre, setCategoriaNombre] = useState<string>('Cargando...');
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('recientes'); // Estado para el filtro

  useEffect(() => {
    const fetchCategoryData = async () => {
      setLoading(true);
      try {
        // 1. Traemos los productos de esta categoría específica
        const resProductos = await apiClient.get(`/productos?id_categoria=${id}`);
        setProductos(resProductos.data);

        // 2. Intentamos deducir el nombre de la categoría del primer producto
        if (resProductos.data.length > 0) {
          setCategoriaNombre(resProductos.data[0].categoria);
        } else {
          // Si no hay productos, consultamos el nombre de la categoría a la API
          const resCats = await apiClient.get('/admin/categorias');
          const cat = resCats.data.find((c: Categoria) => c.id_categoria === Number(id));
          setCategoriaNombre(cat ? cat.nombre : 'Colección');
        }
      } catch (err) {
        console.error(err);
        setCategoriaNombre('Categoría no encontrada');
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryData();
  }, [id]);

  // --- MOTOR DE ORDENAMIENTO EN TIEMPO REAL ---
  const productosOrdenados = useMemo(() => {
    const copia = [...productos];
    if (sortBy === 'precio_asc') {
      return copia.sort((a, b) => (a.precio_desde || 0) - (b.precio_desde || 0));
    }
    if (sortBy === 'precio_desc') {
      return copia.sort((a, b) => (b.precio_desde || 0) - (a.precio_desde || 0));
    }
    if (sortBy === 'az') {
      return copia.sort((a, b) => a.nombre.localeCompare(b.nombre));
    }
    return copia; // 'recientes' (orden por defecto del backend)
  }, [productos, sortBy]);

  const formatearDinero = (monto: number) => 
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  return (
    <div className="min-h-screen bg-white">
      
      {/* HEADER DE CATEGORÍA */}
      <div className="bg-slate-50 border-b border-slate-100 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          {/* Breadcrumbs */}
          <nav className="flex justify-center items-center text-xs text-slate-400 uppercase tracking-wider mb-4">
            <Link to="/" className="hover:text-black transition-colors">Inicio</Link>
            <ChevronRight size={14} className="mx-2" />
            <span>Categorías</span>
            <ChevronRight size={14} className="mx-2" />
            <span className="text-slate-800 font-bold">{categoriaNombre}</span>
          </nav>
          
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 uppercase tracking-tighter mb-4 capitalize">
            {categoriaNombre}
          </h1>
          <p className="text-slate-500 font-medium">
            Descubre nuestra selección exclusiva. {productos.length} productos disponibles.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* BARRA DE FILTROS Y ORDENAMIENTO */}
        <div className="flex flex-col sm:flex-row justify-between items-center pb-6 mb-8 border-b border-slate-100 gap-4">
          <div className="flex items-center gap-2 text-slate-500 font-medium text-sm">
            <SlidersHorizontal size={18} />
            <span>Filtros ocultos (Próximamente)</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">Ordenar por:</span>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 text-sm font-bold rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-black transition-shadow cursor-pointer flex-1 sm:flex-none"
            >
              <option value="recientes">Más recientes</option>
              <option value="precio_asc">Precio: Menor a Mayor</option>
              <option value="precio_desc">Precio: Mayor a Menor</option>
              <option value="az">Alfabéticamente (A-Z)</option>
            </select>
          </div>
        </div>

        {/* GRILLA DE PRODUCTOS */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-4 border-slate-200 border-t-black rounded-full animate-spin"></div>
          </div>
        ) : productosOrdenados.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-slate-400 text-lg font-medium mb-4">No hay productos en esta categoría aún.</p>
            <Link to="/" className="text-black font-bold hover:underline">Volver a la tienda</Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 md:gap-6">
            {productosOrdenados.map((prod) => {
              const esFavorito = isFavorite(prod.id_producto);
              return (
                <div key={prod.id_producto} className="group flex flex-col relative">
                  
                  {/* Botón Favorito */}
                  <button 
                    onClick={(e) => { e.stopPropagation(); toggleFavorite(prod); }}
                    className="absolute top-2 right-2 z-10 bg-white/80 backdrop-blur p-2 rounded-full shadow-sm hover:bg-white hover:scale-110 transition-all cursor-pointer"
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
                    {prod.paquete_estatico && <div className="absolute top-2 left-2 bg-black text-white text-[10px] font-bold uppercase px-2 py-1 rounded shadow-md">Paquete</div>}
                    
                    <div className="absolute bottom-2 left-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <button className="w-full bg-white/90 backdrop-blur text-black text-sm font-bold py-2 rounded shadow-lg hover:bg-black hover:text-white transition-colors flex items-center justify-center gap-2">
                        <ShoppingCart size={16} /> Ver Opciones
                      </button>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex flex-col flex-grow cursor-pointer" onClick={() => navigate(`/producto/${prod.id_producto}`)}>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">{prod.categoria}</span>
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">
                      Disponible en {prod.deposito || prod.id_deposito}
                    </span>
                    <h3 className="text-sm font-medium text-slate-800 line-clamp-2 leading-tight mb-2 group-hover:underline">{prod.nombre}</h3>
                    <div className="mt-auto flex items-end justify-between">
                      <div>
                        {prod.precio_desde ? (
                          <p className="text-lg font-black text-slate-900">{formatearDinero(prod.precio_desde)}</p>
                        ) : (
                          <p className="text-sm text-slate-400 italic">No disponible</p>
                        )}
                      </div>
                      {prod.variantes > 1 && <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">+{prod.variantes} Col.</span>}
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
