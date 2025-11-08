import { Link, useLocation } from 'react-router-dom';

const AdminSidebar = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/admin/dashboard', label: 'Dashboard' },
    { path: '/admin/proxies', label: 'Proxies' },
    { path: '/admin/users', label: 'Users' },
    { path: '/admin/blacklist', label: 'Blacklist' },
    { path: '/admin/logs', label: 'Logs' },
  ];

  return (
    <nav className="w-64 bg-panel border-r border-neon-cyan min-h-screen p-4">
      <h2 className="text-xl font-bold text-neon-magenta mb-6">Admin Panel</h2>
      <ul className="space-y-2">
        {navItems.map((item) => (
          <li key={item.path}>
            <Link
              to={item.path}
              className={`block px-4 py-2 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-neon-cyan bg-opacity-20 text-neon-cyan border border-neon-cyan'
                  : 'text-muted hover:bg-panel hover:text-neon-cyan'
              }`}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default AdminSidebar;

