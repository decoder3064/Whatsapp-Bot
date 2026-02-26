import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getWorkers, createWorker, updateWorker, deleteWorker } from '../api/workers';
import { useAuth } from '../hooks/useAuth';
import DataTable from '../components/common/DataTable';
import Modal from '../components/common/Modal';
import WorkerForm from '../components/workers/WorkerForm';

export default function WorkersPage() {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingWorker, setEditingWorker] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';

  const fetchWorkers = () => {
    setLoading(true);
    getWorkers()
      .then((res) => setWorkers(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchWorkers(); }, []);

  const handleSubmit = async (data) => {
    try {
      if (editingWorker) {
        await updateWorker(editingWorker.id, data);
      } else {
        await createWorker(data);
      }
      setModalOpen(false);
      setEditingWorker(null);
      fetchWorkers();
    } catch (err) {
      alert(err.response?.data?.error || 'Operación fallida');
    }
  };

  const handleToggleActive = async (worker) => {
    try {
      await updateWorker(worker.id, { is_active: !worker.is_active });
      fetchWorkers();
    } catch (err) {
      alert('Error al actualizar el estado del trabajador');
    }
  };

  const columns = [
    { key: 'name', label: 'Nombre' },
    { key: 'phone', label: 'Teléfono' },
    { key: 'email', label: 'Correo' },
    { key: 'role', label: 'Rol', render: (row) => row.role || '—' },
    { key: 'givingServiceTo', label: 'Área de Servicio', render: (row) => row.givingServiceTo || '—' },
    {
      key: 'is_active',
      label: 'Estado',
      render: (row) => (
        <button
          onClick={(e) => { e.stopPropagation(); isAdmin && handleToggleActive(row); }}
          className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
            row.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          } ${isAdmin ? 'cursor-pointer' : ''}`}
        >
          {row.is_active ? 'Activo' : 'Inactivo'}
        </button>
      ),
    },
    ...(isAdmin
      ? [{
          key: 'actions',
          label: 'Acciones',
          render: (row) => (
            <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
              <button
                onClick={() => { setEditingWorker(row); setModalOpen(true); }}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Editar
              </button>
            </div>
          ),
        }]
      : []),
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
        <h2 className="text-2xl font-bold text-gray-900">Trabajadores</h2>
        {isAdmin && (
          <button
            onClick={() => { setEditingWorker(null); setModalOpen(true); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            + Agregar Trabajador
          </button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={workers}
        onRowClick={(row) => navigate(`/workers/${row.id}`)}
      />

      <Modal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditingWorker(null); }}
        title={editingWorker ? 'Editar Trabajador' : 'Nuevo Trabajador'}
      >
        <WorkerForm
          worker={editingWorker}
          onSubmit={handleSubmit}
          onCancel={() => { setModalOpen(false); setEditingWorker(null); }}
        />
      </Modal>
    </div>
  );
}
