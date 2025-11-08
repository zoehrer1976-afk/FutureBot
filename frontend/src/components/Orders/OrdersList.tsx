/**
 * Orders List Component
 * Display active trading orders
 */

import { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, message, Popconfirm } from 'antd';
import { CloseOutlined } from '@ant-design/icons';
import type { Order } from '../../types';
import { getOrders, cancelOrder } from '../../services';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

export default function OrdersList() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
    const interval = setInterval(loadOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      const data = await getOrders({ status: 'open,pending' });
      setOrders(data.orders);
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      await cancelOrder(id);
      message.success('Order cancelled successfully');
      loadOrders();
    } catch (error) {
      message.error('Failed to cancel order');
      console.error(error);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'blue',
      open: 'green',
      filled: 'success',
      partially_filled: 'orange',
      cancelled: 'default',
      expired: 'error',
    };
    return colors[status] || 'default';
  };

  const columns: ColumnsType<Order> = [
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
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => type.toUpperCase(),
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      align: 'right',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      align: 'right',
      render: (price: number | null) => price ? `$${price.toFixed(2)}` : 'Market',
    },
    {
      title: 'Filled',
      key: 'filled',
      align: 'right',
      render: (_, record: Order) => `${record.filled_quantity}/${record.quantity}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase().replace('_', ' ')}
        </Tag>
      ),
    },
    {
      title: 'Time',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => dayjs(time).format('HH:mm:ss'),
    },
    {
      title: 'Action',
      key: 'action',
      align: 'center',
      render: (_, record: Order) => (
        <Space size="small">
          {(record.status === 'open' || record.status === 'pending') && (
            <Popconfirm
              title="Cancel order?"
              description="Are you sure you want to cancel this order?"
              onConfirm={() => handleCancel(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button type="primary" danger size="small" icon={<CloseOutlined />}>
                Cancel
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={orders}
      rowKey="id"
      loading={loading}
      pagination={false}
      size="small"
      scroll={{ x: 900 }}
    />
  );
}
