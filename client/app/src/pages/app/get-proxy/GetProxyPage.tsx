import { useState } from 'react';
import { useGetProxyByStrategy, useGetNextProxy, useGetRandomProxy, useGetBestProxy } from '../../../hooks/useProxies';
import { Button } from '@proxy-manager/ui';
import { Input } from '@proxy-manager/ui';
import type { ProxyResponse } from '@proxy-manager/api';

const GetProxyPage = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [selectedProxy, setSelectedProxy] = useState<ProxyResponse | null>(null);
  const [connectionString, setConnectionString] = useState('');
  
  const getByStrategyMutation = useGetProxyByStrategy();
  const getNextMutation = useGetNextProxy();
  const getRandomMutation = useGetRandomProxy();
  const { data: bestProxy, refetch: refetchBest } = useGetBestProxy();

  const formatConnectionString = (proxy: ProxyResponse) => {
    if (proxy.username) {
      return `${proxy.protocol || 'http'}://${proxy.username}@${proxy.ip}:${proxy.port}`;
    }
    return `${proxy.protocol || 'http'}://${proxy.ip}:${proxy.port}`;
  };

  const handleGetByStrategy = async (strategy: string) => {
    try {
      const proxy = await getByStrategyMutation.mutateAsync({
        strategy: strategy as any,
        target_url: targetUrl || null,
      });
      setSelectedProxy(proxy);
      setConnectionString(formatConnectionString(proxy));
    } catch (error) {
      console.error('Failed to get proxy:', error);
    }
  };

  const handleGetNext = async () => {
    try {
      const proxy = await getNextMutation.mutateAsync(targetUrl || null);
      setSelectedProxy(proxy);
      setConnectionString(formatConnectionString(proxy));
    } catch (error) {
      console.error('Failed to get next proxy:', error);
    }
  };

  const handleGetRandom = async () => {
    try {
      const proxy = await getRandomMutation.mutateAsync(targetUrl || null);
      setSelectedProxy(proxy);
      setConnectionString(formatConnectionString(proxy));
    } catch (error) {
      console.error('Failed to get random proxy:', error);
    }
  };

  const handleGetBest = () => {
    if (bestProxy) {
      setSelectedProxy(bestProxy);
      setConnectionString(formatConnectionString(bestProxy));
    } else {
      refetchBest();
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(connectionString);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-neon-cyan">Get Proxy</h1>

      <div className="card space-y-4">
        <Input
          label="Target URL (optional)"
          type="url"
          placeholder="https://example.com"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          helperText="Optional: Filter proxies by target URL against blacklist"
        />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button
            variant="secondary"
            onClick={() => handleGetByStrategy('random')}
            isLoading={getByStrategyMutation.isPending}
          >
            Random
          </Button>
          <Button
            variant="secondary"
            onClick={handleGetNext}
            isLoading={getNextMutation.isPending}
          >
            Next (RR)
          </Button>
          <Button
            variant="secondary"
            onClick={handleGetRandom}
            isLoading={getRandomMutation.isPending}
          >
            Random Working
          </Button>
          <Button
            variant="secondary"
            onClick={handleGetBest}
            isLoading={!bestProxy}
          >
            Best
          </Button>
        </div>
      </div>

      {selectedProxy && (
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-neon-cyan">Selected Proxy</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-muted text-sm">IP Address</label>
              <p className="text-neon-cyan font-mono">{selectedProxy.ip}</p>
            </div>
            <div>
              <label className="text-muted text-sm">Port</label>
              <p className="text-neon-cyan font-mono">{selectedProxy.port}</p>
            </div>
            <div>
              <label className="text-muted text-sm">Protocol</label>
              <p className="text-neon-cyan">{selectedProxy.protocol || 'http'}</p>
            </div>
            <div>
              <label className="text-muted text-sm">Latency</label>
              <p className="text-neon-cyan">
                {selectedProxy.latency ? `${selectedProxy.latency.toFixed(2)}ms` : 'N/A'}
              </p>
            </div>
          </div>

          <div>
            <label className="text-muted text-sm">Connection String</label>
            <div className="flex space-x-2">
              <Input
                value={connectionString}
                readOnly
                className="font-mono"
              />
              <Button variant="secondary" onClick={copyToClipboard}>
                Copy
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GetProxyPage;

