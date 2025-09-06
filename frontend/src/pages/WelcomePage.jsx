import React from 'react';
import { Card, Typography, Row, Col, Button, Space } from 'antd';
import { 
  ToolOutlined, 
  MessageOutlined, 
  RocketOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  AimOutlined,
  SaveOutlined
} from '@ant-design/icons';
import useAppStore from '../stores/appStore';

const { Title, Paragraph, Text } = Typography;

const WelcomePage = () => {
  const { navigateToProject, navigateToQuery } = useAppStore();

  const features = [
    {
      icon: <RocketOutlined style={{ color: '#52c41a' }} />,
      title: 'AI-Powered Analysis',
      description: 'Local LLM with deep Rails knowledge'
    },
    {
      icon: <ThunderboltOutlined style={{ color: '#faad14' }} />,
      title: 'Fast Pattern Detection',
      description: 'Instant recognition of common issues'
    },
    {
      icon: <SafetyOutlined style={{ color: '#1890ff' }} />,
      title: '100% Private',
      description: 'Your code never leaves your machine'
    }
  ];

  return (
    <div className="welcome-container fade-in">
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{ fontSize: '72px', marginBottom: '24px' }}>🚄</div>
        <Title level={1} style={{ color: 'white', marginBottom: '16px', fontSize: '48px' }}>
          Rails Migration Assistant
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: '20px', marginBottom: '8px' }}>
          Professional Ruby on Rails Upgrade Tool
        </Paragraph>
        <Text style={{ 
          background: 'rgba(255,255,255,0.2)', 
          padding: '4px 12px', 
          borderRadius: '16px',
          color: 'white',
          fontSize: '14px',
          fontWeight: 'bold'
        }}>
          v2.0 - Modern Edition
        </Text>
      </div>

      {/* Features Grid */}
      <div style={{ marginBottom: '40px', maxWidth: '800px', margin: '0 auto 40px auto' }}>
        <Title level={3} style={{ color: 'white', textAlign: 'center', marginBottom: '24px' }}>
          ✨ Key Features
        </Title>
        <Row gutter={[24, 16]}>
          {features.map((feature, index) => (
            <Col xs={24} sm={8} key={index}>
              <Card 
                style={{ 
                  background: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '12px',
                  textAlign: 'center',
                  height: '120px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
                bodyStyle={{ padding: '16px' }}
              >
                <div style={{ fontSize: '28px', marginBottom: '8px' }}>
                  {feature.icon}
                </div>
                <Title level={5} style={{ margin: '0 0 6px 0', color: '#333', fontSize: '14px' }}>
                  {feature.title}
                </Title>
                <Text style={{ color: '#666', fontSize: '12px' }}>
                  {feature.description}
                </Text>
              </Card>
            </Col>
          ))}
        </Row>
      </div>

      {/* Mode Selection */}
      <div style={{ textAlign: 'center' }}>
        <Title level={2} style={{ color: 'white', marginBottom: '32px' }}>
          Choose Your Mode
        </Title>
        
        <Space size="large" wrap>
          <Card 
            className="mode-card"
            hoverable
            onClick={navigateToProject}
            style={{ 
              background: 'rgba(255,255,255,0.95)',
              border: 'none',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              width: '220px'
            }}
            bodyStyle={{ 
              padding: '32px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <ToolOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
            <Title level={3} style={{ margin: '0 0 10px 0', color: '#333' }}>
              Project Mode
            </Title>
            <Paragraph style={{ color: '#666', textAlign: 'center', margin: 0, fontSize: '14px' }}>
              Analyze and upgrade<br />your Rails projects
            </Paragraph>
          </Card>

          <Card 
            className="mode-card"
            hoverable
            onClick={navigateToQuery}
            style={{ 
              background: 'rgba(255,255,255,0.95)',
              border: 'none',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              width: '220px'
            }}
            bodyStyle={{ 
              padding: '32px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <MessageOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={3} style={{ margin: '0 0 10px 0', color: '#333' }}>
              Query Mode
            </Title>
            <Paragraph style={{ color: '#666', textAlign: 'center', margin: 0, fontSize: '14px' }}>
              Ask questions about<br />Rails upgrades
            </Paragraph>
          </Card>
        </Space>
      </div>

      {/* Footer */}
      <div style={{ 
        position: 'absolute', 
        bottom: '24px', 
        left: '50%', 
        transform: 'translateX(-50%)',
        textAlign: 'center'
      }}>
        <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}>
          © 2024 Rails Migration Assistant Team • Built with Electron & React
        </Text>
      </div>
    </div>
  );
};

export default WelcomePage;
