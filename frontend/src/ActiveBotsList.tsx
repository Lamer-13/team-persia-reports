import React from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

interface Bot {
    bot_id: string;
    symbol: string;
    strategy: string;
    is_running: boolean;
}

interface ActiveBotsListProps {
    bots: Bot[];
    onBotStopped: () => void; // Callback to refresh the list
}

const ActiveBotsList: React.FC<ActiveBotsListProps> = ({ bots, onBotStopped }) => {

    const handleStopBot = async (botId: string) => {
        try {
            await axios.post(`${API_BASE_URL}/api/bot/stop/${botId}`);
            onBotStopped();
        } catch (error) {
            console.error("Error stopping bot:", error);
            alert("Failed to stop bot.");
        }
    };

    return (
        <div className="card">
            <h2>Active Bots</h2>
            {bots.length === 0 ? (
                <p>No active bots.</p>
            ) : (
                <table className="bots-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Symbol</th>
                            <th>Strategy</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bots.map(bot => (
                            <tr key={bot.bot_id}>
                                <td title={bot.bot_id}>{bot.bot_id.substring(0, 8)}...</td>
                                <td>{bot.symbol}</td>
                                <td>{bot.strategy}</td>
                                <td>
                                    <span className={bot.is_running ? 'status-on' : 'status-off'}>
                                        {bot.is_running ? 'Running' : 'Stopped'}
                                    </span>
                                </td>
                                <td>
                                    <button onClick={() => handleStopBot(bot.bot_id)} className="stop-button">
                                        Stop
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default ActiveBotsList;
