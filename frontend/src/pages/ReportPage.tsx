import React, { useEffect, useState } from 'react';
import { Layout, Typography, Card, Row, Col, Statistic, Spin, Button } from 'antd';
import {
  ArrowLeftOutlined,
  MessageOutlined,
  AlertOutlined,
  SmileOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { reportAPI } from '../api/report';
import type { WeeklyReportResponse } from '../api/types';
import { useSessionStore } from '../stores/sessionStore';
import EmotionChart from '../components/report/EmotionChart';
import t from '../locales';

const { Header, Content } = Layout;
const { Title } = Typography;

const ReportPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, token } = useSessionStore();
  const [report, setReport] = useState<WeeklyReportResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      if (!sessionId || !token) return;
      try {
        const data = await reportAPI.getWeeklyReport(sessionId, token);
        setReport(data);
      } catch (e) {
        console.error('Failed to fetch report:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [sessionId, token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip={t.report.loading} />
      </div>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header
        style={{
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          gap: 16,
        }}
      >
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} />
        <Title level={4} style={{ margin: 0 }}>
          {t.report.title}
        </Title>
      </Header>
      <Content style={{ padding: 24 }}>
        {report ? (
          <>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={6}>
                <Card>
                  <Statistic title={t.report.totalTurns} value={report.total_turns} prefix={<MessageOutlined />} />
                </Card>
              </Col>
              <Col xs={12} sm={6}>
                <Card>
                  <Statistic title={t.report.crisisTriggers} value={report.crisis_count} prefix={<AlertOutlined />} valueStyle={{ color: report.crisis_count > 0 ? '#cf1322' : '#3f8600' }} />
                </Card>
              </Col>
              <Col xs={12} sm={6}>
                <Card>
                  <Statistic title={t.report.ratingBefore} value={report.rating_before_avg} prefix={<SmileOutlined />} precision={1} suffix="/ 10" />
                </Card>
              </Col>
              <Col xs={12} sm={6}>
                <Card>
                  <Statistic title={t.report.ratingAfter} value={report.rating_after_avg} prefix={<SmileOutlined />} precision={1} suffix="/ 10" valueStyle={{ color: '#3f8600' }} />
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col xs={24} md={12}>
                <Card title={t.report.emotionDist}>
                  <EmotionChart distribution={report.emotion_distribution} />
                </Card>
              </Col>
              <Col xs={24} md={12}>
                <Card title={t.report.performance}>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Statistic title={t.report.bertLatency} value={report.bert_avg_latency_ms} suffix="ms" prefix={<ClockCircleOutlined />} />
                    </Col>
                    <Col span={12}>
                      <Statistic title={t.report.llmLatency} value={report.llm_avg_latency_ms} suffix="ms" prefix={<ClockCircleOutlined />} />
                    </Col>
                    <Col span={12}>
                      <Statistic title={t.report.missingRate} value={report.rating_missing_rate * 100} suffix="%" precision={0} />
                    </Col>
                    <Col span={12}>
                      <Statistic title={t.report.improvement} value={report.rating_after_avg - report.rating_before_avg} precision={1} valueStyle={{ color: (report.rating_after_avg - report.rating_before_avg) >= 0 ? '#3f8600' : '#cf1322' }} prefix={report.rating_after_avg >= report.rating_before_avg ? '↑' : '↓'} />
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </>
        ) : (
          <Card>
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>{t.report.noReport}</div>
          </Card>
        )}
      </Content>
    </Layout>
  );
};

export default ReportPage;
