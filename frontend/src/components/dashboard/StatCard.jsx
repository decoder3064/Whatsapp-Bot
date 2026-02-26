import { useNavigate } from 'react-router-dom';

export default function StatCard({ label, value, color = 'blue', to }) {
  const navigate = useNavigate();
  const colorMap = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
  };

  return (
    <div
      onClick={() => to && navigate(to)}
      className={`rounded-xl border p-6 ${colorMap[color]} ${to ? 'cursor-pointer hover:shadow-md' : ''} transition-shadow`}
    >
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}
