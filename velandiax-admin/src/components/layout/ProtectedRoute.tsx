import { Navigate, Outlet } from 'react-router-dom';
import { getAuthUser } from '../../utils/auth';

export const ProtectedRoute = () => {
  const token = localStorage.getItem('admin_token');
  const user = getAuthUser();

  // Si no hay token, lo mandamos expulsado al login
  if (!token || !user) {
    return <Navigate to="/admin/login" replace />;
  }

  // Si hay token, renderizamos la pantalla que solicitó
  return <Outlet />;
};
