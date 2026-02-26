import { useState, useEffect } from 'react';

export default function WorkerForm({ worker, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    name: '',
    phone: '',
    email: '',
    role: '',
    givingServiceTo: '',
  });

  useEffect(() => {
    if (worker) {
      setForm({
        name: worker.name || '',
        phone: worker.phone || '',
        email: worker.email || '',
        role: worker.role || '',
        givingServiceTo: worker.givingServiceTo || '',
      });
    }
  }, [worker]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
        <input
          type="text"
          required
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
        <input
          type="text"
          required
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="+15551234567"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Correo *</label>
        <input
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
        <input
          type="text"
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="ej. conductor, mecánico"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Área de Servicio</label>
        <input
          type="text"
          value={form.givingServiceTo}
          onChange={(e) => setForm({ ...form, givingServiceTo: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="ej. Flota Amazon"
        />
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          {worker ? 'Actualizar Trabajador' : 'Agregar Trabajador'}
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
