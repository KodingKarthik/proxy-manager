import { useState } from 'react';
import { Modal, Button, Table, type TableColumn } from '@proxy-manager/ui';
import { parseCsv, type CsvRow, type CsvValidationError, csvTemplate } from '../utils/csvParser';
import type { ProxyCreate } from '@proxy-manager/api';

interface CsvImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (proxies: ProxyCreate[]) => Promise<void>;
  isLoading?: boolean;
}

export const CsvImportModal: React.FC<CsvImportModalProps> = ({
  isOpen,
  onClose,
  onImport,
  isLoading = false,
}) => {
  const [csvText, setCsvText] = useState('');
  const [parsedData, setParsedData] = useState<{ rows: CsvRow[]; errors: CsvValidationError[] } | null>(null);
  const [importProgress, setImportProgress] = useState<{ current: number; total: number } | null>(null);

  const handleParse = () => {
    const result = parseCsv(csvText);
    setParsedData(result);
  };

  const handleImport = async () => {
    if (!parsedData || parsedData.errors.length > 0 || parsedData.rows.length === 0) {
      return;
    }

    setImportProgress({ current: 0, total: parsedData.rows.length });

    try {
      const proxies: ProxyCreate[] = parsedData.rows.map((row) => ({
        ip: row.ip,
        port: row.port,
        protocol: row.protocol || 'http',
        username: row.username || null,
        password: row.password || null,
      }));

      await onImport(proxies);
      setCsvText('');
      setParsedData(null);
      setImportProgress(null);
      onClose();
    } catch (error) {
      console.error('Import failed:', error);
    } finally {
      setImportProgress(null);
    }
  };

  const handleDownloadTemplate = () => {
    const blob = new Blob([csvTemplate], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'proxy-template.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const columns: TableColumn<CsvRow>[] = [
    {
      key: 'ip',
      header: 'IP',
      accessor: (row) => row.ip,
    },
    {
      key: 'port',
      header: 'Port',
      accessor: (row) => row.port,
    },
    {
      key: 'protocol',
      header: 'Protocol',
      accessor: (row) => row.protocol || 'http',
    },
    {
      key: 'username',
      header: 'Username',
      accessor: (row) => row.username || 'N/A',
    },
  ];

  const errorColumns: TableColumn<CsvValidationError>[] = [
    {
      key: 'row',
      header: 'Row',
      accessor: (error) => error.row,
    },
    {
      key: 'field',
      header: 'Field',
      accessor: (error) => error.field,
    },
    {
      key: 'message',
      header: 'Message',
      accessor: (error) => error.message,
    },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Import Proxies from CSV"
      size="xl"
      footer={
        <>
          <Button variant="ghost" onClick={handleDownloadTemplate}>
            Download Template
          </Button>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleParse}
            disabled={!csvText.trim()}
          >
            Parse CSV
          </Button>
          {parsedData && parsedData.errors.length === 0 && parsedData.rows.length > 0 && (
            <Button
              variant="primary"
              onClick={handleImport}
              isLoading={isLoading}
            >
              Import {parsedData.rows.length} Proxies
            </Button>
          )}
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-neon-cyan mb-2">
            CSV Content
          </label>
          <textarea
            value={csvText}
            onChange={(e) => setCsvText(e.target.value)}
            className="w-full px-4 py-2 bg-panel border border-neon-cyan rounded-lg text-neon-cyan font-mono text-sm focus:outline-none focus:ring-2 focus:ring-neon-cyan"
            rows={10}
            placeholder="ip,port,protocol,username,password&#10;192.168.1.1,8080,http,user1,pass1"
          />
        </div>

        {parsedData && (
          <div className="space-y-4">
            {parsedData.errors.length > 0 && (
              <div>
                <h4 className="text-neon-magenta font-semibold mb-2">
                  Validation Errors ({parsedData.errors.length})
                </h4>
                <Table columns={errorColumns} data={parsedData.errors} />
              </div>
            )}

            {parsedData.rows.length > 0 && (
              <div>
                <h4 className="text-neon-cyan font-semibold mb-2">
                  Preview ({parsedData.rows.length} rows)
                </h4>
                <Table columns={columns} data={parsedData.rows.slice(0, 10)} />
                {parsedData.rows.length > 10 && (
                  <p className="text-muted text-sm mt-2">
                    Showing first 10 of {parsedData.rows.length} rows
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {importProgress && (
          <div className="bg-panel p-4 rounded-lg">
            <p className="text-neon-cyan mb-2">
              Importing... {importProgress.current} / {importProgress.total}
            </p>
            <div className="w-full bg-bg rounded-full h-2">
              <div
                className="bg-neon-cyan h-2 rounded-full transition-all"
                style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

