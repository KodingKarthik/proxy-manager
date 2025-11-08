import { Routes, Route } from 'react-router-dom';
import AdminSidebar from '../../components/AdminSidebar';
import Dashboard from './Dashboard';
import AdminProxies from './AdminProxies';
import AdminUsers from './AdminUsers';
import AdminBlacklist from './AdminBlacklist';
import AdminLogs from './AdminLogs';

const AdminRoot = () => {
  return (
    <div className="flex min-h-screen bg-bg">
      <AdminSidebar />
      <main className="flex-1 p-6">
        <Routes>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="proxies" element={<AdminProxies />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="blacklist" element={<AdminBlacklist />} />
          <Route path="logs" element={<AdminLogs />} />
        </Routes>
      </main>
    </div>
  );
};

export default AdminRoot;

