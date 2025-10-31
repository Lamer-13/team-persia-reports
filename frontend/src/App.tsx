import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import NavBar from './NavBar';
import DashboardPage from './pages/DashboardPage';
import BotsPage from './pages/BotsPage';
import HistoryPage from './pages/HistoryPage';

function App() {
    return (
        <Router>
            <NavBar />
            <main className="container">
                <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/bots" element={<BotsPage />} />
                    <Route path="/history" element={<HistoryPage />} />
                </Routes>
            </main>
        </Router>
    );
}

export default App;
