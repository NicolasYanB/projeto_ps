import { useState } from 'react';
import './App.css'; // Importando o CSS
import Auth from './Auth';
import Store from './Store';
import SellerDashboard from './SellerDashboard';

export default function App() {
  const [session, setSession] = useState({ userId: null, userType: null });

  const handleLogin = (userId, userType) => setSession({ userId, userType });
  const handleLogout = () => setSession({ userId: null, userType: null });

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>NEW Shopee</h1>
        {session.userId && (
          <div className="user-info">
            <span>Olá, <strong>{session.userId}</strong></span>
            <button className="btn-outline btn-small" onClick={handleLogout}>Sair</button>
          </div>
        )}
      </header>
      
      {!session.userId ? (
        <div className="auth-container">
          <Auth onAuthSuccess={handleLogin} />
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <p>Ou veja nossos produtos sem logar:</p>
          </div>
          <Store userId={null} />
        </div>
      ) : (
        <>
          {session.userType === '3' && <SellerDashboard userId={session.userId} />}
          <Store userId={session.userId} />
        </>
      )}
    </div>
  );
}