import { Navigate, Outlet } from 'react-router-dom';

export const ProtectedRoute = () => {
  const token = localStorage.getItem('admin_token');

  // Si no hay token, lo mandamos expulsado al login
  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }

  // Si hay token, renderizamos la pantalla que solicitó
  return <Outlet />;
};