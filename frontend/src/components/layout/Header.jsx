import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div></div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600">
          {user?.username} <span className="text-gray-400">({user?.role})</span>
        </span>
        <button
          onClick={handleLogout}
          className="text-sm text-red-600 hover:text-red-800 font-medium"
        >
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}
