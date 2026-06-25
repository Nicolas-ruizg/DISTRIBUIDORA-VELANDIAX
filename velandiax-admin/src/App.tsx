import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Context
import { CartProvider } from './context/CartContext';

// Layouts
import { AdminLayout } from './components/layout/AdminLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { StoreLayout } from './features/storefront/StoreLayout';

// Vistes Públiques (Storefront)
import { HomeView } from './features/storefront/HomeView';
import { ProductView } from './features/storefront/ProductView';

import { PackageBuilderView } from './features/storefront/PackageBuilderView';
import { FavoritesView } from './features/storefront/FavoritesView';

// Vistes Administrador (Backoffice)
import { LoginView } from './features/auth/LoginView';
import { Dashboard } from './features/dashboard/Dashboard';
import { CategoriasView } from './features/catalog/CategoriasView';
import { ProductosView } from './features/catalog/ProductosView';
import { ProductoFormView } from './features/catalog/ProductoFormView';
import { PedidosView } from './features/orders/PedidosView';
import { PedidoFormView } from './features/orders/PedidoFormView';
import { PedidoDetalleView } from './features/orders/PedidoDetalleView';
import { FavoritesProvider } from './context/FavoritesContext';
import { CategoryView } from './features/storefront/CategoryView';
import { SaleView } from './features/storefront/SaleView';
import { OrderTrackingView } from './features/storefront/OrderTrackingView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* RUTAS PÚBLICAS DE LA TIENDA (AMB EL CART PROVIDER) */}
        <Route element={<FavoritesProvider><CartProvider><StoreLayout /></CartProvider></FavoritesProvider>}>
          <Route path="/" element={<HomeView />} />
          <Route path="/producto/:id" element={<ProductView />} />
          <Route path="/categoria/:id" element={<CategoryView />} />
          <Route path="/arma-tu-paca" element={<PackageBuilderView />} />
          <Route path="/arma-tu-paquete" element={<Navigate to="/arma-tu-paca" replace />} />
          <Route path="/favoritos" element={<FavoritesView />} />
          <Route path="/sale" element={<SaleView />} />
          <Route path="/seguimiento" element={<OrderTrackingView />} />
        </Route>

        {/* RUTAS DEL ADMINISTRADOR */}
        <Route path="/admin/login" element={<LoginView />} />
        
        <Route path="/admin" element={<ProtectedRoute />}>
          <Route element={<AdminLayout />}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="categorias" element={<CategoriasView />} />
            <Route path="productos" element={<ProductosView />} />
            <Route path="productos/nuevo" element={<ProductoFormView />} />
            <Route path="productos/:id" element={<ProductoFormView />} />
            <Route path="pedidos" element={<PedidosView />} />
            <Route path="pedidos/nuevo" element={<PedidoFormView />} />
            <Route path="pedidos/:id" element={<PedidoDetalleView />} />
            
            <Route index element={<Navigate to="dashboard" replace />} />
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
