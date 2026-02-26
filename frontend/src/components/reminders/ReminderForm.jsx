import { useState, useEffect } from 'react';

export default function ReminderForm({ reminder, workers, vehicles, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    assigned_worker_id: '',
    vehicle_id: '',
    reminder_type: '',
    scheduled_date: '',
    message: '',
  });

  useEffect(() => {
    if (reminder) {
      setForm({
        assigned_worker_id: reminder.assigned_worker?.id || '',
        vehicle_id: reminder.vehicle?.id || '',
        reminder_type: reminder.reminder_type || '',
        scheduled_date: reminder.scheduled_date || '',
        message: reminder.message || '',
      });
    }
  }, [reminder]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...form,
      assigned_worker_id: Number(form.assigned_worker_id),
    };
    if (form.vehicle_id) data.vehicle_id = Number(form.vehicle_id);
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Asignar a Trabajador *</label>
        <select
          required
          value={form.assigned_worker_id}
          onChange={(e) => setForm({ ...form, assigned_worker_id: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Seleccione un trabajador</option>
          {workers?.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Vehículo (opcional)</label>
        <select
          value={form.vehicle_id}
          onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Sin vehículo</option>
          {vehicles?.map((v) => (
            <option key={v.id} value={v.id}>{v.make} {v.model} - {v.plate}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
          <select
            required
            value={form.reminder_type}
            onChange={(e) => setForm({ ...form, reminder_type: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Seleccione tipo</option>
            <option value="oil_change">Cambio de Aceite</option>
            <option value="inspection">Inspección</option>
            <option value="tire_rotation">Rotación de Llantas</option>
            <option value="brake_check">Revisión de Frenos</option>
            <option value="general">General</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Programada *</label>
          <input
            type="date"
            required
            value={form.scheduled_date}
            onChange={(e) => setForm({ ...form, scheduled_date: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Mensaje *</label>
        <textarea
          required
          rows={3}
          value={form.message}
          onChange={(e) => setForm({ ...form, message: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Mensaje de recordatorio a enviar al trabajador..."
        />
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          {reminder ? 'Actualizar Recordatorio' : 'Agregar Recordatorio'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg text-sm font-medium hover:bg-gray-200"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
