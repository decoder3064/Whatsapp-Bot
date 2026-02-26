import { useState, useEffect } from 'react';
import { getVehicles, createVehicle, updateVehicle, deleteVehicle } from '../api/vehicles';
import { getWorkers } from '../api/workers';
import { useAuth } from '../hooks/useAuth';
import DataTable from '../components/common/DataTable';
import Modal from '../components/common/Modal';
import VehicleForm from '../components/vehicles/VehicleForm';

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const fetchData = () => {
    setLoading(true);
    Promise.all([getVehicles(), getWorkers()])
      .then(([vRes, wRes]) => {
        setVehicles(vRes.data);
        setWorkers(wRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (data) => {
    try {
      if (editingVehicle) {
        await updateVehicle(editingVehicle.id, data);
      } else {
        await createVehicle(data);
      }
      setModalOpen(false);
      setEditingVehicle(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Operación fallida');
    }
  };

  const handleDelete = async (vehicle) => {
    if (!confirm(`¿Eliminar ${vehicle.make} ${vehicle.model} (${vehicle.plate})?`)) return;
    try {
      await deleteVehicle(vehicle.id);
      fetchData();
    } catch (err) {
      alert('Error al eliminar vehículo');
    }
  };

  const columns = [
    { key: 'driver', label: 'Conductor', render: (row) => row.driver?.name || '—' },
    { key: 'make', label: 'Marca' },
    { key: 'model', label: 'Modelo' },
    { key: 'plate', label: 'Placa' },
    { key: 'year', label: 'Año' },
    ...(isAdmin
      ? [{
          key: 'actions',
          label: 'Acciones',
          render: (row) => (
            <div className="flex gap-2">
              <button onClick={() => { setEditingVehicle(row); setModalOpen(true); }} className="text-blue-600 hover:text-blue-800 text-sm font-medium">Editar</button>
              <button onClick={() => handleDelete(row)} className="text-red-600 hover:text-red-800 text-sm font-medium">Eliminar</button>
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
        <h2 className="text-2xl font-bold text-gray-900">Vehículos</h2>
        {isAdmin && (
          <button
            onClick={() => { setEditingVehicle(null); setModalOpen(true); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            + Agregar Vehículo
          </button>
        )}
      </div>

      <DataTable columns={columns} data={vehicles} />

      <Modal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditingVehicle(null); }}
        title={editingVehicle ? 'Editar Vehículo' : 'Nuevo Vehículo'}
      >
        <VehicleForm
          vehicle={editingVehicle}
          workers={workers}
          onSubmit={handleSubmit}
          onCancel={() => { setModalOpen(false); setEditingVehicle(null); }}
        />
      </Modal>
    </div>
  );
}
