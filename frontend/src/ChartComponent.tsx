import React from 'react';
import { Chart, CandlestickSeries } from 'react-lightweight-charts-simple';
import { UTCTimestamp } from 'lightweight-charts';

// The kline interface remains the same, but we need to ensure the data format matches
export interface Kline {
    time: UTCTimestamp;
    open: number;
    high: number;
    low: number;
    close: number;
}

interface ChartComponentProps {
    data: Kline[];
}

const ChartComponent: React.FC<ChartComponentProps> = ({ data }) => {

    const chartOptions = {
        layout: {
            background: { color: '#1e1e1e' },
            textColor: '#e0e0e0',
        },
        grid: {
            vertLines: { color: '#333' },
            horzLines: { color: '#333' },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        }
    };

    const seriesOptions = {
        upColor: '#28a745',
        downColor: '#dc3545',
        borderDownColor: '#dc3545',
        borderUpColor: '#28a745',
        wickDownColor: '#dc3545',
        wickUpColor: '#28a745',
    };

    return (
        <Chart height={400} options={chartOptions}>
            <CandlestickSeries data={data} options={seriesOptions} />
        </Chart>
    );
};

export default ChartComponent;
