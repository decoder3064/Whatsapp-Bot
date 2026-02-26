import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { MdDashboard, MdPeople, MdDirectionsCar, MdNotifications, MdAdminPanelSettings } from 'react-icons/md';

const navItems = [
  { to: '/dashboard', label: 'Tablero', icon: MdDashboard },
  { to: '/workers', label: 'Trabajadores', icon: MdPeople },
  { to: '/vehicles', label: 'Vehículos', icon: MdDirectionsCar },
  { to: '/reminders', label: 'Recordatorios', icon: MdNotifications },
];

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold tracking-tight">Pulse</h1>
        <p className="text-gray-400 text-sm mt-1">Gestión de Flotas</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <item.icon className="text-lg" />
            {item.label}
          </NavLink>
        ))}

        {user?.role === 'admin' && (
          <NavLink
            to="/users"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <MdAdminPanelSettings className="text-lg" />
            Usuarios
          </NavLink>
        )}
      </nav>

      <div className="p-4 border-t border-gray-700">
        <div className="text-sm text-gray-400">
          Sesión iniciada como <span className="text-white font-medium">{user?.username}</span>
        </div>
        <div className="text-xs text-gray-500 capitalize">{user?.role}</div>
      </div>
    </aside>
  );
}
