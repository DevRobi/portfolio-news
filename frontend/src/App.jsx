import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="dark">
      {/* Force dark mode for premium feel, or remove class to respect system pref */}
      <Dashboard />
    </div>
  );
}

export default App;
