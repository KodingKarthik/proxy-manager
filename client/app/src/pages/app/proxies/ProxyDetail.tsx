import { useParams, useNavigate } from 'react-router-dom';
import { useProxy, useTestProxy } from '../../../hooks/useProxies';
import { Button } from '@proxy-manager/ui';
import { Skeleton } from '../../../components/Skeleton';
import { useState } from 'react';

const ProxyDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const proxyId = id ? parseInt(id, 10) : 0;
  const { data: proxy, isLoading } = useProxy(proxyId);
  const testMutation = useTestProxy();
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleTest = async () => {
    if (!proxy) return;
    try {
      const result = await testMutation.mutateAsync(proxy.id);
      if (result.success) {
        setTestResult(`Success! Latency: ${result.latency?.toFixed(2)}ms`);
      } else {
        setTestResult(`Failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      setTestResult('Test failed');
    }
  };

  if (isLoading) {
    return <Skeleton lines={10} />;
  }

  if (!proxy) {
    return <div className="text-neon-magenta">Proxy not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Proxy Details</h1>
        <Button variant="secondary" onClick={() => navigate('/app/proxies')}>
          Back to List
        </Button>
      </div>

      <div className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-muted text-sm">IP Address</label>
            <p className="text-neon-cyan font-mono">{proxy.ip}</p>
          </div>
          <div>
            <label className="text-muted text-sm">Port</label>
            <p className="text-neon-cyan font-mono">{proxy.port}</p>
          </div>
          <div>
            <label className="text-muted text-sm">Protocol</label>
            <p className="text-neon-cyan">{proxy.protocol || 'http'}</p>
          </div>
          <div>
            <label className="text-muted text-sm">Status</label>
            <p
              className={proxy.is_working ? 'text-green-400' : 'text-red-400'}
            >
              {proxy.is_working ? 'Working' : 'Dead'}
            </p>
          </div>
          <div>
            <label className="text-muted text-sm">Latency</label>
            <p className="text-neon-cyan">
              {proxy.latency ? `${proxy.latency.toFixed(2)}ms` : 'N/A'}
            </p>
          </div>
          <div>
            <label className="text-muted text-sm">Fail Count</label>
            <p className="text-neon-cyan">{proxy.fail_count}</p>
          </div>
          <div>
            <label className="text-muted text-sm">Health Score</label>
            <p className="text-neon-cyan">
              {proxy.health_score ? proxy.health_score.toFixed(2) : 'N/A'}
            </p>
          </div>
          <div>
            <label className="text-muted text-sm">Address</label>
            <p className="text-neon-cyan font-mono">{proxy.address}</p>
          </div>
        </div>

        <div className="border-t border-neon-cyan pt-4">
          <Button
            onClick={handleTest}
            isLoading={testMutation.isPending}
            className="w-full"
          >
            Test Proxy
          </Button>
          {testResult && (
            <div
              className={`mt-4 p-3 rounded ${
                testResult.includes('Success')
                  ? 'bg-green-500 bg-opacity-20 text-green-400'
                  : 'bg-neon-magenta bg-opacity-20 text-neon-magenta'
              }`}
            >
              {testResult}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProxyDetail;

