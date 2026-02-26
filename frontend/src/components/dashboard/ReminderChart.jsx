import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ReminderChart({ data }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recordatorios en el Tiempo</h3>
      {data.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No hay datos disponibles</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(d) => new Date(d).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="created" stroke="#6366f1" name="Creados" strokeWidth={2} />
            <Line type="monotone" dataKey="sent" stroke="#3b82f6" name="Enviados" strokeWidth={2} />
            <Line type="monotone" dataKey="completed" stroke="#22c55e" name="Completados" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
