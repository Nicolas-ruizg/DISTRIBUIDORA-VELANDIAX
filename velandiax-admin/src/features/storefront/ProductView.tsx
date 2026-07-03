import { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ShoppingBag, ChevronRight, Star, ShieldCheck, Truck } from 'lucide-react';
import apiClient from '../../api/axios';
import type { ProductoDetalle } from '../../types/index';
import { useCart } from '../../context/CartContext';
import { CartModal } from './components/CartModal'; // <-- IMPORTAMOS EL MODAL AQUÍ TAMBIÉN

export const ProductView = () => {
  const { id } = useParams();
  const { addToCart } = useCart();
  
  const [producto, setProducto] = useState<ProductoDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  // Estado local para abrir el modal automático al comprar
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [agregado, setAgregado] = useState(false);

  const [imagenActiva, setImagenActiva] = useState<string>('');
  const [cantidad, setCantidad] = useState(1);
  const [atributosSeleccionados, setAtributosSeleccionados] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchProducto = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get(`/productos/${id}`);
        const data: ProductoDetalle = res.data;
        
        setProducto(data);
        
        const imgPrincipal = data.imagenes.find(img => img.es_principal) || data.imagenes[0];
        if (imgPrincipal) setImagenActiva(imgPrincipal.url);

      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchProducto();
  }, [id]);

  const opcionesDisponibles = useMemo(() => {
    if (!producto) return {};
    const opciones: Record<string, Set<string>> = {};
    
    producto.variantes.forEach(v => {
      Object.entries(v.atributos).forEach(([key, val]) => {
        if (!opciones[key]) opciones[key] = new Set();
        opciones[key].add(val);
      });
    });

    const resultado: Record<string, string[]> = {};
    for (const key in opciones) {
      resultado[key] = Array.from(opciones[key]);
    }
    return resultado;
  }, [producto]);

  const varianteSeleccionada = useMemo(() => {
    if (!producto || producto.variantes.length === 0) return null;
    
    if (Object.keys(opcionesDisponibles).length === 0) {
      return producto.variantes[0];
    }

    return producto.variantes.find(v => {
      const keysVariante = Object.keys(v.atributos);
      if (keysVariante.length !== Object.keys(atributosSeleccionados).length) return false;
      
      return keysVariante.every((key: string) => {
        const valorVariante = (v.atributos as Record<string, string>)[key];
        const valorSeleccionado = atributosSeleccionados[key];
        return valorVariante === valorSeleccionado;
      });
    }) || null;

  }, [producto, atributosSeleccionados, opcionesDisponibles]);

  const handleSelectAttribute = (key: string, valor: string) => {
    setAtributosSeleccionados(prev => ({ ...prev, [key]: valor }));
  };

  useEffect(() => {
    const imagenVariante = varianteSeleccionada?.imagen_principal || varianteSeleccionada?.imagenes?.find(img => img.es_principal)?.url || varianteSeleccionada?.imagenes?.[0]?.url;
    if (imagenVariante) {
      setImagenActiva(imagenVariante);
    }
  }, [varianteSeleccionada]);

  const formatearDinero = (monto: number) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  const handleAddToCart = () => {
    if (!varianteSeleccionada || !producto) return alert("Por favor selecciona todas las opciones.");
    
    // Agregamos al Context Global
    addToCart(producto, varianteSeleccionada, cantidad);
    
    // Cambiamos el botón a éxito
    setAgregado(true);
    setTimeout(() => setAgregado(false), 2000);
    
    // ¡DESPLEGAMOS EL CARRITO DE MANERA DINÁMICA!
    setTimeout(() => setIsCartOpen(true), 300);
  };

  if (loading) return <div className="flex h-[60vh] items-center justify-center"><div className="w-12 h-12 border-4 border-slate-200 border-t-black rounded-full animate-spin"></div></div>;
  if (error || !producto) return <div className="text-center py-20 text-slate-500">Producto no encontrado.</div>;

  const precioMostrar = varianteSeleccionada 
    ? varianteSeleccionada.precio_minorista 
    : Math.min(...producto.variantes.map(v => v.precio_minorista));

  const precioMayoristaMostrar = varianteSeleccionada 
    ? varianteSeleccionada.precio_mayorista 
    : Math.min(...producto.variantes.map(v => v.precio_mayorista));

  const faltanAtributos = Object.keys(opcionesDisponibles).length > Object.keys(atributosSeleccionados).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <nav className="flex items-center text-xs text-slate-500 mb-6 uppercase tracking-wider">
        <Link to="/" className="hover:text-black transition-colors">Inicio</Link>
        <ChevronRight size={14} className="mx-2" />
        <span className="hover:text-black transition-colors cursor-pointer">{producto.categoria}</span>
        <ChevronRight size={14} className="mx-2" />
        <span className="text-slate-800 font-bold truncate w-32 sm:w-auto">{producto.nombre}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        
        <div className="flex flex-col-reverse md:flex-row gap-4">
          <div className="flex md:flex-col gap-3 overflow-x-auto md:overflow-y-auto md:w-24 hide-scrollbar">
            {producto.imagenes.map((img) => (
              <button 
                key={img.id_imagen} 
                onClick={() => setImagenActiva(img.url)}
                className={`flex-shrink-0 w-20 h-24 md:w-24 md:h-32 rounded-lg overflow-hidden border-2 transition-all ${imagenActiva === img.url ? 'border-black opacity-100' : 'border-transparent opacity-60 hover:opacity-100'}`}
              >
                <img src={img.url} alt="miniatura" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
          <div className="flex-1 bg-slate-100 rounded-xl overflow-hidden relative aspect-[3/4] md:aspect-auto">
            {imagenActiva ? (
              <img src={imagenActiva} alt={producto.nombre} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-400">Sin Imagen</div>
            )}
            {producto.paquete_estatico && (
              <span className="absolute top-4 left-4 bg-black text-white text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-full shadow-lg">
                Paquete Mayorista
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col pt-2 md:pt-6">
          <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tight leading-none mb-2">
            {producto.nombre}
          </h1>
          <div className="flex items-center gap-4 mb-6 text-sm text-slate-500">
            <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded font-bold uppercase tracking-wider">{producto.categoria}</span>
            <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded font-bold uppercase tracking-wider">
              {producto.deposito || producto.id_deposito}
            </span>
            <div className="flex items-center gap-1 text-amber-500"><Star size={16} fill="currentColor"/> 4.9 (128 reviews)</div>
          </div>

          <div className="mb-6">
            <div className="flex items-end gap-3 mb-1">
              <span className="text-3xl font-black text-slate-900">{formatearDinero(precioMostrar)}</span>
              {!varianteSeleccionada && <span className="text-sm text-slate-500 font-medium mb-1.5">Precio desde</span>}
            </div>
            <div className="bg-slate-50 border border-slate-200 p-3 rounded-lg inline-flex flex-col sm:flex-row sm:items-center gap-2 text-sm mt-2">
              <span className="bg-slate-100 text-slate-800 font-bold px-2 py-0.5 rounded text-xs uppercase">Precio Mayorista</span>
              <span className="font-bold text-slate-800">{formatearDinero(precioMayoristaMostrar)}</span>
              <span className="text-slate-500 text-xs">/ud al llevar 6+ unidades.</span>
            </div>
          </div>

          <div className="space-y-6 mb-8 border-t border-slate-100 pt-6">
            {Object.keys(opcionesDisponibles).length > 0 ? (
              Object.entries(opcionesDisponibles).map(([atributo, valores]) => (
                <div key={atributo}>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                    {atributo}: <span className="text-slate-500 font-medium">
                      {(atributosSeleccionados as Record<string, string>)[atributo] || 'Selecciona uno'}
                    </span>
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {valores.map(valor => {
                      const isSelected = atributosSeleccionados[atributo] === valor;
                      return (
                        <button 
                          key={valor}
                          onClick={() => handleSelectAttribute(atributo, valor)}
                          className={`px-4 py-2 border rounded-md text-sm font-bold transition-all ${isSelected ? 'border-black bg-black text-white shadow-md transform scale-105' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-400'}`}
                        >
                          {valor}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 italic">Producto de variante única.</p>
            )}
          </div>

          <div className="flex items-center gap-4 mb-8">
            <div className="flex items-center border-2 border-slate-200 rounded-lg w-32 h-12">
              <button onClick={() => setCantidad(Math.max(1, cantidad - 1))} className="w-10 h-full flex items-center justify-center text-slate-500 hover:text-black font-bold text-xl transition-colors">-</button>
              <input type="number" value={cantidad} readOnly className="flex-1 h-full w-full text-center font-bold text-lg text-slate-900 bg-transparent outline-none" />
              <button onClick={() => setCantidad(cantidad + 1)} className="w-10 h-full flex items-center justify-center text-slate-500 hover:text-black font-bold text-xl transition-colors">+</button>
            </div>

            <button 
              onClick={handleAddToCart}
              disabled={faltanAtributos}
              className={`flex-1 h-12 rounded-lg flex items-center justify-center gap-2 font-bold uppercase tracking-wide transition-all shadow-xl cursor-pointer ${
                faltanAtributos 
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
                  : agregado 
                    ? 'bg-emerald-500 text-white scale-[1.02]' 
                    : 'bg-black text-white hover:bg-slate-800 hover:scale-[1.02]'
              }`}
            >
              <ShoppingBag size={20} />
              {faltanAtributos ? 'Selecciona Opciones' : agregado ? '¡Añadido al Carrito!' : 'Añadir al Carrito'}
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 py-6 border-y border-slate-100 mb-8">
            <div className="flex items-center gap-3 text-slate-600">
              <Truck className="text-slate-400" size={24} />
              <span className="text-xs font-bold leading-tight">Envíos a todo el país<br/><span className="text-slate-400 font-normal">Rápidos y seguros</span></span>
            </div>
            <div className="flex items-center gap-3 text-slate-600">
              <ShieldCheck className="text-slate-400" size={24} />
              <span className="text-xs font-bold leading-tight">Compra Segura<br/><span className="text-slate-400 font-normal">Atención personalizada</span></span>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-3">Detalles del Producto</h3>
            <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-line">
              {producto.descripcion || "Un producto excelente diseñado para brindarte la mejor calidad y estilo. Combínalo a tu gusto y aprovecha nuestros precios al por mayor."}
            </p>
          </div>

        </div>
      </div>

      {/* MODAL INYECTADO PARA LA APERTURA AUTOMÁTICA */}
      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </div>
  );
};
