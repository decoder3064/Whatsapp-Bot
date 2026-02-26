import { useState, useEffect } from 'react';
import StatCard from '../components/dashboard/StatCard';
import ReminderChart from '../components/dashboard/ReminderChart';
import WorkerTable from '../components/dashboard/WorkerTable';
import { getDashboard, getWorkerMetrics, getReminderAnalytics } from '../api/metrics';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [workerMetrics, setWorkerMetrics] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboard(),
      getWorkerMetrics(),
      getReminderAnalytics({ group_by: 'day' }),
    ])
      .then(([dashRes, workersRes, chartRes]) => {
        setDashboard(dashRes.data);
        setWorkerMetrics(workersRes.data);
        setChartData(chartRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Tablero</h2>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Trabajadores Activos"
          value={dashboard?.active_workers || 0}
          color="blue"
          to="/workers"
        />
        <StatCard
          label="Total de Vehículos"
          value={dashboard?.total_vehicles || 0}
          color="purple"
          to="/vehicles"
        />
        <StatCard
          label="Recordatorios Pendientes"
          value={dashboard?.reminders?.pending || 0}
          color="yellow"
          to="/reminders"
        />
        <StatCard
          label="Enviados Hoy"
          value={dashboard?.sent_today || 0}
          color="green"
        />
      </div>

      {/* Chart */}
      <ReminderChart data={chartData} />

      {/* Worker productivity */}
      <WorkerTable workers={workerMetrics} />
    </div>
  );
}
