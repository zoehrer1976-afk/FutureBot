/**
 * Dashboard Component
 * Main trading dashboard layout
 */

import { useEffect, useState } from 'react';
import { Layout, Row, Col, Card, Statistic, message } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import type { PortfolioSummary } from '../../types';
import { getPortfolioSummary } from '../../services';
import PositionsList from '../Positions/PositionsList';
import OrdersList from '../Orders/OrdersList';
import TradingChart from '../TradingChart/TradingChart';

const { Header, Content } = Layout;

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPortfolioData();
    // Refresh every 10 seconds
    const interval = setInterval(loadPortfolioData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadPortfolioData = async () => {
    try {
      const data = await getPortfolioSummary();
      setPortfolio(data);
    } catch (error) {
      message.error('Failed to load portfolio data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <h1 style={{ color: 'white', margin: '16px 0' }}>FutureBot Trading Dashboard</h1>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        {/* Portfolio Summary */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Balance"
                value={portfolio?.total_balance || 0}
                precision={2}
                prefix="$"
                loading={loading}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Available Balance"
                value={portfolio?.available_balance || 0}
                precision={2}
                prefix="$"
                loading={loading}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Unrealized P&L"
                value={portfolio?.unrealized_pnl || 0}
                precision={2}
                prefix="$"
                valueStyle={{
                  color: (portfolio?.unrealized_pnl || 0) >= 0 ? '#3f8600' : '#cf1322',
                }}
                prefix={(portfolio?.unrealized_pnl || 0) >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                loading={loading}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total P&L %"
                value={portfolio?.pnl_percentage || 0}
                precision={2}
                suffix="%"
                valueStyle={{
                  color: (portfolio?.pnl_percentage || 0) >= 0 ? '#3f8600' : '#cf1322',
                }}
                loading={loading}
              />
            </Card>
          </Col>
        </Row>

        {/* Trading Chart */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Card title="Chart" bodyStyle={{ padding: '12px' }}>
              <TradingChart symbol="BTCUSDT" />
            </Card>
          </Col>
        </Row>

        {/* Positions and Orders */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="Open Positions" bodyStyle={{ padding: 0 }}>
              <PositionsList />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Active Orders" bodyStyle={{ padding: 0 }}>
              <OrdersList />
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}
