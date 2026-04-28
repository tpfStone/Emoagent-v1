import React, { useState } from 'react';
import { Layout, Typography, Button } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import ChatWindow from '../components/chat/ChatWindow';
import RatingModal from '../components/rating/RatingModal';
import { useSessionStore } from '../stores/sessionStore';
import t from '../locales';

const { Header, Content } = Layout;
const { Title } = Typography;

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSessionStore();
  const [beforeRatingDismissed, setBeforeRatingDismissed] = useState(false);
  const showBeforeRating = isAuthenticated && !beforeRatingDismissed;

  return (
    <Layout style={{ height: '100vh' }}>
      <Header
        style={{
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
        }}
      >
        <Title level={4} style={{ margin: 0, color: '#5B8FB9' }}>
          {t.chat.title}
        </Title>
        <Button
          type="text"
          icon={<BarChartOutlined />}
          onClick={() => navigate('/report')}
        >
          {t.report.button}
        </Button>
      </Header>
      <Content style={{ background: '#fff' }}>
        <ChatWindow />
      </Content>

      <RatingModal
        type="before"
        open={showBeforeRating}
        onClose={() => setBeforeRatingDismissed(true)}
      />
    </Layout>
  );
};

export default ChatPage;
