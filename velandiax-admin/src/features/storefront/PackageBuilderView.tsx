import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, X, Plus, CheckCircle2, Info, ArrowLeft, Layers } from 'lucide-react';
import apiClient from '../../api/axios';
import { useCart } from '../../context/CartContext';
import type { Categoria, ProductoResumen, ProductoDetalle, Variante } from '../../types/index';

export const PackageBuilderView = () => {
  const navigate = useNavigate();
  const { addToCart } = useCart();

  const CAPACIDAD_PACA = 6;
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [productos, setProductos] = useState<ProductoResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategoria, setSelectedCategoria] = useState<Categoria | null>(null);

  const [paca, setPaca] = useState<{ producto: ProductoDetalle, variante: Variante, cantidad: number }[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [productoDetalle, setProductoDetalle] = useState<ProductoDetalle | null>(null);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [atributosSeleccionados, setAtributosSeleccionados] = useState<Record<string, string>>({});
  const [cantidadQuick, setCantidadQuick] = useState(1);

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const [catRes, prodRes] = await Promise.all([
          apiClient.get('/categorias'),
          apiClient.get('/productos'),
        ]);
        setCategorias(catRes.data);
        setProductos(
          prodRes.data.filter((p: ProductoResumen) => p.estado === 'ACTIVO' && !p.paquete_estatico)
        );
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitial();
  }, []);

  useEffect(() => {
    if (!selectedProductId) return;
    const fetchDetalle = async () => {
      setLoadingDetalle(true);
      try {
        const res = await apiClient.get(`/productos/${selectedProductId}`);
        setProductoDetalle(res.data);
        setAtributosSeleccionados({});
        setCantidadQuick(1);
      } catch {
        alert('Error al cargar el producto');
        setSelectedProductId(null);
      } finally {
        setLoadingDetalle(false);
      }
    };
    fetchDetalle();
  }, [selectedProductId]);

  const productosCategoria = useMemo(() => {
    if (!selectedCategoria) return [];
    return productos.filter(producto => producto.id_categoria === selectedCategoria.id_categoria);
  }, [productos, selectedCategoria]);

  const categoriasDisponibles = useMemo(() => {
    const categoriasConProductos = new Set(productos.map(producto => producto.id_categoria));
    return categorias.filter(categoria => categoriasConProductos.has(categoria.id_categoria));
  }, [categorias, productos]);

  const opcionesDisponibles = useMemo(() => {
    if (!productoDetalle) return {};
    const opciones: Record<string, Set<string>> = {};
    const variantesValidas = productoDetalle.variantes.filter(v => v.estado === 'ACTIVO' && v.aplica_paquete);

    variantesValidas.forEach(v => {
      Object.entries(v.atributos as Record<string, string>).forEach(([key, val]) => {
        if (!opciones[key]) opciones[key] = new Set();
        opciones[key].add(val);
      });
    });

    const resultado: Record<string, string[]> = {};
    for (const key in opciones) resultado[key] = Array.from(opciones[key]);
    return resultado;
  }, [productoDetalle]);

  const varianteSeleccionada = useMemo(() => {
    if (!productoDetalle) return null;
    const variantesValidas = productoDetalle.variantes.filter(v => v.estado === 'ACTIVO' && v.aplica_paquete);

    if (Object.keys(opcionesDisponibles).length === 0 && variantesValidas.length > 0) {
      return variantesValidas[0];
    }

    return variantesValidas.find(v => {
      const atributosVariante = v.atributos as Record<string, string>;
      const keysVariante = Object.keys(atributosVariante);
      if (keysVariante.length !== Object.keys(atributosSeleccionados).length) return false;
      return keysVariante.every((key: string) => atributosVariante[key] === atributosSeleccionados[key]);
    }) || null;
  }, [productoDetalle, atributosSeleccionados, opcionesDisponibles]);

  const prendasActuales = paca.reduce((acc, item) => acc + item.cantidad, 0);
  const espacioDisponible = CAPACIDAD_PACA - prendasActuales;
  const precioTotalPaca = paca.reduce((acc, item) => acc + (item.variante.precio_mayorista * item.cantidad), 0);

  const handleAgregarAPaca = () => {
    if (!varianteSeleccionada || !productoDetalle) return alert('Selecciona todas las opciones.');
    if (cantidadQuick > espacioDisponible) return alert(`Solo te queda espacio para ${espacioDisponible} prenda(s) en esta paca.`);

    setPaca(prev => {
      const existe = prev.findIndex(item => item.variante.id_variante === varianteSeleccionada.id_variante);
      if (existe >= 0) {
        const nueva = [...prev];
        nueva[existe].cantidad += cantidadQuick;
        return nueva;
      }
      return [...prev, { producto: productoDetalle, variante: varianteSeleccionada, cantidad: cantidadQuick }];
    });

    setSelectedProductId(null);
  };

  const handleQuitarDePaca = (id_variante: number) => {
    setPaca(prev => prev.filter(item => item.variante.id_variante !== id_variante));
  };

  const handleEnviarAlCarrito = () => {
    if (prendasActuales < CAPACIDAD_PACA) return;
    paca.forEach(item => addToCart(item.producto, item.variante, item.cantidad));
    setPaca([]);
    navigate('/');
  };

  const formatearDinero = (monto: number) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(monto);

  return (
    <div className="min-h-screen bg-slate-50 pb-40">
      <div className="bg-slate-900 text-white pt-10 pb-16 px-4 text-center">
        <h1 className="text-3xl md:text-5xl font-black uppercase tracking-tight flex items-center justify-center gap-3 mb-4">
          <Package size={40} /> Arma tu Paca
        </h1>
        <p className="text-slate-100 max-w-2xl mx-auto font-medium">
          Primero elige una categoria y luego selecciona {CAPACIDAD_PACA} prendas para desbloquear precio mayorista.
        </p>
      </div>

      <div className="max-w-7xl mx-auto px-4 -mt-8 relative z-10">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-12 h-12 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
          </div>
        ) : !selectedCategoria ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {categoriasDisponibles.map(categoria => {
              const totalProductos = productos.filter(producto => producto.id_categoria === categoria.id_categoria).length;
              return (
                <button
                  key={categoria.id_categoria}
                  type="button"
                  onClick={() => setSelectedCategoria(categoria)}
                  className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 text-left hover:-translate-y-1 hover:shadow-xl hover:border-black transition-all cursor-pointer group"
                >
                  <div className="w-12 h-12 rounded-full bg-slate-900 text-white flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                    <Layers size={22} />
                  </div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
                    {totalProductos} productos disponibles
                  </p>
                  <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tight">{categoria.nombre}</h2>
                  {categoria.descripcion && (
                    <p className="text-sm text-slate-500 mt-2 line-clamp-2">{categoria.descripcion}</p>
                  )}
                </button>
              );
            })}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <button
                  type="button"
                  onClick={() => setSelectedCategoria(null)}
                  className="text-xs font-black uppercase tracking-widest text-slate-500 hover:text-black flex items-center gap-1 mb-2 cursor-pointer"
                >
                  <ArrowLeft size={14} /> Volver a categorias
                </button>
                <h2 className="text-2xl font-black text-slate-900 uppercase">{selectedCategoria.nombre}</h2>
                <p className="text-sm text-slate-500">Selecciona productos de esta categoria para armar tu paca.</p>
              </div>
              <span className="text-sm font-bold text-slate-500">{productosCategoria.length} productos</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
              {productosCategoria.map(prod => (
                <div key={prod.id_producto} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden group">
                  <div className="relative aspect-[3/4] bg-slate-100 overflow-hidden cursor-pointer" onClick={() => setSelectedProductId(prod.id_producto)}>
                    {prod.imagen_principal ? (
                      <img src={prod.imagen_principal} alt={prod.nombre} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-400">Sin foto</div>
                    )}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <span className="bg-white text-black font-bold uppercase text-xs px-4 py-2 rounded-full flex items-center gap-2">
                        <Plus size={14} /> Seleccionar
                      </span>
                    </div>
                  </div>
                  <div className="p-4">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{prod.categoria}</span>
                    <h3 className="text-sm font-bold text-slate-800 line-clamp-1">{prod.nombre}</h3>
                    {prod.precio_desde && <p className="text-sm font-black text-slate-900 mt-1">{formatearDinero(prod.precio_desde)}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedProductId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSelectedProductId(null)} />
          <div className="bg-white w-full max-w-3xl rounded-2xl shadow-2xl relative z-10 overflow-hidden flex flex-col md:flex-row animate-slideLeft">
            <button onClick={() => setSelectedProductId(null)} className="absolute top-4 right-4 bg-white p-1 rounded-full text-slate-400 hover:text-black shadow-md z-20 cursor-pointer">
              <X size={20} />
            </button>

            {loadingDetalle || !productoDetalle ? (
              <div className="w-full h-64 flex items-center justify-center"><div className="w-8 h-8 border-4 border-slate-200 border-t-black rounded-full animate-spin"></div></div>
            ) : (
              <>
                <div className="w-full md:w-1/2 bg-slate-100 h-64 md:h-auto">
                  <img
                    src={
                      varianteSeleccionada?.imagen_principal ||
                      varianteSeleccionada?.imagenes?.find(i => i.es_principal)?.url ||
                      varianteSeleccionada?.imagenes?.[0]?.url ||
                      productoDetalle.imagenes.find(i => i.es_principal)?.url ||
                      productoDetalle.imagenes[0]?.url
                    }
                    className="w-full h-full object-cover"
                    alt={productoDetalle.nombre}
                  />
                </div>

                <div className="w-full md:w-1/2 p-6 flex flex-col">
                  <h2 className="text-xl font-black text-slate-900 uppercase tracking-tight line-clamp-2 mb-4">{productoDetalle.nombre}</h2>

                  {Object.keys(opcionesDisponibles).length === 0 && productoDetalle.variantes.filter(v => v.aplica_paquete).length === 0 ? (
                    <div className="bg-amber-50 text-amber-700 p-4 rounded-lg flex items-start gap-3 mt-4">
                      <Info size={20} className="shrink-0" />
                      <p className="text-sm font-medium">Este producto no tiene variantes habilitadas para paca.</p>
                    </div>
                  ) : (
                    <>
                      <div className="flex-1 space-y-5 overflow-y-auto hide-scrollbar">
                        {Object.entries(opcionesDisponibles).map(([atributo, valores]) => (
                          <div key={atributo}>
                            <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">{atributo}</h4>
                            <div className="flex flex-wrap gap-2">
                              {valores.map(valor => (
                                <button
                                  key={valor}
                                  type="button"
                                  onClick={() => setAtributosSeleccionados(prev => ({ ...prev, [atributo]: valor }))}
                                  className={`px-3 py-1.5 border rounded text-sm font-bold transition-all cursor-pointer ${atributosSeleccionados[atributo] === valor ? 'border-black bg-black text-white' : 'border-slate-200 text-slate-700 hover:border-slate-400'}`}
                                >
                                  {valor}
                                </button>
                              ))}
                            </div>
                          </div>
                        ))}

                        <div className="pt-4">
                          <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Cantidad</h4>
                          <div className="flex items-center border border-slate-200 rounded-lg w-28 h-10">
                            <button type="button" onClick={() => setCantidadQuick(Math.max(1, cantidadQuick - 1))} className="w-10 flex justify-center text-slate-500 font-bold cursor-pointer">-</button>
                            <input type="number" value={cantidadQuick} readOnly className="flex-1 text-center font-bold text-slate-900 bg-transparent outline-none" />
                            <button type="button" onClick={() => setCantidadQuick(Math.min(espacioDisponible, cantidadQuick + 1))} className="w-10 flex justify-center text-slate-500 font-bold cursor-pointer">+</button>
                          </div>
                        </div>
                      </div>

                      <div className="pt-6 mt-6 border-t border-slate-100">
                        <button
                          type="button"
                          onClick={handleAgregarAPaca}
                          disabled={!varianteSeleccionada || cantidadQuick > espacioDisponible}
                          className="w-full bg-black text-white py-3 rounded-xl font-bold uppercase tracking-wide hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md cursor-pointer"
                        >
                          {!varianteSeleccionada ? 'Selecciona opciones' : cantidadQuick > espacioDisponible ? 'Sin espacio en la paca' : 'Anadir a la paca'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 shadow-[0_-10px_40px_rgba(0,0,0,0.1)] z-40 transition-transform duration-500 ${paca.length > 0 ? 'translate-y-0' : 'translate-y-full'}`}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row items-center gap-6">
          <div className="w-full md:w-1/3">
            <div className="flex justify-between items-end mb-2">
              <span className="font-black text-slate-900 uppercase">Tu Paca</span>
              <span className="text-sm font-bold text-black">{prendasActuales} / {CAPACIDAD_PACA}</span>
            </div>
            <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
              <div className="bg-black h-full transition-all duration-300" style={{ width: `${(prendasActuales / CAPACIDAD_PACA) * 100}%` }} />
            </div>
          </div>

          <div className="flex-1 flex gap-2 overflow-x-auto hide-scrollbar w-full md:w-auto pb-2 md:pb-0">
            {paca.map(item => {
              const foto = item.variante.imagen_principal || item.variante.imagenes?.find(i => i.es_principal)?.url || item.variante.imagenes?.[0]?.url || item.producto.imagenes.find(i => i.es_principal)?.url || item.producto.imagenes[0]?.url;
              return (
                <div key={item.variante.id_variante} className="relative w-14 h-16 bg-slate-100 rounded-md border border-slate-200 shrink-0 group">
                  {foto && <img src={foto} className="w-full h-full object-cover rounded-md opacity-80" alt="item" />}
                  <span className="absolute -top-2 -right-2 bg-black text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full shadow-md z-10">{item.cantidad}</span>
                  <button type="button" onClick={() => handleQuitarDePaca(item.variante.id_variante)} className="absolute inset-0 bg-red-500/80 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-md cursor-pointer">
                    <X size={16} />
                  </button>
                </div>
              );
            })}

            {Array.from({ length: Math.max(0, CAPACIDAD_PACA - prendasActuales) }).map((_, i) => (
              <div key={`empty-${i}`} className="w-14 h-16 rounded-md border-2 border-dashed border-slate-200 shrink-0 flex items-center justify-center bg-slate-50/50 text-slate-300">
                <Package size={16} />
              </div>
            ))}
          </div>

          <div className="w-full md:w-auto flex items-center justify-between md:justify-end gap-6 border-t md:border-t-0 border-slate-100 pt-4 md:pt-0">
            <div className="text-right">
              <p className="text-xs font-bold text-slate-400 uppercase">Total Paca</p>
              <p className="text-xl font-black text-slate-900">{formatearDinero(precioTotalPaca)}</p>
            </div>
            <button
              type="button"
              onClick={handleEnviarAlCarrito}
              disabled={prendasActuales < CAPACIDAD_PACA}
              className="bg-black text-white px-6 py-3 rounded-xl font-bold uppercase tracking-wide flex items-center gap-2 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all cursor-pointer"
            >
              {prendasActuales < CAPACIDAD_PACA ? 'Completa la paca' : <><CheckCircle2 size={18}/> Al Carrito</>}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
