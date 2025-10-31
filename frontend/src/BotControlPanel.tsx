import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

interface BotControlPanelProps {
    onBotLaunched: () => void; // Callback to refresh the list of active bots
}

const BotControlPanel: React.FC<BotControlPanelProps> = ({ onBotLaunched }) => {
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [interval, setInterval] = useState('1m');
    const [strategy, setStrategy] = useState('ma_crossover');
    const [quantity, setQuantity] = useState(0.001);
    const [isLoading, setIsLoading] = useState(false);

    const handleLaunchBot = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/bot/start`, {
                symbol,
                interval,
                strategy,
                quantity,
                // Here you could add strategy-specific params
            });
            onBotLaunched(); // Trigger refresh
        } catch (error) {
            console.error("Error launching bot:", error);
            alert("Failed to launch bot. Check console for details.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>Launch a New Bot</h2>
            <form onSubmit={handleLaunchBot} className="bot-form">
                <div className="form-group">
                    <label>Symbol:</label>
                    <input
                        type="text"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Interval:</label>
                    <select value={interval} onChange={(e) => setInterval(e.target.value)}>
                        <option value="1m">1 minute</option>
                        <option value="5m">5 minutes</option>
                        <option value="15m">15 minutes</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>Strategy:</label>
                    <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                        <option value="ma_crossover">Moving Average Crossover</option>
                        <option value="bollinger_bands">Bollinger Bands</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>Quantity:</label>
                    <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(parseFloat(e.target.value))}
                        step="0.001"
                        min="0"
                        required
                    />
                </div>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Launching...' : 'Launch Bot'}
                </button>
            </form>
        </div>
    );
};

export default BotControlPanel;
