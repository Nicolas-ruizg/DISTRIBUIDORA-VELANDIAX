import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { ProductoResumen } from '../types/index';

interface FavoritesContextProps {
  favorites: ProductoResumen[];
  toggleFavorite: (producto: ProductoResumen) => void;
  isFavorite: (id_producto: number) => boolean;
}

const FavoritesContext = createContext<FavoritesContextProps | undefined>(undefined);

export const FavoritesProvider = ({ children }: { children: ReactNode }) => {
  const [favorites, setFavorites] = useState<ProductoResumen[]>(() => {
    const savedFavs = localStorage.getItem('velandiax_favorites');
    return savedFavs ? JSON.parse(savedFavs) : [];
  });

  useEffect(() => {
    localStorage.setItem('velandiax_favorites', JSON.stringify(favorites));
  }, [favorites]);

  const toggleFavorite = (producto: ProductoResumen) => {
    setFavorites(prev => {
      const existe = prev.find(p => p.id_producto === producto.id_producto);
      if (existe) return prev.filter(p => p.id_producto !== producto.id_producto);
      return [...prev, producto];
    });
  };

  const isFavorite = (id_producto: number) => {
    return favorites.some(p => p.id_producto === id_producto);
  };

  return (
    <FavoritesContext.Provider value={{ favorites, toggleFavorite, isFavorite }}>
      {children}
    </FavoritesContext.Provider>
  );
};

export const useFavorites = () => {
  const context = useContext(FavoritesContext);
  if (!context) throw new Error("useFavorites debe usarse dentro de un FavoritesProvider");
  return context;
};