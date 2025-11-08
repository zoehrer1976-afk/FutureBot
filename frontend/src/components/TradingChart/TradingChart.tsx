/**
 * Trading Chart Component
 * Candlestick chart for price visualization
 */

import { useEffect, useState } from 'react';
import { message, Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { Kline } from '../../types';
import { getKlines } from '../../services';
import dayjs from 'dayjs';

interface TradingChartProps {
  symbol: string;
  interval?: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
}

export default function TradingChart({ symbol, interval = '15m' }: TradingChartProps) {
  const [data, setData] = useState<Kline[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChartData();
    const refreshInterval = setInterval(loadChartData, 60000); // Refresh every minute
    return () => clearInterval(refreshInterval);
  }, [symbol, interval]);

  const loadChartData = async () => {
    try {
      const klines = await getKlines(symbol, { interval, limit: 100 });
      setData(klines);
    } catch (error) {
      message.error('Failed to load chart data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = data.map((kline) => ({
    time: dayjs(kline.timestamp).format('HH:mm'),
    price: kline.close,
    high: kline.high,
    low: kline.low,
    open: kline.open,
  }));

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis domain={['auto', 'auto']} />
        <Tooltip
          formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
          labelStyle={{ color: '#000' }}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#1890ff"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
