import { useState } from 'react';
import { useAdminUsers, useDeleteUser, usePromoteUser } from '../../hooks/useAdmin';
import { Table, type TableColumn, Button, Modal } from '@proxy-manager/ui';
import type { UserResponse } from '@proxy-manager/api';

const AdminUsers = () => {
  const [page, setPage] = useState(0);
  const [userToDelete, setUserToDelete] = useState<UserResponse | null>(null);
  const [userToPromote, setUserToPromote] = useState<UserResponse | null>(null);
  const limit = 25;

  const { data: users = [], isLoading } = useAdminUsers({
    limit,
    offset: page * limit,
  });
  const deleteMutation = useDeleteUser();
  const promoteMutation = usePromoteUser();

  const columns: TableColumn<UserResponse>[] = [
    {
      key: 'id',
      header: 'ID',
      accessor: (user) => user.id,
    },
    {
      key: 'username',
      header: 'Username',
      accessor: (user) => user.username,
    },
    {
      key: 'email',
      header: 'Email',
      accessor: (user) => user.email,
    },
    {
      key: 'role',
      header: 'Role',
      accessor: (user) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            user.role === 'admin'
              ? 'bg-neon-magenta bg-opacity-20 text-neon-magenta'
              : 'bg-neon-cyan bg-opacity-20 text-neon-cyan'
          }`}
        >
          {user.role}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Active',
      accessor: (user) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            user.is_active
              ? 'bg-green-500 bg-opacity-20 text-green-400'
              : 'bg-red-500 bg-opacity-20 text-red-400'
          }`}
        >
          {user.is_active ? 'Yes' : 'No'}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      accessor: (user) => new Date(user.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      accessor: (user) => (
        <div className="flex space-x-2">
          {user.role !== 'admin' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setUserToPromote(user);
              }}
              className="text-neon-cyan hover:text-accent text-sm"
            >
              Promote
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setUserToDelete(user);
            }}
            className="text-neon-magenta hover:text-accent text-sm"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  const handleDelete = async () => {
    if (userToDelete) {
      await deleteMutation.mutateAsync(userToDelete.id);
      setUserToDelete(null);
    }
  };

  const handlePromote = async () => {
    if (userToPromote) {
      await promoteMutation.mutateAsync(userToPromote.id);
      setUserToPromote(null);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-neon-cyan">Admin Users</h1>

      <Table columns={columns} data={users} isLoading={isLoading} emptyMessage="No users found" />

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
          disabled={users.length < limit}
        >
          Next
        </Button>
      </div>

      {userToDelete && (
        <Modal
          isOpen={!!userToDelete}
          onClose={() => setUserToDelete(null)}
          title="Delete User"
          footer={
            <>
              <Button variant="ghost" onClick={() => setUserToDelete(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDelete} isLoading={deleteMutation.isPending}>
                Delete
              </Button>
            </>
          }
        >
          <p>Are you sure you want to delete user {userToDelete.username}?</p>
        </Modal>
      )}

      {userToPromote && (
        <Modal
          isOpen={!!userToPromote}
          onClose={() => setUserToPromote(null)}
          title="Promote User"
          footer={
            <>
              <Button variant="ghost" onClick={() => setUserToPromote(null)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handlePromote}
                isLoading={promoteMutation.isPending}
              >
                Promote
              </Button>
            </>
          }
        >
          <p>Are you sure you want to promote {userToPromote.username} to admin?</p>
        </Modal>
      )}
    </div>
  );
};

export default AdminUsers;

