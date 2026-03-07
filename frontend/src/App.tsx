import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';

const ChatPage = lazy(() => import('./pages/ChatPage'));
const ReportPage = lazy(() => import('./pages/ReportPage'));
const NotFound = lazy(() => import('./pages/NotFound'));

const Loading: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <Spin size="large" />
  </div>
);

const App: React.FC = () => {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#5B8FB9',
          borderRadius: 12,
          colorBgContainer: '#fafafa',
        },
      }}
    >
      <BrowserRouter>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
