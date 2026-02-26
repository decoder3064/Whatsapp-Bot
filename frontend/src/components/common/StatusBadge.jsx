const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  sent: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
};

const statusLabels = {
  pending: 'Pendiente',
  sent: 'Enviado',
  completed: 'Completado',
  overdue: 'Vencido',
};

export default function StatusBadge({ status }) {
  const color = statusColors[status] || 'bg-gray-100 text-gray-800';
  const label = statusLabels[status] || status;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}
