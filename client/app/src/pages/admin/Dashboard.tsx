import { useQuery } from '@tanstack/react-query';
import { healthApi } from '@proxy-manager/api';
import { useProxies } from '../../hooks/useProxies';
import { Skeleton } from '../../components/Skeleton';
import { Button } from '@proxy-manager/ui';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['health', 'proxies'],
    queryFn: () => healthApi.getProxyStats(),
    refetchInterval: 30000, // Poll every 30 seconds
  });

  const { data: proxies = [] } = useProxies({ limit: 1000 });

  if (isLoading) {
    return <Skeleton lines={5} />;
  }

  const workingPercentage = stats
    ? ((stats.working / stats.total) * 100).toFixed(1)
    : '0';

  // Calculate latency distribution
  const latencyData = proxies
    .filter((p: { latency?: number | null }) => p.latency !== null && p.latency !== undefined)
    .reduce((acc: Record<string, number>, p: { latency?: number | null }) => {
      const range = Math.floor((p.latency as number) / 100) * 100;
      const key = `${range}-${range + 100}ms`;
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

  const latencyChartData = Object.entries(latencyData).map(([name, value]) => ({
    name,
    value,
  }));

  // Protocol distribution
  const protocolData = proxies.reduce((acc: Record<string, number>, p: { protocol?: string | null }) => {
    const protocol = p.protocol || 'http';
    acc[protocol] = (acc[protocol] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const protocolChartData = Object.entries(protocolData).map(([name, value]) => ({
    name,
    value,
  }));

  const statusData = [
    { name: 'Working', value: stats?.working || 0, color: '#00FF00' },
    { name: 'Dead', value: stats?.dead || 0, color: '#FF0000' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Admin Dashboard</h1>
        <Button variant="secondary" onClick={() => refetch()}>
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-2">Total Proxies</h3>
          <p className="text-3xl font-bold text-neon-cyan">{stats?.total || 0}</p>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-2">Working Proxies</h3>
          <p className="text-3xl font-bold text-green-400">{stats?.working || 0}</p>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-2">Working %</h3>
          <p className="text-3xl font-bold text-neon-cyan">{workingPercentage}%</p>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-2">Dead Proxies</h3>
          <p className="text-3xl font-bold text-red-400">{stats?.dead || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Status Pie Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-4">Proxy Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Protocol Distribution */}
        {protocolChartData.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-neon-cyan mb-4">Protocol Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={protocolChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#6b7684" />
                <XAxis dataKey="name" stroke="#00FFF7" />
                <YAxis stroke="#00FFF7" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#071023',
                    border: '1px solid #00FFF7',
                    color: '#00FFF7',
                  }}
                />
                <Bar dataKey="value" fill="#00FFF7" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Latency Distribution */}
        {latencyChartData.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-neon-cyan mb-4">Latency Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={latencyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#6b7684" />
                <XAxis dataKey="name" stroke="#00FFF7" />
                <YAxis stroke="#00FFF7" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#071023',
                    border: '1px solid #00FFF7',
                    color: '#00FFF7',
                  }}
                />
                <Bar dataKey="value" fill="#FF00E1" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {stats?.statistics && Object.keys(stats.statistics).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-neon-cyan mb-4">Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.statistics).map(([key, value]) => (
              <div key={key}>
                <p className="text-muted text-sm">{key}</p>
                <p className="text-neon-cyan font-semibold">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

