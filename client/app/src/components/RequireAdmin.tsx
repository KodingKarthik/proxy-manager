import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface RequireAdminProps {
  children: ReactNode;
}

export const RequireAdmin: React.FC<RequireAdminProps> = ({ children }) => {
  const { isAdmin, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner h-8 w-8"></div>
      </div>
    );
  }

  if (!isAdmin) {
    return <Navigate to="/app/proxies" replace />;
  }

  return <>{children}</>;
};

