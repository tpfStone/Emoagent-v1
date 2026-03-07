import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import t from '../locales';

const NotFound: React.FC = () => {
  const navigate = useNavigate();
  return (
    <Result
      status="404"
      title="404"
      subTitle={t.notFound.subtitle}
      extra={
        <Button type="primary" onClick={() => navigate('/')}>
          {t.notFound.backHome}
        </Button>
      }
    />
  );
};

export default NotFound;
