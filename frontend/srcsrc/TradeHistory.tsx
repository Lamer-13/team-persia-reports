import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

interface Trade {
    id: number;
    timestamp: string;
    symbol: string;
    side: 'BUY' | 'SELL';
    price: number;
    quantity: number;
    strategy: string;
}

const TradeHistory: React.FC = () => {
    const [trades, setTrades] = useState<Trade[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchTrades = async () => {
            setIsLoading(true);
            try {
                const res = await axios.get<Trade[]>(`${API_BASE_URL}/api/trades`);
                setTrades(res.data);
            } catch (error) {
                console.error("Error fetching trade history:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchTrades();
        // Optional: Refresh history periodically
        const intervalId = setInterval(fetchTrades, 30000); // Refresh every 30 seconds
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="card">
            <h2>Trade History</h2>
            {isLoading && trades.length === 0 ? (
                <p>Loading trades...</p>
            ) : trades.length === 0 ? (
                <p>No trades have been executed yet.</p>
            ) : (
                <div className="table-container">
                    <table className="bots-table">
                        <thead>
                            <tr>
                                <th>Timestamp (UTC)</th>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Strategy</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trades.map(trade => (
                                <tr key={trade.id}>
                                    <td>{new Date(trade.timestamp).toLocaleString('en-GB', { timeZone: 'UTC' })}</td>
                                    <td>{trade.symbol}</td>
                                    <td className={trade.side === 'BUY' ? 'status-on' : 'status-off'}>
                                        {trade.side}
                                    </td>
                                    <td>{trade.price.toFixed(2)}</td>
                                    <td>{trade.quantity}</td>
                                    <td>{trade.strategy}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default TradeHistory;
