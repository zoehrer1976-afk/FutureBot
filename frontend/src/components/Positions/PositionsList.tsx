/**
 * Positions List Component
 * Display open trading positions
 */

import { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, message, Popconfirm } from 'antd';
import { CloseOutlined } from '@ant-design/icons';
import type { Position } from '../../types';
import { getPositions, closePosition } from '../../services';
import type { ColumnsType } from 'antd/es/table';

export default function PositionsList() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPositions();
    const interval = setInterval(loadPositions, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadPositions = async () => {
    try {
      const data = await getPositions();
      setPositions(data.positions);
    } catch (error) {
      console.error('Failed to load positions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = async (id: string) => {
    try {
      await closePosition(id);
      message.success('Position closed successfully');
      loadPositions();
    } catch (error) {
      message.error('Failed to close position');
      console.error(error);
    }
  };

  const columns: ColumnsType<Position> = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <strong>{symbol}</strong>,
    },
    {
      title: 'Side',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'long' ? 'green' : 'red'}>
          {side.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      align: 'right',
    },
    {
      title: 'Entry Price',
      dataIndex: 'entry_price',
      key: 'entry_price',
      align: 'right',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Current Price',
      dataIndex: 'current_price',
      key: 'current_price',
      align: 'right',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'P&L',
      key: 'pnl',
      align: 'right',
      render: (_, record: Position) => (
        <span style={{ color: record.unrealized_pnl >= 0 ? '#3f8600' : '#cf1322' }}>
          ${record.unrealized_pnl.toFixed(2)} ({record.unrealized_pnl_percentage.toFixed(2)}%)
        </span>
      ),
    },
    {
      title: 'Leverage',
      dataIndex: 'leverage',
      key: 'leverage',
      align: 'center',
      render: (leverage: number) => `${leverage}x`,
    },
    {
      title: 'Action',
      key: 'action',
      align: 'center',
      render: (_, record: Position) => (
        <Space size="small">
          <Popconfirm
            title="Close position?"
            description="Are you sure you want to close this position?"
            onConfirm={() => handleClose(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="primary" danger size="small" icon={<CloseOutlined />}>
              Close
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={positions}
      rowKey="id"
      loading={loading}
      pagination={false}
      size="small"
      scroll={{ x: 800 }}
    />
  );
}
