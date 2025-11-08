import { useState } from 'react';
import { useAdminLogs, useExportAdminLogs } from '../../hooks/useAdmin';
import { Table, type TableColumn, Button } from '@proxy-manager/ui';
import type { ActivityLogResponse } from '@proxy-manager/api';
import { format } from 'date-fns';

const AdminLogs = () => {
  const [page, setPage] = useState(0);
  const limit = 25;
  const { data: logs = [], isLoading } = useAdminLogs({
    limit,
    offset: page * limit,
  });
  const exportLogs = useExportAdminLogs();

  const columns: TableColumn<ActivityLogResponse>[] = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      accessor: (log) => format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss'),
    },
    {
      key: 'user_id',
      header: 'User ID',
      accessor: (log) => log.user_id,
    },
    {
      key: 'endpoint',
      header: 'Endpoint',
      accessor: (log) => log.endpoint,
    },
    {
      key: 'method',
      header: 'Method',
      accessor: (log) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            log.method === 'GET'
              ? 'bg-blue-500 bg-opacity-20 text-blue-400'
              : log.method === 'POST'
              ? 'bg-green-500 bg-opacity-20 text-green-400'
              : 'bg-yellow-500 bg-opacity-20 text-yellow-400'
          }`}
        >
          {log.method}
        </span>
      ),
    },
    {
      key: 'status_code',
      header: 'Status Code',
      accessor: (log) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            log.status_code >= 200 && log.status_code < 300
              ? 'bg-green-500 bg-opacity-20 text-green-400'
              : log.status_code >= 400
              ? 'bg-red-500 bg-opacity-20 text-red-400'
              : 'bg-yellow-500 bg-opacity-20 text-yellow-400'
          }`}
        >
          {log.status_code}
        </span>
      ),
    },
    {
      key: 'target_url',
      header: 'Target URL',
      accessor: (log) => log.target_url || 'N/A',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Admin Logs</h1>
        <Button
          variant="secondary"
          onClick={() => exportLogs({ limit, offset: page * limit })}
        >
          Export CSV
        </Button>
      </div>

      <Table
        columns={columns}
        data={logs}
        isLoading={isLoading}
        emptyMessage="No logs found"
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
          disabled={logs.length < limit}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

export default AdminLogs;

