import { Navigate } from 'react-router-dom';
import { getAuthUser, getDefaultAdminPath, type UserRole } from '../../utils/auth';

interface RoleRouteProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
}

export const RoleRoute = ({ allowedRoles, children }: RoleRouteProps) => {
  const user = getAuthUser();

  if (!user) {
    return <Navigate to="/admin/login" replace />;
  }

  if (!allowedRoles.includes(user.rol)) {
    return <Navigate to={getDefaultAdminPath(user.rol)} replace />;
  }

  return <>{children}</>;
};
