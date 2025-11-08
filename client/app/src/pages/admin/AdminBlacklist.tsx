import { useState } from 'react';
import { useBlacklist, useCreateBlacklistRule, useDeleteBlacklistRule } from '../../hooks/useBlacklist';
import { Table, type TableColumn, Button, Modal, Input } from '@proxy-manager/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { BlacklistResponse } from '@proxy-manager/api';

const blacklistSchema = z.object({
  pattern: z.string().min(1, 'Pattern is required'),
  description: z.string().optional(),
});

type BlacklistFormData = z.infer<typeof blacklistSchema>;

const AdminBlacklist = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [ruleToDelete, setRuleToDelete] = useState<BlacklistResponse | null>(null);

  const { data: rules = [], isLoading } = useBlacklist();
  const createMutation = useCreateBlacklistRule();
  const deleteMutation = useDeleteBlacklistRule();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<BlacklistFormData>({
    resolver: zodResolver(blacklistSchema),
  });

  const onSubmit = async (data: BlacklistFormData) => {
    await createMutation.mutateAsync({
      pattern: data.pattern,
      description: data.description || null,
    });
    reset();
    setIsAddModalOpen(false);
  };

  const handleDelete = async () => {
    if (ruleToDelete) {
      await deleteMutation.mutateAsync(ruleToDelete.id);
      setRuleToDelete(null);
    }
  };

  const columns: TableColumn<BlacklistResponse>[] = [
    {
      key: 'id',
      header: 'ID',
      accessor: (rule) => rule.id,
    },
    {
      key: 'pattern',
      header: 'Pattern',
      accessor: (rule) => <code className="text-neon-cyan">{rule.pattern}</code>,
    },
    {
      key: 'description',
      header: 'Description',
      accessor: (rule) => rule.description || 'N/A',
    },
    {
      key: 'created_at',
      header: 'Created',
      accessor: (rule) => new Date(rule.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      accessor: (rule) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setRuleToDelete(rule);
          }}
          className="text-neon-magenta hover:text-accent text-sm"
        >
          Delete
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-neon-cyan">Admin Blacklist</h1>
        <Button variant="primary" onClick={() => setIsAddModalOpen(true)}>
          Add Rule
        </Button>
      </div>

      <Table columns={columns} data={rules} isLoading={isLoading} emptyMessage="No blacklist rules found" />

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Blacklist Rule"
        footer={
          <>
            <Button variant="ghost" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit(onSubmit)}
              isLoading={createMutation.isPending}
            >
              Add
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Pattern (Regex)"
            {...register('pattern')}
            error={errors.pattern?.message}
            placeholder=".*\\.example\\.com"
          />
          <Input
            label="Description (optional)"
            {...register('description')}
            error={errors.description?.message}
          />
        </form>
      </Modal>

      {ruleToDelete && (
        <Modal
          isOpen={!!ruleToDelete}
          onClose={() => setRuleToDelete(null)}
          title="Delete Blacklist Rule"
          footer={
            <>
              <Button variant="ghost" onClick={() => setRuleToDelete(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDelete} isLoading={deleteMutation.isPending}>
                Delete
              </Button>
            </>
          }
        >
          <p>Are you sure you want to delete this blacklist rule?</p>
          <code className="block mt-2 text-neon-cyan">{ruleToDelete.pattern}</code>
        </Modal>
      )}
    </div>
  );
};

export default AdminBlacklist;

