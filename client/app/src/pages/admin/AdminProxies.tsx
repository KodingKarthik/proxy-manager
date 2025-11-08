import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProxies, useDeleteProxy, useCreateProxy } from '../../hooks/useProxies';
import { ProxyTable } from '../../components/ProxyTable';
import { ProxyForm } from '../../components/ProxyForm';
import { CsvImportModal } from '../../components/CsvImportModal';
import { Button } from '@proxy-manager/ui';
import { ConfirmModal } from '../../components/ConfirmModal';
import { Input } from '@proxy-manager/ui';
import type { ProxyResponse, ProxyCreate } from '@proxy-manager/api';

const AdminProxies = () => {
  const navigate = useNavigate();
  const [workingOnly, setWorkingOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [proxyToDelete, setProxyToDelete] = useState<ProxyResponse | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isCsvImportOpen, setIsCsvImportOpen] = useState(false);
  const limit = 25;

  const { data: proxies = [], isLoading } = useProxies({
    working_only: workingOnly,
    limit,
    offset: page * limit,
  });
  const deleteMutation = useDeleteProxy();
  const createMutation = useCreateProxy();

  const filteredProxies = proxies.filter(
    (proxy: ProxyResponse) => !search || proxy.ip.includes(search) || proxy.address.includes(search)
  );

  const handleDelete = async () => {
    if (proxyToDelete) {
      await deleteMutation.mutateAsync(proxyToDelete.id);
      setProxyToDelete(null);
    }
  };

  const handleAddProxy = async (data: ProxyCreate) => {
    await createMutation.mutateAsync(data);
  };

  const handleBulkImport = async (proxies: ProxyCreate[]) => {
    // Import proxies sequentially to avoid overwhelming the server
    for (const proxy of proxies) {
      await createMutation.mutateAsync(proxy);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Admin Proxies</h1>
        <div className="flex space-x-2">
          <Button variant="secondary" onClick={() => setIsCsvImportOpen(true)}>
            Import CSV
          </Button>
          <Button variant="primary" onClick={() => setIsAddModalOpen(true)}>
            Add Proxy
          </Button>
        </div>
      </div>

      <div className="flex space-x-4 items-center">
        <Input
          type="text"
          placeholder="Search by IP or address..."
          value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          className="max-w-md"
        />
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={workingOnly}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setWorkingOnly(e.target.checked)}
            className="rounded border-neon-cyan text-neon-cyan focus:ring-neon-cyan"
          />
          <span className="text-neon-cyan">Working only</span>
        </label>
      </div>

      <ProxyTable
        proxies={filteredProxies}
        isLoading={isLoading}
        onRowClick={(proxy) => navigate(`/app/proxies/${proxy.id}`)}
        showActions
        onDelete={(proxy) => setProxyToDelete(proxy)}
      />

      <div className="flex justify-between items-center">
        <Button
          variant="secondary"
          onClick={() => setPage((p: number) => Math.max(0, p - 1))}
          disabled={page === 0}
        >
          Previous
        </Button>
        <span className="text-muted">Page {page + 1}</span>
        <Button
          variant="secondary"
          onClick={() => setPage((p: number) => p + 1)}
          disabled={filteredProxies.length < limit}
        >
          Next
        </Button>
      </div>

      <ProxyForm
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddProxy}
        isLoading={createMutation.isPending}
      />

      <CsvImportModal
        isOpen={isCsvImportOpen}
        onClose={() => setIsCsvImportOpen(false)}
        onImport={handleBulkImport}
        isLoading={createMutation.isPending}
      />

      {proxyToDelete && (
        <ConfirmModal
          isOpen={!!proxyToDelete}
          onClose={() => setProxyToDelete(null)}
          onConfirm={handleDelete}
          title="Delete Proxy"
          message={`Are you sure you want to delete proxy ${proxyToDelete.ip}:${proxyToDelete.port}?`}
          isLoading={deleteMutation.isPending}
        />
      )}
    </div>
  );
};

export default AdminProxies;

