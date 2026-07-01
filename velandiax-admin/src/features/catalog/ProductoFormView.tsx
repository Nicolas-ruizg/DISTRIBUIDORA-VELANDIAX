import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, ArrowLeft, Plus, Package, Layers, Edit, Image as ImageIcon, Star, Trash2, UploadCloud, Tag, DollarSign, ImagePlus } from 'lucide-react';
import apiClient from '../../api/axios';
import type { Categoria, ProductoDetalle, Variante, ImagenProducto } from '../../types/index';

const ATRIBUTOS_PREDEFINIDOS = ["Color", "Talla", "Material", "Marca", "Estilo", "Sabor", "Capacidad", "Dimensiones", "Peso", "Otro (Personalizado...)"];

export const ProductoFormView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(isEditing);
  const [saving, setSaving] = useState(false);
  
  const [producto, setProducto] = useState({
    codigo_producto: '',
    nombre: '', 
    descripcion: '', 
    id_categoria: 0, 
    paquete_estatico: false, 
    estado: 'ACTIVO',
    en_oferta: false,      // <-- Agregado
    precio_anterior: 0     // <-- Agregado
  });

  // --- ESTADOS VARIANTES ---
  const [variantes, setVariantes] = useState<Variante[]>([]);
  const [isVariantModalOpen, setIsVariantModalOpen] = useState(false);
  const [editingVarianteId, setEditingVarianteId] = useState<number | null>(null);
  const [varianteForm, setVarianteForm] = useState({
    precio_costo: 0, precio_minorista: 0, precio_mayorista: 0, peso: 0, aplica_paquete: false, estado: 'ACTIVO', id_imagen: null as number | null
  });
  const [atributosDinamicos, setAtributosDinamicos] = useState<{ tipo: string; personalizado: string; valor: string }[]>([]);

  // --- ESTADOS IMÁGENES ---
  const [imagenes, setImagenes] = useState<ImagenProducto[]>([]);
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  const [editingImagenId, setEditingImagenId] = useState<number | null>(null);
  
  const [imagenFile, setImagenFile] = useState<File | null>(null);
  const [imagenPreview, setImagenPreview] = useState<string | null>(null);
  const [imagenForm, setImagenForm] = useState({
    alt_text: '', es_principal: false, orden: 0, estado: 'ACTIVO'
  });

  const fetchProductoData = async () => {
    try {
      const prodRes = await apiClient.get(`/admin/productos/${id}`);
      const p: ProductoDetalle = prodRes.data;
      setProducto({ 
        codigo_producto: p.codigo_producto,
        nombre: p.nombre, 
        descripcion: p.descripcion || '', 
        id_categoria: p.id_categoria, 
        paquete_estatico: p.paquete_estatico, 
        estado: p.estado,
        en_oferta: p.en_oferta,       // Mapeado de p
        precio_anterior: p.precio_anterior || 0 // Mapeado de p
      });
      setVariantes(p.variantes);
      setImagenes(p.imagenes);
    } catch (err) {
      alert('Error al cargar la información del producto.');
    }
  };

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const catRes = await apiClient.get('/admin/categorias');
        setCategorias(catRes.data);
        if (!isEditing && catRes.data.length > 0) setProducto(prev => ({ ...prev, id_categoria: catRes.data[0].id_categoria }));
        if (isEditing) await fetchProductoData();
      } catch (err) {
        alert('Error al inicializar.');
      } finally {
        setLoading(false);
      }
    };
    fetchInitial();
  }, [id, isEditing]);

  const handleSaveProducto = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...producto,
        codigo_producto: producto.codigo_producto.trim().toUpperCase(),
      };
      if (isEditing) {
        await apiClient.put(`/admin/productos/${id}`, payload);
        alert('Producto actualizado.');
      } else {
        const res = await apiClient.post('/admin/productos', payload);
        navigate(`/admin/productos/${res.data.id_producto}`);
      }
    } catch (err: any) { alert(err.response?.data?.detail || 'Error al guardar.'); } 
    finally { setSaving(false); }
  };

  const handleToggleProductoStatus = async () => {
    const nuevoEstado = producto.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    setProducto({ ...producto, estado: nuevoEstado });
    if (isEditing) await apiClient.put(`/admin/productos/${id}`, { estado: nuevoEstado });
  };

  // --- LÓGICA DE IMÁGENES ---
  const openImageModal = (img?: ImagenProducto) => {
    if (img) {
      setEditingImagenId(img.id_imagen);
      setImagenForm({ alt_text: img.alt_text || '', es_principal: img.es_principal, orden: img.orden, estado: img.estado });
      setImagenPreview(img.url);
      setImagenFile(null);
    } else {
      setEditingImagenId(null);
      setImagenForm({ alt_text: '', es_principal: imagenes.length === 0, orden: imagenes.length, estado: 'ACTIVO' });
      setImagenPreview(null);
      setImagenFile(null);
    }
    setIsImageModalOpen(true);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImagenFile(file);
      setImagenPreview(URL.createObjectURL(file)); 
    }
  };

  const handleSaveImagen = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingImagenId) {
        await apiClient.put(`/admin/productos/imagenes/${editingImagenId}`, {
          alt_text: imagenForm.alt_text, es_principal: imagenForm.es_principal, orden: imagenForm.orden, estado: imagenForm.estado
        });
      } else {
        if (!imagenFile) { alert('Selecciona una imagen'); setSaving(false); return; }
        const formData = new FormData();
        formData.append('archivo', imagenFile);
        if (imagenForm.alt_text) formData.append('alt_text', imagenForm.alt_text);
        formData.append('es_principal', String(imagenForm.es_principal));
        formData.append('orden', String(imagenForm.orden));
        formData.append('estado', imagenForm.estado);
        await apiClient.post(`/admin/productos/${id}/imagenes/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      }
      await fetchProductoData();
      setIsImageModalOpen(false);
    } catch (err: any) { alert(err.response?.data?.detail || 'Error al guardar.'); } 
    finally { setSaving(false); }
  };

  const handleToggleImagenStatus = async (img: ImagenProducto) => {
    const nuevoEstado = img.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    try {
      await apiClient.put(`/admin/productos/imagenes/${img.id_imagen}`, { estado: nuevoEstado });
      await fetchProductoData();
    } catch (err) { alert('Error al cambiar estado.'); }
  };

  // --- LÓGICA DE VARIANTES MEJORADA ---
  const openVariantModal = (v?: Variante) => {
    if (v) {
      setEditingVarianteId(v.id_variante);
      setVarianteForm({ 
        precio_costo: v.precio_costo, precio_minorista: v.precio_minorista, precio_mayorista: v.precio_mayorista, 
        peso: v.peso || 0, aplica_paquete: v.aplica_paquete, estado: v.estado, id_imagen: v.imagenes?.find(img => img.es_principal)?.id_imagen_variante || null
      });
      const attrs = Object.entries(v.atributos).map(([key, val]) => {
        const isPredefined = ATRIBUTOS_PREDEFINIDOS.includes(key);
        return { tipo: isPredefined ? key : "Otro (Personalizado...)", personalizado: isPredefined ? '' : key, valor: val };
      });
      setAtributosDinamicos(attrs);
    } else {
      setEditingVarianteId(null);
      setVarianteForm({ precio_costo: 0, precio_minorista: 0, precio_mayorista: 0, peso: 0, aplica_paquete: false, estado: 'ACTIVO', id_imagen: null });
      setAtributosDinamicos([]);
    }
    setIsVariantModalOpen(true);
  };

  const handleSaveVariante = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const jsonAtributos: Record<string, string> = {};
    atributosDinamicos.forEach(attr => {
      const finalKey = attr.tipo === "Otro (Personalizado...)" ? attr.personalizado.trim() : attr.tipo;
      if (finalKey && attr.valor.trim() !== '') jsonAtributos[finalKey] = attr.valor.trim();
    });
    
    // Aquí enviamos el id_imagen (Asegúrate de recibirlo en el Pydantic Schema de tu backend)
    const payload = { ...varianteForm, atributos: jsonAtributos };
    
    try {
      if (editingVarianteId) await apiClient.put(`/admin/variantes/${editingVarianteId}`, payload);
      else await apiClient.post(`/admin/productos/${id}/variantes`, payload);
      await fetchProductoData();
      setIsVariantModalOpen(false);
    } catch (err: any) { alert(err.response?.data?.detail || 'Error al guardar.'); } 
    finally { setSaving(false); }
  };

  const handleToggleVarianteStatus = async (v: Variante) => {
    const nuevoEstado = v.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    setVariantes(variantes.map(vari => vari.id_variante === v.id_variante ? { ...vari, estado: nuevoEstado } : vari));
    try { await apiClient.put(`/admin/variantes/${v.id_variante}`, { estado: nuevoEstado }); } 
    catch (err) { alert('Error al cambiar estado.'); }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Cargando constructor...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-20">
      
      {/* Encabezado */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/productos')} className="p-2 text-slate-400 hover:text-slate-600 bg-white rounded-lg border border-slate-200 shadow-sm"><ArrowLeft size={20} /></button>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">{isEditing ? `Producto ${producto.codigo_producto}` : 'Nuevo Producto'}</h2>
            <p className="text-slate-500 text-sm mt-1">Información principal, galería y variantes</p>
          </div>
        </div>
        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-sm font-bold text-slate-600">Activo:</span>
          <button type="button" onClick={handleToggleProductoStatus} className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${producto.estado === 'ACTIVO' ? 'bg-emerald-500' : 'bg-slate-300'}`}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${producto.estado === 'ACTIVO' ? 'translate-x-6' : 'translate-x-1'}`} />
          </button>
        </div>
      </div>

      {/* 1. PRODUCTO BASE */}
      <form onSubmit={handleSaveProducto} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center gap-2"><Package className="text-blue-600" size={20} /><h3 className="text-lg font-bold text-slate-800">1. Detalles Básicos</h3></div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Codigo de Producto *</label>
            <input
              type="text"
              required
              value={producto.codigo_producto}
              onChange={(e) => setProducto({...producto, codigo_producto: e.target.value.toUpperCase()})}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-600 font-bold uppercase"
              placeholder="Ej: VX-CAM-001"
            />
            <p className="text-xs text-slate-400 mt-1">Este codigo lo define el negocio, no es autoincremental.</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Nombre *</label>
            <input type="text" required value={producto.nombre} onChange={(e) => setProducto({...producto, nombre: e.target.value})} className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-600" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Categoría *</label>
            <select required value={producto.id_categoria} onChange={(e) => setProducto({...producto, id_categoria: Number(e.target.value)})} className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none bg-white">
              {categorias.map(cat => <option key={cat.id_categoria} value={cat.id_categoria}>{cat.nombre}</option>)}
            </select>
          </div>
          <div className="flex items-center mt-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={producto.paquete_estatico} onChange={(e) => setProducto({...producto, paquete_estatico: e.target.checked})} className="w-5 h-5 text-blue-600 rounded" />
              <span className="text-sm font-medium text-slate-700">Es un Paquete Estático</span>
            </label>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Descripción</label>
            <textarea rows={3} value={producto.descripcion} onChange={(e) => setProducto({...producto, descripcion: e.target.value})} className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none resize-none" />
          </div>
          <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6 bg-red-50 p-4 rounded-lg border border-red-100 mt-4">
            <div className="flex items-center">
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={producto.en_oferta} onChange={(e) => setProducto({...producto, en_oferta: e.target.checked})} className="w-5 h-5 text-red-600 rounded cursor-pointer" />
                <span className="text-sm font-bold text-red-700">¿Mostrar en sección "Sale %"?</span>
              </label>
            </div>
            {producto.en_oferta && (
              <div>
                <label className="block text-xs font-bold text-red-700 mb-1.5">Precio Anterior (Tachado) $</label>
                <input type="number" min="0" value={producto.precio_anterior || ''} onChange={(e) => setProducto({...producto, precio_anterior: Number(e.target.value)})} className="w-full px-4 py-2 border border-red-200 rounded-lg outline-none focus:ring-2 focus:ring-red-500" placeholder="Ej: 85000" />
              </div>
            )}
          </div>
        </div>
        <div className="bg-slate-50 p-4 border-t border-slate-200 flex justify-end">
          <button type="submit" disabled={saving} className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700"><Save size={18} className="inline mr-2" />{saving ? 'Guardando...' : 'Guardar Producto'}</button>
        </div>
      </form>

      {/* 2. GALERÍA DE IMÁGENES */}
      {isEditing && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <ImageIcon className="text-black" size={20} />
              <h3 className="text-lg font-bold text-slate-800">2. Galería de Imágenes</h3>
            </div>
            <button onClick={() => openImageModal()} className="bg-black text-white px-4 py-2 rounded-lg hover:bg-slate-800 flex items-center gap-2 text-sm font-bold cursor-pointer">
              <UploadCloud size={18} /> Subir Imagen
            </button>
          </div>
          
          <div className="p-6">
            {imagenes.length === 0 ? (
              <div className="text-center text-slate-400 py-8 border-2 border-dashed border-slate-200 rounded-xl">
                <UploadCloud size={32} className="mx-auto mb-2 opacity-50" />
                <p>No hay imágenes en Supabase. Sube la primera.</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {imagenes.map(img => (
                  <div key={img.id_imagen} className={`relative group rounded-xl border overflow-hidden ${img.estado === 'INACTIVO' ? 'opacity-50 border-red-200' : 'border-slate-200'} ${img.es_principal ? 'ring-2 ring-slate-500' : ''}`}>
                    <img src={img.url} alt={img.alt_text || 'Imagen'} className="w-full h-32 object-cover bg-slate-100" />
                    <div className="absolute top-2 left-2 flex flex-col gap-1">
                      {img.es_principal && <span className="bg-slate-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold shadow flex items-center gap-1"><Star size={10} /> Principal</span>}
                    </div>
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      <button type="button" onClick={() => openImageModal(img)} className="bg-white text-slate-700 p-2 rounded-lg hover:text-blue-600 cursor-pointer"><Edit size={16} /></button>
                      <button type="button" onClick={() => handleToggleImagenStatus(img)} className={`p-2 rounded-lg text-white cursor-pointer ${img.estado === 'ACTIVO' ? 'bg-red-500 hover:bg-red-600' : 'bg-emerald-500 hover:bg-emerald-600'}`}>
                        {img.estado === 'ACTIVO' ? <Trash2 size={16} /> : <Plus size={16} />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 3. VARIANTES */}
      {isEditing && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Layers className="text-black" size={20} />
              <h3 className="text-lg font-bold text-slate-800">3. Variantes y Atributos (SKUs)</h3>
            </div>
            <button onClick={() => openVariantModal()} className="bg-black text-white px-4 py-2 rounded-lg hover:bg-slate-800 flex items-center gap-2 text-sm font-bold cursor-pointer"><Plus size={18} /> Añadir Variante</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead><tr className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200"><th className="p-4">SKU / Img</th><th className="p-4">Atributos</th><th className="p-4 text-right">Costo</th><th className="p-4 text-right">Minorista</th><th className="p-4 text-right">Mayorista</th><th className="p-4 text-center">Activa</th><th className="p-4 text-center">Acciones</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {variantes.length === 0 ? (<tr><td colSpan={7} className="p-8 text-center text-slate-500">Agrega tu primera variante.</td></tr>) : (
                  variantes.map(v => {
                    const variantImage = v.imagenes?.find(i => i.es_principal)?.url || v.imagenes?.[0]?.url;
                    return (
                      <tr key={v.id_variante} className={v.estado === 'INACTIVO' ? 'bg-slate-50 opacity-60' : 'hover:bg-slate-50'}>
                        <td className="p-4 text-sm font-bold">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded border border-slate-200 overflow-hidden bg-slate-100 shrink-0 flex items-center justify-center">
                              {variantImage ? <img src={variantImage} className="w-full h-full object-cover" /> : <ImageIcon size={16} className="text-slate-300"/>}
                            </div>
                            <span>#{v.id_variante}</span>
                          </div>
                        </td>
                        <td className="p-4 text-sm flex gap-1 mt-2">{Object.entries(v.atributos).map(([k, val]) => (<span key={k} className="bg-slate-200 px-2 py-1 rounded text-[11px]">{k}: {val}</span>))}</td>
                        <td className="p-4 text-sm text-right">${v.precio_costo}</td><td className="p-4 text-sm text-right text-blue-700">${v.precio_minorista}</td><td className="p-4 text-sm text-right text-emerald-700">${v.precio_mayorista}</td>
                        <td className="p-4 text-center"><button type="button" onClick={() => handleToggleVarianteStatus(v)} className={`relative inline-flex h-5 w-9 rounded-full ${v.estado === 'ACTIVO' ? 'bg-emerald-500' : 'bg-slate-300'} cursor-pointer`}><span className={`inline-block h-3 w-3 rounded-full bg-white transform transition-transform ${v.estado === 'ACTIVO' ? 'translate-x-5' : 'translate-x-1'} mt-1 ml-0.5`} /></button></td>
                        <td className="p-4 text-center"><button type="button" onClick={() => openVariantModal(v)} className="text-blue-600 font-bold text-xs cursor-pointer bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100">Editar</button></td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL IMÁGENES (UPLOAD A SUPABASE) */}
      {isImageModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-100 flex justify-between">
              <h3 className="text-lg font-bold text-slate-800">{editingImagenId ? 'Editar Información' : 'Subir Imagen a Supabase'}</h3>
              <button onClick={() => setIsImageModalOpen(false)} className="text-slate-400 font-bold text-xl hover:text-slate-600 cursor-pointer">&times;</button>
            </div>
            <form onSubmit={handleSaveImagen} className="p-6 space-y-4">
              {!editingImagenId ? (
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:bg-slate-50 transition-colors">
                  <input type="file" accept="image/jpeg, image/png, image/webp, image/gif" onChange={handleFileChange} className="hidden" id="file-upload" />
                  <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                    {imagenPreview ? <img src={imagenPreview} alt="Preview" className="h-40 object-contain rounded-lg border border-slate-200 mb-2 shadow-sm" /> : <><UploadCloud size={40} className="text-slate-400 mb-3" /><span className="text-sm font-bold text-blue-600">Haz clic para seleccionar archivo</span><span className="text-xs text-slate-500 mt-1">Soporta JPG, PNG, WEBP (Max 5MB)</span></>}
                  </label>
                </div>
              ) : (
                <div className="text-center">
                  <img src={imagenPreview!} alt="Current" className="h-40 object-contain mx-auto rounded-lg border border-slate-200 shadow-sm" />
                  <p className="text-xs text-slate-500 mt-2">Archivo alojado en Supabase.</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div><label className="block text-xs font-bold text-slate-500 uppercase mb-1">Texto Alternativo (SEO)</label><input type="text" value={imagenForm.alt_text} onChange={e => setImagenForm({...imagenForm, alt_text: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-slate-500" placeholder="Ej: Camiseta frontal" /></div>
                <div><label className="block text-xs font-bold text-slate-500 uppercase mb-1">Orden de visualización</label><input type="number" min="0" value={imagenForm.orden} onChange={e => setImagenForm({...imagenForm, orden: Number(e.target.value)})} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-slate-500" /></div>
              </div>
              <label className="flex items-center gap-2 cursor-pointer pt-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <input type="checkbox" checked={imagenForm.es_principal} onChange={e => setImagenForm({...imagenForm, es_principal: e.target.checked})} className="w-5 h-5 text-black rounded cursor-pointer" />
                <span className="text-sm font-bold text-slate-900">Marcar como la imagen principal</span>
              </label>
              <button type="submit" disabled={saving || (!editingImagenId && !imagenFile)} className="w-full bg-black text-white py-3 rounded-xl font-bold hover:bg-slate-800 mt-4 disabled:opacity-50 transition-colors cursor-pointer">{saving ? 'Procesando...' : (editingImagenId ? 'Actualizar Datos' : 'Subir a Supabase')}</button>
            </form>
          </div>
        </div>
      )}

      {/* NUEVO MODAL DE VARIANTES (MÁS ANCHO Y CON SELECTOR DE IMAGEN) */}
      {isVariantModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl overflow-hidden max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                {editingVarianteId ? <><Edit size={22} className="text-black"/> Editar Variante #{editingVarianteId}</> : <><Plus size={22} className="text-black"/> Crear Nueva Variante</>}
              </h3>
              <button onClick={() => setIsVariantModalOpen(false)} className="text-slate-400 hover:text-slate-600 font-bold text-2xl cursor-pointer">&times;</button>
            </div>
            
            <form onSubmit={handleSaveVariante} className="p-6 overflow-y-auto">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* COLUMNA IZQUIERDA: PRECIOS Y ATRIBUTOS */}
                <div className="lg:col-span-2 space-y-6">
                  
                  {/* Precios */}
                  <div>
                    <h4 className="font-bold text-slate-800 flex items-center gap-2 mb-3"><DollarSign size={16} /> Precios y Costos</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div><label className="block text-xs font-bold text-slate-500 uppercase mb-1">Costo Base ($)</label><input type="number" required min="0" step="0.01" value={varianteForm.precio_costo} onChange={e => setVarianteForm({...varianteForm, precio_costo: Number(e.target.value)})} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-black" /></div>
                      <div><label className="block text-xs font-bold text-blue-500 uppercase mb-1">Minorista ($)</label><input type="number" required min="0" step="0.01" value={varianteForm.precio_minorista} onChange={e => setVarianteForm({...varianteForm, precio_minorista: Number(e.target.value)})} className="w-full px-3 py-2 border border-blue-300 rounded-lg outline-none bg-blue-50/30 focus:ring-2 focus:ring-blue-600" /></div>
                      <div><label className="block text-xs font-bold text-emerald-500 uppercase mb-1">Mayorista ($)</label><input type="number" required min="0" step="0.01" value={varianteForm.precio_mayorista} onChange={e => setVarianteForm({...varianteForm, precio_mayorista: Number(e.target.value)})} className="w-full px-3 py-2 border border-emerald-300 rounded-lg outline-none bg-emerald-50/30 focus:ring-2 focus:ring-emerald-600" /></div>
                    </div>
                  </div>

                  {/* Logística */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <div><label className="block text-sm font-bold text-slate-700 mb-1">Peso Físico (Kg)</label><input type="number" min="0" step="0.01" value={varianteForm.peso} onChange={e => setVarianteForm({...varianteForm, peso: Number(e.target.value)})} className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-slate-400" /></div>
                    <div className="flex items-center pt-6"><label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={varianteForm.aplica_paquete} onChange={e => setVarianteForm({...varianteForm, aplica_paquete: e.target.checked})} className="w-5 h-5 text-black rounded" /><span className="text-sm font-bold text-slate-700">Permitir en "Arma tu paquete"</span></label></div>
                  </div>

                  {/* Atributos */}
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-bold text-slate-800 flex items-center gap-2"><Tag size={16} /> Atributos Diferenciadores</h4>
                      <button type="button" onClick={() => setAtributosDinamicos([...atributosDinamicos, { tipo: 'Color', personalizado: '', valor: '' }])} className="text-xs bg-slate-900 text-white px-3 py-1.5 rounded-lg font-bold hover:bg-slate-800 cursor-pointer">+ Añadir Atributo</button>
                    </div>
                    {atributosDinamicos.length === 0 ? (
                      <p className="text-sm text-slate-400 italic bg-slate-50 p-4 rounded-lg border border-dashed border-slate-300">Variante única sin atributos.</p>
                    ) : (
                      <div className="space-y-3">
                        {atributosDinamicos.map((attr, index) => (
                          <div key={index} className="flex gap-2 items-start bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <div className="flex-1 space-y-2">
                              <select value={attr.tipo} onChange={e => { const newArr = [...atributosDinamicos]; newArr[index].tipo = e.target.value; setAtributosDinamicos(newArr); }} className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white outline-none focus:ring-2 focus:ring-slate-500 font-medium">
                                {ATRIBUTOS_PREDEFINIDOS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                              </select>
                              {attr.tipo === "Otro (Personalizado...)" && <input type="text" placeholder="Escribe el nombre..." value={attr.personalizado} onChange={e => { const newArr = [...atributosDinamicos]; newArr[index].personalizado = e.target.value; setAtributosDinamicos(newArr); }} className="w-full px-3 py-1.5 text-sm border border-orange-300 bg-orange-50 rounded-lg outline-none" required />}
                            </div>
                            <span className="text-slate-300 font-bold mt-2">=</span>
                            <input type="text" placeholder="Valor (Ej: Rojo, XL...)" value={attr.valor} onChange={e => { const newArr = [...atributosDinamicos]; newArr[index].valor = e.target.value; setAtributosDinamicos(newArr); }} className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-slate-500 font-bold" required />
                            <button type="button" onClick={() => setAtributosDinamicos(atributosDinamicos.filter((_, i) => i !== index))} className="text-slate-400 hover:text-red-600 p-2 mt-0.5 cursor-pointer bg-white rounded border border-slate-200"><Trash2 size={16}/></button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* COLUMNA DERECHA: SELECCIÓN DE IMAGEN DE GALERÍA */}
                <div className="border-l border-slate-200 pl-8">
                  <h4 className="font-bold text-slate-800 flex items-center gap-2 mb-4"><ImagePlus size={16} /> Imagen de la Variante</h4>
                  
                  {imagenes.length === 0 ? (
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                      <ImageIcon size={32} className="text-slate-300 mx-auto mb-2" />
                      <p className="text-sm text-slate-800 font-medium">No hay imágenes en la galería.</p>
                      <p className="text-xs text-black mt-1">Cierra este panel y sube fotos al producto primero.</p>
                    </div>
                  ) : (
                    <>
                      <p className="text-xs text-slate-500 mb-3">Haz clic en la imagen que deseas asignar a esta variante específica.</p>
                      <div className="grid grid-cols-2 gap-3 max-h-[400px] overflow-y-auto pr-2">
                        {/* Opción para quitar la imagen */}
                        <div 
                          onClick={() => setVarianteForm({...varianteForm, id_imagen: null})}
                          className={`cursor-pointer rounded-xl border-2 flex flex-col items-center justify-center p-4 transition-all ${varianteForm.id_imagen === null ? 'border-black bg-slate-50 ring-2 ring-black/20' : 'border-slate-200 bg-slate-50 hover:border-slate-300'}`}
                        >
                          <ImageIcon size={24} className={varianteForm.id_imagen === null ? 'text-black' : 'text-slate-400'} />
                          <span className={`text-xs mt-2 font-bold ${varianteForm.id_imagen === null ? 'text-slate-800' : 'text-slate-500'}`}>Sin Imagen</span>
                        </div>

                        {/* Imágenes disponibles en la galería */}
                        {imagenes.map(img => (
                          <div 
                            key={img.id_imagen}
                            onClick={() => setVarianteForm({...varianteForm, id_imagen: img.id_imagen})}
                            className={`cursor-pointer rounded-xl border-2 overflow-hidden relative transition-all ${varianteForm.id_imagen === img.id_imagen ? 'border-black ring-2 ring-black/30' : 'border-transparent hover:ring-2 hover:ring-slate-300'}`}
                          >
                            <img src={img.url} className="w-full h-24 object-cover" />
                            {varianteForm.id_imagen === img.id_imagen && (
                              <div className="absolute inset-0 bg-black/10 flex items-center justify-center">
                                <div className="bg-black text-white rounded-full p-1 shadow-lg"><Star size={12}/></div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Botón de Guardado */}
              <div className="mt-8 pt-4 border-t border-slate-100">
                <button type="submit" disabled={saving} className="w-full lg:w-auto lg:float-right bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 disabled:opacity-70 transition-colors flex justify-center items-center gap-2 cursor-pointer shadow-md">
                  <Save size={18} /> {saving ? 'Guardando Variante...' : (editingVarianteId ? 'Actualizar Variante' : 'Crear Variante')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
