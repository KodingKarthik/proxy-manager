import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import AppRoot from './pages/app/AppRoot';
import AdminRoot from './pages/admin/AdminRoot';
import { RequireAuth } from './components/RequireAuth';
import { RequireAdmin } from './components/RequireAdmin'; // Temporary comment to trigger re-evaluation

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/app/proxies" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/app/*"
          element={
            <RequireAuth>
              <AppRoot />
            </RequireAuth>
          }
        />
        <Route
          path="/admin/*"
          element={
            <RequireAuth>
              <RequireAdmin>
                <AdminRoot />
              </RequireAdmin>
            </RequireAuth>
          }
        />
      </Routes>
    </AuthProvider>
  );
}

export default App;

