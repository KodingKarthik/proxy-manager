import { Table, type TableColumn } from '@proxy-manager/ui';
import type { ProxyResponse } from '@proxy-manager/api';
import { formatDistanceToNow } from 'date-fns';

interface ProxyTableProps {
  proxies: ProxyResponse[];
  isLoading?: boolean;
  onRowClick?: (proxy: ProxyResponse) => void;
  showActions?: boolean;
  onDelete?: (proxy: ProxyResponse) => void;
  onTest?: (proxy: ProxyResponse) => void;
}

export const ProxyTable: React.FC<ProxyTableProps> = ({
  proxies,
  isLoading = false,
  onRowClick,
  showActions = false,
  onDelete,
  onTest,
}) => {
  const columns: TableColumn<ProxyResponse>[] = [
    {
      key: 'ip',
      header: 'IP Address',
      accessor: (proxy) => proxy.ip,
    },
    {
      key: 'port',
      header: 'Port',
      accessor: (proxy) => proxy.port,
    },
    {
      key: 'protocol',
      header: 'Protocol',
      accessor: (proxy) => proxy.protocol || 'http',
    },
    {
      key: 'latency',
      header: 'Latency',
      accessor: (proxy) => (proxy.latency ? `${proxy.latency.toFixed(2)}ms` : 'N/A'),
    },
    {
      key: 'is_working',
      header: 'Status',
      accessor: (proxy) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            proxy.is_working
              ? 'bg-green-500 bg-opacity-20 text-green-400'
              : 'bg-red-500 bg-opacity-20 text-red-400'
          }`}
        >
          {proxy.is_working ? 'Working' : 'Dead'}
        </span>
      ),
    },
    {
      key: 'fail_count',
      header: 'Fail Count',
      accessor: (proxy) => proxy.fail_count,
    },
    {
      key: 'last_checked',
      header: 'Last Checked',
      accessor: (proxy) =>
        proxy.last_checked
          ? formatDistanceToNow(new Date(proxy.last_checked), { addSuffix: true })
          : 'Never',
    },
    {
      key: 'health_score',
      header: 'Health Score',
      accessor: (proxy) => (proxy.health_score ? proxy.health_score.toFixed(2) : 'N/A'),
    },
    {
      key: 'address',
      header: 'Address',
      accessor: (proxy) => proxy.address,
    },
  ];

  if (showActions && (onDelete || onTest)) {
    columns.push({
      key: 'actions',
      header: 'Actions',
      accessor: (proxy) => (
        <div className="flex space-x-2">
          {onTest && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onTest(proxy);
              }}
              className="text-neon-cyan hover:text-accent text-sm"
            >
              Test
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(proxy);
              }}
              className="text-neon-magenta hover:text-accent text-sm"
            >
              Delete
            </button>
          )}
        </div>
      ),
    });
  }

  return (
    <Table
      columns={columns}
      data={proxies}
      isLoading={isLoading}
      onRowClick={onRowClick}
      emptyMessage="No proxies found"
    />
  );
};

