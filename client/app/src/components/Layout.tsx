import { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@proxy-manager/ui';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <div className="min-h-screen bg-bg">
      <nav className="bg-panel border-b border-neon-cyan">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/app/proxies" className="text-xl font-bold text-neon-cyan">
                  Proxy Manager
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/app/proxies"
                  className="border-transparent text-neon-cyan hover:border-accent hover:text-accent inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Proxies
                </Link>
                <Link
                  to="/app/get-proxy"
                  className="border-transparent text-neon-cyan hover:border-accent hover:text-accent inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Get Proxy
                </Link>
                <Link
                  to="/app/logs"
                  className="border-transparent text-neon-cyan hover:border-accent hover:text-accent inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Logs
                </Link>
                {isAdmin && (
                  <Link
                    to="/admin/dashboard"
                    className="border-transparent text-neon-magenta hover:border-accent hover:text-accent inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Admin
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-muted text-sm">{user?.username}</span>
              <Button variant="ghost" size="sm" onClick={() => logout()}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
};

