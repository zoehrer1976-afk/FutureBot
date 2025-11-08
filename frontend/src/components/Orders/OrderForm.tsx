/**
 * Order Form Component
 * Form for creating new trading orders
 */

import { useState } from 'react';
import { Form, Input, Select, Button, InputNumber, message, Card, Row, Col, Space } from 'antd';
import type { OrderSide, OrderType } from '../../types';
import { createOrder } from '../../services';

const { Option } = Select;

interface OrderFormValues {
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stop_price?: number;
}

export default function OrderForm() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [orderType, setOrderType] = useState<OrderType>('market');

  const handleSubmit = async (values: OrderFormValues) => {
    setLoading(true);
    try {
      const order = await createOrder({
        symbol: values.symbol.toUpperCase(),
        side: values.side,
        type: values.type,
        quantity: values.quantity,
        price: values.price,
        stop_price: values.stop_price,
      });

      message.success(`Order placed successfully! Order ID: ${order.id}`);
      form.resetFields();
    } catch (error: any) {
      message.error(`Failed to place order: ${error.detail || 'Unknown error'}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderTypeChange = (value: OrderType) => {
    setOrderType(value);
    if (value === 'market') {
      form.setFieldsValue({ price: undefined, stop_price: undefined });
    }
  };

  return (
    <Card title="Place Order" style={{ maxWidth: 600, margin: '0 auto' }}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          symbol: 'BTCUSDT',
          side: 'buy',
          type: 'market',
          quantity: 0.001,
        }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="Symbol"
              name="symbol"
              rules={[{ required: true, message: 'Please select a symbol' }]}
            >
              <Select size="large">
                <Option value="BTCUSDT">BTC/USDT</Option>
                <Option value="ETHUSDT">ETH/USDT</Option>
                <Option value="SOLUSDT">SOL/USDT</Option>
                <Option value="BNBUSDT">BNB/USDT</Option>
                <Option value="ADAUSDT">ADA/USDT</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item
              label="Side"
              name="side"
              rules={[{ required: true, message: 'Please select a side' }]}
            >
              <Select size="large">
                <Option value="buy">
                  <span style={{ color: '#3f8600' }}>BUY</span>
                </Option>
                <Option value="sell">
                  <span style={{ color: '#cf1322' }}>SELL</span>
                </Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="Order Type"
              name="type"
              rules={[{ required: true, message: 'Please select order type' }]}
            >
              <Select size="large" onChange={handleOrderTypeChange}>
                <Option value="market">Market</Option>
                <Option value="limit">Limit</Option>
                <Option value="stop">Stop</Option>
                <Option value="stop_limit">Stop Limit</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item
              label="Quantity"
              name="quantity"
              rules={[
                { required: true, message: 'Please enter quantity' },
                { type: 'number', min: 0.001, message: 'Minimum quantity is 0.001' },
              ]}
            >
              <InputNumber
                size="large"
                style={{ width: '100%' }}
                step={0.001}
                precision={3}
                min={0.001}
              />
            </Form.Item>
          </Col>
        </Row>

        {(orderType === 'limit' || orderType === 'stop_limit') && (
          <Form.Item
            label="Limit Price"
            name="price"
            rules={[
              { required: true, message: 'Please enter limit price' },
              { type: 'number', min: 0.01, message: 'Price must be greater than 0' },
            ]}
          >
            <InputNumber
              size="large"
              style={{ width: '100%' }}
              step={0.01}
              precision={2}
              min={0.01}
              prefix="$"
            />
          </Form.Item>
        )}

        {(orderType === 'stop' || orderType === 'stop_limit') && (
          <Form.Item
            label="Stop Price"
            name="stop_price"
            rules={[
              { required: true, message: 'Please enter stop price' },
              { type: 'number', min: 0.01, message: 'Price must be greater than 0' },
            ]}
          >
            <InputNumber
              size="large"
              style={{ width: '100%' }}
              step={0.01}
              precision={2}
              min={0.01}
              prefix="$"
            />
          </Form.Item>
        )}

        <Form.Item>
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button onClick={() => form.resetFields()}>Reset</Button>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              Place Order
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
}
