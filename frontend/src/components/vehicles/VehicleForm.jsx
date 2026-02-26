import { useState, useEffect } from 'react';

export default function VehicleForm({ vehicle, workers, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    driver_id: '',
    make: '',
    model: '',
    plate: '',
    year: '',
  });

  useEffect(() => {
    if (vehicle) {
      setForm({
        driver_id: vehicle.driver?.id || '',
        make: vehicle.make || '',
        model: vehicle.model || '',
        plate: vehicle.plate || '',
        year: vehicle.year || '',
      });
    }
  }, [vehicle]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...form, driver_id: Number(form.driver_id), year: Number(form.year) });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Conductor *</label>
        <select
          required
          value={form.driver_id}
          onChange={(e) => setForm({ ...form, driver_id: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Seleccione un conductor</option>
          {workers?.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Marca *</label>
          <input
            type="text"
            required
            value={form.make}
            onChange={(e) => setForm({ ...form, make: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Toyota"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Modelo *</label>
          <input
            type="text"
            required
            value={form.model}
            onChange={(e) => setForm({ ...form, model: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Camry"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Placa *</label>
          <input
            type="text"
            required
            value={form.plate}
            onChange={(e) => setForm({ ...form, plate: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="ABC123"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Año *</label>
          <input
            type="number"
            required
            value={form.year}
            onChange={(e) => setForm({ ...form, year: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="2022"
          />
        </div>
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          {vehicle ? 'Actualizar Vehículo' : 'Agregar Vehículo'}
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
