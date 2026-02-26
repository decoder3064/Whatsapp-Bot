export default function WorkerTable({ workers }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Productividad de Trabajadores</h3>
      {workers.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No hay datos de trabajadores disponibles</p>
      ) : (
        <div className="space-y-3">
          {workers.slice(0, 10).map((w) => (
            <div key={w.worker_id} className="flex items-center gap-4">
              <div className="w-32 text-sm font-medium text-gray-700 truncate">{w.worker_name}</div>
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all"
                    style={{ width: `${Math.min(w.completion_rate, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm text-gray-600">{w.completion_rate}%</div>
              <div className="w-20 text-right text-xs text-gray-400">{w.total_assigned} tareas</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
