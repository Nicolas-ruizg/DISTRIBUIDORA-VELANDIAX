import { createContext, useContext, useState, useMemo, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { ProductoDetalle, Variante } from '../types/index';

export interface CartItem {
  producto: ProductoDetalle;
  variante: Variante;
  cantidad: number;
}

interface CartContextProps {
  items: CartItem[];
  totalItems: number;
  esMayorista: boolean;
  subtotal: number;
  addToCart: (producto: ProductoDetalle, variante: Variante, cantidad: number) => void;
  removeFromCart: (id_variante: number) => void;
  updateQuantity: (id_variante: number, cantidad: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextProps | undefined>(undefined);

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<CartItem[]>(() => {
    const savedCart = localStorage.getItem('velandiax_cart');
    return savedCart ? JSON.parse(savedCart) : [];
  });

  useEffect(() => {
    localStorage.setItem('velandiax_cart', JSON.stringify(items));
  }, [items]);

  const totalItems = useMemo(() => items.reduce((acc, item) => acc + item.cantidad, 0), [items]);
  
  const esMayorista = totalItems >= 6;

  const subtotal = useMemo(() => {
    return items.reduce((acc, item) => {
      const precio = esMayorista ? item.variante.precio_mayorista : item.variante.precio_minorista;
      return acc + (precio * item.cantidad);
    }, 0);
  }, [items, esMayorista]);

  const addToCart = (producto: ProductoDetalle, variante: Variante, cantidad: number) => {
    setItems(prev => {
      const existeIndex = prev.findIndex(item => item.variante.id_variante === variante.id_variante);
      
      if (existeIndex >= 0) {
        const nuevoCarrito = [...prev];
        nuevoCarrito[existeIndex].cantidad += cantidad;
        return nuevoCarrito;
      }
      return [...prev, { producto, variante, cantidad }];
    });
  };

  const removeFromCart = (id_variante: number) => {
    setItems(prev => prev.filter(item => item.variante.id_variante !== id_variante));
  };

  const updateQuantity = (id_variante: number, cantidad: number) => {
    if (cantidad <= 0) {
      removeFromCart(id_variante);
      return;
    }
    setItems(prev => prev.map(item => 
      item.variante.id_variante === id_variante ? { ...item, cantidad } : item
    ));
  };

  const clearCart = () => setItems([]);

  return (
    <CartContext.Provider value={{ items, totalItems, esMayorista, subtotal, addToCart, removeFromCart, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) throw new Error("useCart debe usarse dentro de un CartProvider");
  return context;
};