import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProxies } from '../../../hooks/useProxies';
import { ProxyTable } from '../../../components/ProxyTable';
import { Button } from '@proxy-manager/ui';
import { Input } from '@proxy-manager/ui';

const ProxiesPage = () => {
  const navigate = useNavigate();
  const [workingOnly, setWorkingOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const limit = 25;

  const { data: proxies = [], isLoading } = useProxies({
    working_only: workingOnly,
    limit,
    offset: page * limit,
  });

  const filteredProxies = proxies.filter(
    (proxy) => !search || proxy.ip.includes(search) || proxy.address.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Proxies</h1>
      </div>

      <div className="flex space-x-4 items-center">
        <Input
          type="text"
          placeholder="Search by IP or address..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-md"
        />
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={workingOnly}
            onChange={(e) => setWorkingOnly(e.target.checked)}
            className="rounded border-neon-cyan text-neon-cyan focus:ring-neon-cyan"
          />
          <span className="text-neon-cyan">Working only</span>
        </label>
      </div>

      <ProxyTable
        proxies={filteredProxies}
        isLoading={isLoading}
        onRowClick={(proxy) => navigate(`/app/proxies/${proxy.id}`)}
      />

      <div className="flex justify-between items-center">
        <Button
          variant="secondary"
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
        >
          Previous
        </Button>
        <span className="text-muted">Page {page + 1}</span>
        <Button
          variant="secondary"
          onClick={() => setPage((p) => p + 1)}
          disabled={filteredProxies.length < limit}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

export default ProxiesPage;

