import { useState, useEffect } from 'react';
import { getReminders, createReminder, updateReminder, deleteReminder, sendReminder } from '../api/reminders';
import { getWorkers } from '../api/workers';
import { getVehicles } from '../api/vehicles';
import { useAuth } from '../hooks/useAuth';
import DataTable from '../components/common/DataTable';
import Modal from '../components/common/Modal';
import StatusBadge from '../components/common/StatusBadge';
import ReminderForm from '../components/reminders/ReminderForm';

export default function RemindersPage() {
  const [reminders, setReminders] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingReminder, setEditingReminder] = useState(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterWorker, setFilterWorker] = useState('');
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const fetchData = () => {
    setLoading(true);
    const params = {};
    if (filterStatus) params.status = filterStatus;
    if (filterWorker) params.worker_id = filterWorker;

    Promise.all([getReminders(params), getWorkers(), getVehicles()])
      .then(([rRes, wRes, vRes]) => {
        setReminders(rRes.data);
        setWorkers(wRes.data);
        setVehicles(vRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [filterStatus, filterWorker]);

  const handleSubmit = async (data) => {
    try {
      if (editingReminder) {
        await updateReminder(editingReminder.id, data);
      } else {
        await createReminder(data);
      }
      setModalOpen(false);
      setEditingReminder(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Operación fallida');
    }
  };

  const handleSend = async (reminder) => {
    if (!confirm(`¿Enviar recordatorio a ${reminder.assigned_worker?.name}?`)) return;
    try {
      await sendReminder(reminder.id);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Error al enviar');
    }
  };

  const handleComplete = async (reminder) => {
    try {
      await updateReminder(reminder.id, { status: 'completed' });
      fetchData();
    } catch (err) {
      alert('Error al marcar como completado');
    }
  };

  const handleDelete = async (reminder) => {
    if (!confirm('¿Eliminar este recordatorio?')) return;
    try {
      await deleteReminder(reminder.id);
      fetchData();
    } catch (err) {
      alert('Error al eliminar');
    }
  };

  const columns = [
    { key: 'reminder_type', label: 'Tipo', render: (row) => row.reminder_type.replace('_', ' ') },
    { key: 'worker', label: 'Trabajador', render: (row) => row.assigned_worker?.name || '—' },
    { key: 'vehicle', label: 'Vehículo', render: (row) => row.vehicle ? `${row.vehicle.make} ${row.vehicle.model}` : '—' },
    { key: 'scheduled_date', label: 'Programado' },
    { key: 'status', label: 'Estado', render: (row) => <StatusBadge status={row.status} /> },
    ...(isAdmin
      ? [{
          key: 'actions',
          label: 'Acciones',
          render: (row) => (
            <div className="flex gap-2">
              {row.status === 'pending' && (
                <>
                  <button onClick={() => handleSend(row)} className="text-blue-600 hover:text-blue-800 text-xs font-medium">Enviar</button>
                  <button onClick={() => handleComplete(row)} className="text-green-600 hover:text-green-800 text-xs font-medium">Completar</button>
                </>
              )}
              <button onClick={() => { setEditingReminder(row); setModalOpen(true); }} className="text-gray-600 hover:text-gray-800 text-xs font-medium">Editar</button>
              <button onClick={() => handleDelete(row)} className="text-red-600 hover:text-red-800 text-xs font-medium">Eliminar</button>
            </div>
          ),
        }]
      : []),
  ];

  if (loading && reminders.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Recordatorios</h2>
        {isAdmin && (
          <button
            onClick={() => { setEditingReminder(null); setModalOpen(true); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            + Nuevo Recordatorio
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Todos los Estados</option>
          <option value="pending">Pendiente</option>
          <option value="sent">Enviado</option>
          <option value="completed">Completado</option>
        </select>
        <select
          value={filterWorker}
          onChange={(e) => setFilterWorker(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Todos los Trabajadores</option>
          {workers.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </div>

      <DataTable columns={columns} data={reminders} />

      <Modal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditingReminder(null); }}
        title={editingReminder ? 'Editar Recordatorio' : 'Nuevo Recordatorio'}
      >
        <ReminderForm
          reminder={editingReminder}
          workers={workers}
          vehicles={vehicles}
          onSubmit={handleSubmit}
          onCancel={() => { setModalOpen(false); setEditingReminder(null); }}
        />
      </Modal>
    </div>
  );
}
