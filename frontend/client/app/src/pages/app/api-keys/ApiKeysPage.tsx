import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiKeysApi, type ApiKeyCreate, type ApiKeyResponse } from '@proxy-manager/api';
import { Button, Table, Modal, Input, type TableColumn } from '@proxy-manager/ui';
import { format } from 'date-fns';

const ApiKeysPage = () => {
    const queryClient = useQueryClient();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [newKeyName, setNewKeyName] = useState('');
    const [newKeyExpiry, setNewKeyExpiry] = useState('');
    const [createdKey, setCreatedKey] = useState<{ key: string; name: string } | null>(null);

    // Fetch API keys
    const {
        data: apiKeys = [],
        isLoading,
        error,
    } = useQuery({
        queryKey: ['apiKeys'],
        queryFn: apiKeysApi.list,
    });

    // Create API key mutation
    const createMutation = useMutation({
        mutationFn: (data: ApiKeyCreate) => apiKeysApi.create(data),
        onSuccess: (data) => {
            setCreatedKey({ key: data.raw_key, name: data.api_key.name });
            setIsCreateModalOpen(false);
            setNewKeyName('');
            setNewKeyExpiry('');
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
        },
    });

    // Revoke API key mutation
    const revokeMutation = useMutation({
        mutationFn: (keyId: number) => apiKeysApi.revoke(keyId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
        },
    });

    const handleCreateKey = () => {
        if (!newKeyName.trim()) {
            return;
        }

        const data: ApiKeyCreate = {
            name: newKeyName.trim(),
            expires_at: newKeyExpiry ? new Date(newKeyExpiry).toISOString() : null,
        };

        createMutation.mutate(data);
    };

    const handleRevokeKey = (keyId: number, keyName: string) => {
        if (window.confirm(`Are you sure you want to revoke the API key "${keyName}"? This action cannot be undone.`)) {
            revokeMutation.mutate(keyId);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    const handleCloseCreatedKeyModal = () => {
        setCreatedKey(null);
    };

    const isExpired = (expiresAt: string | null | undefined) => {
        if (!expiresAt) return false;
        return new Date(expiresAt) < new Date();
    };

    // Define table columns
    const columns: TableColumn<ApiKeyResponse>[] = [
        {
            key: 'name',
            header: 'Name',
            accessor: (row) => <span className="font-medium">{row.name}</span>,
        },
        {
            key: 'prefix',
            header: 'Prefix',
            accessor: (row) => (
                <code className="text-accent bg-bg px-2 py-1 rounded text-sm">
                    {row.prefix}...
                </code>
            ),
        },
        {
            key: 'status',
            header: 'Status',
            accessor: (row) => {
                const expired = isExpired(row.expires_at);
                const inactive = !row.is_active || expired;

                return (
                    <span
                        className={`px-2 py-1 rounded text-xs font-medium ${inactive
                            ? 'bg-neon-magenta/20 text-neon-magenta'
                            : 'bg-neon-cyan/20 text-neon-cyan'
                            }`}
                    >
                        {expired ? 'Expired' : row.is_active ? 'Active' : 'Inactive'}
                    </span>
                );
            },
        },
        {
            key: 'created_at',
            header: 'Created',
            accessor: (row) => (
                <span className="text-muted text-sm">
                    {format(new Date(row.created_at), 'MMM d, yyyy')}
                </span>
            ),
        },
        {
            key: 'expires_at',
            header: 'Expires',
            accessor: (row) => {
                const expired = isExpired(row.expires_at);
                return (
                    <span className={`text-sm ${expired ? 'text-neon-magenta' : 'text-muted'}`}>
                        {row.expires_at ? format(new Date(row.expires_at), 'MMM d, yyyy') : 'Never'}
                    </span>
                );
            },
        },
        {
            key: 'actions',
            header: 'Actions',
            accessor: (row) => (
                <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleRevokeKey(row.id, row.name)}
                    disabled={revokeMutation.isPending}
                >
                    Revoke
                </Button>
            ),
        },
    ];

    if (error) {
        return <div className="text-neon-magenta">Error loading API keys: {(error as Error).message}</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-neon-cyan">API Keys</h1>
                    <p className="text-muted mt-1">Manage your API keys for programmatic access</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                    Create API Key
                </Button>
            </div>

            {!isLoading && apiKeys.length === 0 ? (
                <div className="bg-panel border border-neon-cyan/30 rounded-lg p-8 text-center">
                    <p className="text-muted mb-4">You don't have any API keys yet.</p>
                    <Button onClick={() => setIsCreateModalOpen(true)}>
                        Create Your First API Key
                    </Button>
                </div>
            ) : (
                <div className="bg-panel border border-neon-cyan/30 rounded-lg overflow-hidden">
                    <Table
                        columns={columns as unknown as TableColumn<Record<string, unknown>>[]}
                        data={apiKeys as unknown as Record<string, unknown>[]}
                        isLoading={isLoading}
                        emptyMessage="No API keys found"
                    />
                </div>
            )}

            {/* Create API Key Modal */}
            <Modal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                title="Create New API Key"
            >
                <div className="space-y-4">
                    <div>
                        <label htmlFor="keyName" className="block text-sm font-medium text-neon-cyan mb-2">
                            Key Name *
                        </label>
                        <Input
                            id="keyName"
                            type="text"
                            placeholder="e.g., Production Server"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            required
                        />
                        <p className="text-muted text-xs mt-1">
                            A friendly name to help you identify this key
                        </p>
                    </div>

                    <div>
                        <label htmlFor="keyExpiry" className="block text-sm font-medium text-neon-cyan mb-2">
                            Expiration Date (Optional)
                        </label>
                        <Input
                            id="keyExpiry"
                            type="datetime-local"
                            value={newKeyExpiry}
                            onChange={(e) => setNewKeyExpiry(e.target.value)}
                        />
                        <p className="text-muted text-xs mt-1">
                            Leave empty for a key that never expires
                        </p>
                    </div>

                    <div className="flex justify-end space-x-3 pt-4">
                        <Button
                            variant="ghost"
                            onClick={() => setIsCreateModalOpen(false)}
                            disabled={createMutation.isPending}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleCreateKey}
                            disabled={!newKeyName.trim() || createMutation.isPending}
                        >
                            {createMutation.isPending ? 'Creating...' : 'Create Key'}
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* Created Key Display Modal */}
            <Modal
                isOpen={createdKey !== null}
                onClose={handleCloseCreatedKeyModal}
                title="API Key Created Successfully"
            >
                <div className="space-y-4">
                    <div className="bg-neon-magenta/10 border border-neon-magenta rounded-lg p-4">
                        <p className="text-neon-magenta font-medium mb-2">⚠️ Important</p>
                        <p className="text-sm text-muted">
                            This is the only time you will see this API key. Make sure to copy it and store it securely.
                        </p>
                    </div>

                    {createdKey && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-neon-cyan mb-2">
                                    Key Name
                                </label>
                                <p className="text-foreground">{createdKey.name}</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-neon-cyan mb-2">
                                    API Key
                                </label>
                                <div className="flex items-center space-x-2">
                                    <code className="flex-1 bg-bg border border-neon-cyan/30 rounded px-3 py-2 text-sm break-all">
                                        {createdKey.key}
                                    </code>
                                    <Button
                                        size="sm"
                                        onClick={() => copyToClipboard(createdKey.key)}
                                    >
                                        Copy
                                    </Button>
                                </div>
                            </div>
                        </>
                    )}

                    <div className="flex justify-end pt-4">
                        <Button onClick={handleCloseCreatedKeyModal}>
                            I've Saved My Key
                        </Button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default ApiKeysPage;
