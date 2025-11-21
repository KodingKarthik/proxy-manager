import { Routes, Route } from 'react-router-dom';
import { Layout } from '../../components/Layout';
import ProxiesPage from './proxies/ProxiesPage';
import ProxyDetail from './proxies/ProxyDetail';
import GetProxyPage from './get-proxy/GetProxyPage';
import UserLogs from './logs/UserLogs';
import ApiKeysPage from './api-keys/ApiKeysPage';

const AppRoot = () => {
  return (
    <Layout>
      <Routes>
        <Route path="proxies" element={<ProxiesPage />} />
        <Route path="proxies/:id" element={<ProxyDetail />} />
        <Route path="get-proxy" element={<GetProxyPage />} />
        <Route path="logs" element={<UserLogs />} />
        <Route path="api-keys" element={<ApiKeysPage />} />
      </Routes>
    </Layout>
  );
};

export default AppRoot;

