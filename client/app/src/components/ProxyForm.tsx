import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Modal, Button, Input } from '@proxy-manager/ui';
import type { ProxyCreate, ProxyResponse } from '@proxy-manager/api';

const proxySchema = z.object({
  ip: z.string().min(1, 'IP is required'),
  port: z.number().min(1).max(65535),
  protocol: z.enum(['http', 'https', 'socks5']).default('http'),
  username: z.string().optional(),
  password: z.string().optional(),
});

type ProxyFormData = z.infer<typeof proxySchema>;

interface ProxyFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProxyCreate) => Promise<void>;
  proxy?: ProxyResponse | null;
  isLoading?: boolean;
}

export const ProxyForm: React.FC<ProxyFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  proxy,
  isLoading = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProxyFormData>({
    resolver: zodResolver(proxySchema),
    defaultValues: proxy
      ? {
          ip: proxy.ip,
          port: proxy.port,
          protocol: (proxy.protocol as 'http' | 'https' | 'socks5') || 'http',
          username: proxy.username || '',
          password: '',
        }
      : undefined,
  });

  const handleFormSubmit = async (data: ProxyFormData) => {
    await onSubmit({
      ip: data.ip,
      port: data.port,
      protocol: data.protocol,
      username: data.username || null,
      password: data.password || null,
    });
    reset();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={proxy ? 'Edit Proxy' : 'Add Proxy'}
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit(handleFormSubmit)}
            isLoading={isLoading}
          >
            {proxy ? 'Update' : 'Add'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <Input
          label="IP Address"
          type="text"
          {...register('ip')}
          error={errors.ip?.message}
        />

        <Input
          label="Port"
          type="number"
          {...register('port', { valueAsNumber: true })}
          error={errors.port?.message}
        />

        <div>
          <label className="block text-sm font-medium text-neon-cyan mb-1">Protocol</label>
          <select
            {...register('protocol')}
            className="w-full px-4 py-2 bg-panel border border-neon-cyan rounded-lg text-neon-cyan focus:outline-none focus:ring-2 focus:ring-neon-cyan"
          >
            <option value="http">HTTP</option>
            <option value="https">HTTPS</option>
            <option value="socks5">SOCKS5</option>
          </select>
        </div>

        <Input
          label="Username (optional)"
          type="text"
          {...register('username')}
          error={errors.username?.message}
        />

        <Input
          label="Password (optional)"
          type="password"
          {...register('password')}
          error={errors.password?.message}
        />
      </form>
    </Modal>
  );
};

