import React from 'react';
import { Alert } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import t from '../../locales';

interface CrisisAlertProps {
  message: string;
}

const CrisisAlert: React.FC<CrisisAlertProps> = ({ message }) => {
  return (
    <Alert
      message={t.crisis.title}
      description={message}
      type="error"
      showIcon
      icon={<WarningOutlined />}
      style={{ marginBottom: 16 }}
    />
  );
};

export default CrisisAlert;
