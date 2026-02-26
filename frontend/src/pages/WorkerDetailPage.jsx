import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getWorker } from '../api/workers';
import { getSingleWorkerMetrics } from '../api/metrics';
import StatusBadge from '../components/common/StatusBadge';

export default function WorkerDetailPage() {
  const { id } = useParams();
  const [worker, setWorker] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getWorker(id), getSingleWorkerMetrics(id)])
      .then(([workerRes, metricsRes]) => {
        setWorker(workerRes.data);
        setMetrics(metricsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!worker) return <p className="text-gray-500">Worker not found</p>;

  const m = metrics?.metrics;

  return (
    <div className="space-y-6">
      <Link to="/workers" className="text-blue-600 hover:text-blue-800 text-sm">&larr; Back to Workers</Link>

      {/* Worker info card */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">{worker.name}</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${worker.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {worker.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><span className="text-gray-500">Phone:</span> <span className="font-medium">{worker.phone}</span></div>
          <div><span className="text-gray-500">Email:</span> <span className="font-medium">{worker.email}</span></div>
          <div><span className="text-gray-500">Role:</span> <span className="font-medium">{worker.role || '—'}</span></div>
          <div><span className="text-gray-500">Service:</span> <span className="font-medium">{worker.givingServiceTo || '—'}</span></div>
        </div>
      </div>

      {/* Productivity metrics */}
      {m && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-xl border p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{m.total_assigned}</p>
            <p className="text-xs text-gray-500 mt-1">Assigned</p>
          </div>
          <div className="bg-white rounded-xl border p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{m.total_completed}</p>
            <p className="text-xs text-gray-500 mt-1">Completed</p>
          </div>
          <div className="bg-white rounded-xl border p-4 text-center">
            <p className="text-2xl font-bold text-blue-500">{m.total_sent}</p>
            <p className="text-xs text-gray-500 mt-1">Sent</p>
          </div>
          <div className="bg-white rounded-xl border p-4 text-center">
            <p className="text-2xl font-bold text-yellow-600">{m.total_pending}</p>
            <p className="text-xs text-gray-500 mt-1">Pending</p>
          </div>
          <div className="bg-white rounded-xl border p-4 text-center">
            <p className="text-2xl font-bold text-purple-600">{m.completion_rate}%</p>
            <p className="text-xs text-gray-500 mt-1">Completion Rate</p>
          </div>
        </div>
      )}

      {/* Vehicles */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Assigned Vehicles ({worker.vehicles?.length || 0})</h3>
        {worker.vehicles?.length > 0 ? (
          <div className="space-y-2">
            {worker.vehicles.map((v) => (
              <div key={v.id} className="flex items-center gap-4 text-sm py-2 border-b last:border-0">
                <span className="font-medium">{v.make} {v.model}</span>
                <span className="text-gray-500">{v.plate}</span>
                <span className="text-gray-400">{v.year}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No vehicles assigned</p>
        )}
      </div>

      {/* Reminders */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Reminders ({worker.reminders?.length || 0})</h3>
        {worker.reminders?.length > 0 ? (
          <div className="space-y-2">
            {worker.reminders.map((r) => (
              <div key={r.id} className="flex items-center gap-4 text-sm py-2 border-b last:border-0">
                <span className="font-medium">{r.reminder_type}</span>
                <span className="text-gray-500">{r.scheduled_date}</span>
                <StatusBadge status={r.status} />
                <span className="text-gray-400 truncate flex-1">{r.message}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No reminders assigned</p>
        )}
      </div>
    </div>
  );
}
