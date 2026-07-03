export type UserRole = 'ADMINISTRADOR' | 'VENDEDOR' | 'INVENTARIO';

export interface AuthUser {
  id_usuario: number;
  nombre: string;
  email: string;
  codigo_cuenta?: string | null;
  id_deposito?: string | null;
  deposito?: string | null;
  rol: UserRole;
}

const USER_KEY = 'admin_user';

export const getAuthUser = (): AuthUser | null => {
  const rawUser = localStorage.getItem(USER_KEY);
  if (!rawUser) return null;

  try {
    return JSON.parse(rawUser) as AuthUser;
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
};

export const setAuthUser = (user: AuthUser) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem('admin_token');
  localStorage.removeItem(USER_KEY);
};

export const hasRole = (roles: UserRole[]) => {
  const user = getAuthUser();
  return Boolean(user && roles.includes(user.rol));
};

export const getDefaultAdminPath = (role?: string) => {
  switch (role) {
    case 'VENDEDOR':
      return '/admin/pedidos/nuevo';
    case 'INVENTARIO':
      return '/admin/productos';
    default:
      return '/admin/dashboard';
  }
};
