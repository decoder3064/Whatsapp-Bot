import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <h2 className="text-4xl font-bold text-gray-300">404</h2>
      <p className="text-gray-500 mt-2">Página no encontrada</p>
      <Link to="/dashboard" className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium">
        Ir al Tablero
      </Link>
    </div>
  );
}
