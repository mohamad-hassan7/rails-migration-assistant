import React from 'react';
import { Layout, Button, Space, Typography } from 'antd';
import { HomeOutlined, SettingOutlined } from '@ant-design/icons';
import useAppStore from '../stores/appStore';

const { Header } = Layout;
const { Title } = Typography;

const AppHeader = () => {
  const { 
    currentPage, 
    navigateToWelcome 
  } = useAppStore();

  const getPageTitle = () => {
    switch (currentPage) {
      case 'project':
        return 'Project Analysis';
      case 'query':
        return 'Query Assistant';
      default:
        return 'Rails Migration Assistant';
    }
  };

  return (
    <Header 
      style={{ 
        background: 'white', 
        borderBottom: '1px solid #e8e8e8',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '24px' }}>🚄</span>
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            {getPageTitle()}
          </Title>
        </div>
        
        {currentPage !== 'welcome' && (
          <Button 
            type="text" 
            icon={<HomeOutlined />}
            onClick={navigateToWelcome}
            style={{ color: '#666' }}
          >
            Home
          </Button>
        )}
      </div>

      <Space>
        <Button 
          type="text" 
          icon={<SettingOutlined />}
          style={{ color: '#666' }}
        >
          Settings
        </Button>
      </Space>
    </Header>
  );
};

export default AppHeader;
