import { useState, useEffect } from 'react';
import { getUsers, register, updateUser } from '../api/auth';
import { useAuth } from '../hooks/useAuth';
import DataTable from '../components/common/DataTable';
import Modal from '../components/common/Modal';
import UserForm from '../components/users/UserForm';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const { user } = useAuth();

  if (user?.role !== 'admin') {
    return <p className="text-red-600">Acceso denegado. Solo administradores.</p>;
  }

  const fetchUsers = () => {
    setLoading(true);
    getUsers()
      .then((res) => setUsers(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async (data) => {
    try {
      await register(data);
      setModalOpen(false);
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.error || 'Error al crear usuario');
    }
  };

  const handleToggleRole = async (u) => {
    const newRole = u.role === 'admin' ? 'viewer' : 'admin';
    try {
      await updateUser(u.id, { role: newRole });
      fetchUsers();
    } catch (err) {
      alert('Error al actualizar el rol');
    }
  };

  const handleToggleActive = async (u) => {
    try {
      await updateUser(u.id, { is_active: !u.is_active });
      fetchUsers();
    } catch (err) {
      alert('Error al actualizar el estado');
    }
  };

  const columns = [
    { key: 'username', label: 'Usuario' },
    { key: 'email', label: 'Correo' },
    {
      key: 'role',
      label: 'Rol',
      render: (row) => (
        <button
          onClick={() => handleToggleRole(row)}
          className={`px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer ${
            row.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
          }`}
        >
          {row.role}
        </button>
      ),
    },
    {
      key: 'is_active',
      label: 'Estado',
      render: (row) => (
        <button
          onClick={() => handleToggleActive(row)}
          className={`px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer ${
            row.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {row.is_active ? 'Activo' : 'Inactivo'}
        </button>
      ),
    },
    { key: 'created_at', label: 'Creado', render: (row) => new Date(row.created_at).toLocaleDateString() },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Usuarios</h2>
        <button
          onClick={() => setModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          + Agregar Usuario
        </button>
      </div>

      <DataTable columns={columns} data={users} />

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Nuevo Usuario">
        <UserForm onSubmit={handleCreate} onCancel={() => setModalOpen(false)} />
      </Modal>
    </div>
  );
}
