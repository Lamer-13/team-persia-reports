import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import ChartComponent, { Kline } from './ChartComponent';
import BotControlPanel from './BotControlPanel';
import ActiveBotsList from './ActiveBotsList';
import TradeHistory from './TradeHistory';

// --- Configuration ---
const API_BASE_URL = 'http://localhost:5001';

// --- Interfaces ---
interface Bot {
    bot_id: string;
    symbol: string;
    strategy: string;
    is_running: boolean;
}

// --- Main App Component ---
function App() {
    // Global State
    const [serverStatus, setServerStatus] = useState<string>('connecting...');
    const [activeBots, setActiveBots] = useState<Bot[]>([]);

    // Chart State
    const [chartSymbol, setChartSymbol] = useState('BTCUSDT');
    const [chartInterval, setChartInterval] = useState('1m');
    const [klineData, setKlineData] = useState<Kline[]>([]);

    // --- Data Fetching Callbacks ---
    const fetchActiveBots = useCallback(async () => {
        try {
            const res = await axios.get<Bot[]>(`${API_BASE_URL}/api/bots/active`);
            setActiveBots(res.data);
        } catch (error) {
            console.error("Error fetching active bots:", error);
        }
    }, []);

    const fetchKlineData = useCallback(async () => {
        try {
            const res = await axios.get<Kline[]>(`${API_BASE_URL}/api/klines`, {
                params: { symbol: chartSymbol, interval: chartInterval },
            });
            setKlineData(res.data);
        } catch (error) {
            console.error("Error fetching kline data:", error);
            setKlineData([]);
        }
    }, [chartSymbol, chartInterval]);

    const fetchServerStatus = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/status`);
            setServerStatus(res.data.binance_connection === 'ok' ? 'Connected' : 'Binance Error');
        } catch (error) {
            setServerStatus('Error');
        }
    }, []);

    // --- Effects ---
    useEffect(() => {
        fetchServerStatus();
        fetchActiveBots();
    }, [fetchServerStatus, fetchActiveBots]);

    useEffect(() => {
        fetchKlineData();
        const intervalId = setInterval(fetchKlineData, 60000); // Refresh chart every minute
        return () => clearInterval(intervalId);
    }, [fetchKlineData]);

    // --- Render ---
    return (
        <div className="App">
            <header className="App-header">
                <h1>Crypto Trading Bot Dashboard</h1>
                <p className={`status-badge status-${serverStatus.toLowerCase().replace(' ', '-')}`}>
                    Backend Status: <strong>{serverStatus}</strong>
                </p>
            </header>

            <main className="container dashboard-grid">
                <div className="grid-item-main">
                    <div className="card">
                        <h2>{chartSymbol} Chart ({chartInterval})</h2>
                        {/* Add controls here to change symbol/interval later */}
                        <ChartComponent data={klineData} />
                    </div>
                    <TradeHistory />
                </div>

                <div className="grid-item-side">
                    <BotControlPanel onBotLaunched={fetchActiveBots} />
                    <ActiveBotsList bots={activeBots} onBotStopped={fetchActiveBots} />
                </div>
            </main>
        </div>
    );
}

export default App;
