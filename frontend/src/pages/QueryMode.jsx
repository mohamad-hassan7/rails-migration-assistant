import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  Space, 
  Typography, 
  Avatar, 
  Spin,
  Tag,
  Row,
  Col,
  message
} from 'antd';
import { 
  SendOutlined, 
  UserOutlined, 
  RobotOutlined,
  DeleteOutlined,
  DownloadOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import useAppStore from '../stores/appStore';
import { askQuestion, checkApiConnection } from '../services/apiClient';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const QueryMode = () => {
  const {
    chatMessages,
    isProcessingQuery,
    addChatMessage,
    clearChatMessages,
    setIsProcessingQuery,
    setError
  } = useAppStore();

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, isProcessingQuery]);

  // Add welcome message only once per session
  const welcomeSentRef = useRef(false);
  useEffect(() => {
    if (!welcomeSentRef.current && chatMessages.length === 0) {
      addChatMessage({
        role: 'assistant',
        content: `🚄 Welcome to Rails Query Mode!

I'm your Rails assistant. Ask me anything about Ruby on Rails upgrades, best practices, or general Rails development.

💡 **Try asking:**
• "How do I upgrade from Rails 5.2 to 7.0?"
• "What are the key features in Rails 7.1?"
• "Best practices for Rails migrations?"
• "How to handle deprecated ActiveRecord methods?"

Feel free to ask any Rails-related question!`
      });
      welcomeSentRef.current = true;
    }
  }, [chatMessages.length, addChatMessage]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isProcessingQuery) {
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputValue.trim()
    };

    addChatMessage(userMessage);
    setInputValue('');
    setIsProcessingQuery(true);

    try {
      const response = await askQuestion({
        question: userMessage.content
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.answer
      };

      addChatMessage(assistantMessage);
    } catch (error) {
      console.error('Query failed:', error);
      setError(error.message);
      
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error processing your question: ${error.message}\n\nPlease try again or rephrase your question.`
      };
      
      addChatMessage(errorMessage);
      message.error('Failed to process your question. Please try again.');
    } finally {
      setIsProcessingQuery(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickQuestion = (question) => {
    setInputValue(question);
  };

  const handleTestConnection = async () => {
    try {
      console.log('🔧 Testing API connection...');
      const result = await checkApiConnection();
      console.log('🔧 Connection test result:', result);
      message.success('API connection test successful!');
    } catch (error) {
      console.error('🔧 Connection test failed:', error);
      message.error(`API connection test failed: ${error.message}`);
    }
  };

  const handleExportChat = () => {
    if (chatMessages.length === 0) {
      message.info('No chat history to export.');
      return;
    }

    const exportContent = chatMessages
      .map(msg => `[${new Date(msg.timestamp).toLocaleTimeString()}] ${msg.role.toUpperCase()}:\n${msg.content}\n\n`)
      .join('---\n\n');

    const blob = new Blob([exportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rails_chat_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    message.success('Chat history exported successfully!');
  };

  const handleClearChat = () => {
    clearChatMessages();
    message.success('Chat history cleared.');
  };

  const quickQuestions = [
    "Rails 7 features",
    "Upgrade from Rails 6 to 7",
    "Performance optimization",
    "Security best practices",
    "Migration strategies"
  ];

  const formatMessage = (content) => {
    // Improved markdown and HTML formatting for bot answers
    // Handle code blocks (``` ... ```)
    const codeBlockRegex = /```([\s\S]*?)```/g;
    let blocks = [];
    let lastIndex = 0;
    let match;
    let idx = 0;
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        blocks.push({ type: 'text', value: content.slice(lastIndex, match.index) });
      }
      // Add code block
      blocks.push({ type: 'code', value: match[1] });
      lastIndex = codeBlockRegex.lastIndex;
    }
    // Add remaining text after last code block
    if (lastIndex < content.length) {
      blocks.push({ type: 'text', value: content.slice(lastIndex) });
    }

    // Render blocks
    return blocks.map((block, blockIdx) => {
      if (block.type === 'code') {
        return (
          <Paragraph key={`code-${blockIdx}`}>
            <pre style={{ background: '#f6f8fa', padding: '8px', borderRadius: '6px', overflowX: 'auto' }}>
              <code>{block.value.trim()}</code>
            </pre>
          </Paragraph>
        );
      }
      // For text blocks, split by line and format
      return block.value.split('\n').map((line, index) => {
        // Bold (**text**)
        let formattedLine = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Percent sign (%) - just display as is
        // Links
        formattedLine = formattedLine.replace(
          /(https?:\/\/[^\s]+)/g,
          '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #1890ff;">$1</a>'
        );
        // Inline code (`code`)
        formattedLine = formattedLine.replace(/`([^`]+)`/g, '<code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px;">$1</code>');
        // Emoji headers
        if (line.startsWith('🚀') || line.startsWith('✨') || line.startsWith('🔹') || line.startsWith('⚡') || line.startsWith('🔒')) {
          return <Text key={index} strong style={{ display: 'block', marginBottom: '12px', color: '#1890ff', fontSize: '16px' }}>{line}</Text>;
        }
        // Markdown headers
        if (line.match(/^##\s+(.+)/)) {
          const headerText = line.replace(/^##\s+/, '');
          return <Title key={index} level={4} style={{ margin: '16px 0 8px 0', color: '#1890ff' }}>{headerText}</Title>;
        }
        if (line.match(/^###\s+(.+)/)) {
          const headerText = line.replace(/^###\s+/, '');
          return <Title key={index} level={5} style={{ margin: '12px 0 6px 0', color: '#1890ff' }}>{headerText}</Title>;
        }
        // Bullet points
        if (line.match(/^[•-]\s+/)) {
          return (
            <Text key={index} style={{ display: 'block', marginLeft: '16px', marginBottom: '4px' }}>
              <span dangerouslySetInnerHTML={{ __html: formattedLine }} />
            </Text>
          );
        }
        // Render formatted line
        return line ? (
          <Text key={index} style={{ display: 'block', marginBottom: '4px' }}>
            <span dangerouslySetInnerHTML={{ __html: formattedLine }} />
          </Text>
        ) : <br key={index} />;
      });
    });
  };

  return (
    <div className="fade-in" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <RobotOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              <div>
                <Title level={4} style={{ margin: 0 }}>Rails Query Assistant</Title>
                <Text type="secondary">Ask me anything about Rails development</Text>
              </div>
            </Space>
          </Col>
          <Col>
            <Space>
              <Tag color="success" icon={<RobotOutlined />}>AI Active</Tag>
              <Button 
                icon={<DownloadOutlined />} 
                onClick={handleExportChat}
                disabled={chatMessages.length === 0}
              >
                Export
              </Button>
              <Button 
                icon={<DeleteOutlined />} 
                onClick={handleClearChat}
                disabled={chatMessages.length === 0}
              >
                Clear
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Chat Messages */}
      <Card 
        title="💬 Conversation"
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
      >
        <div 
          style={{ 
            flex: 1, 
            overflowY: 'auto', 
            padding: '16px',
            background: '#fafafa'
          }}
          className="chat-messages"
        >
          {chatMessages.map((message) => (
            <div key={message.id} style={{ marginBottom: '16px' }}>
              <Card 
                size="small"
                style={{
                  background: message.role === 'user' ? '#e6f7ff' : '#f6ffed',
                  border: message.role === 'user' ? '1px solid #91d5ff' : '1px solid #b7eb8f',
                  marginLeft: message.role === 'user' ? '20%' : '0',
                  marginRight: message.role === 'user' ? '0' : '20%'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                  <Avatar 
                    icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      background: message.role === 'user' ? '#1890ff' : '#52c41a'
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <Text strong style={{ color: message.role === 'user' ? '#1890ff' : '#52c41a' }}>
                        {message.role === 'user' ? 'You' : 'Rails Assistant'}
                      </Text>
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Text>
                    </div>
                    <div style={{ lineHeight: '1.6' }}>
                      {typeof message.content === 'string' ? 
                        formatMessage(message.content) : 
                        message.content
                      }
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          ))}
          
          {isProcessingQuery && (
            <div style={{ marginBottom: '16px' }}>
              <Card 
                size="small"
                style={{
                  background: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  marginRight: '20%'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Avatar icon={<RobotOutlined />} style={{ background: '#52c41a' }} />
                  <div>
                    <Text strong style={{ color: '#52c41a' }}>Rails Assistant</Text>
                    <div style={{ marginTop: '8px' }}>
                      <Spin size="small" style={{ marginRight: '8px' }} />
                      <Text type="secondary">🤖 AI is analyzing your question and generating a comprehensive response... (this may take 30-90 seconds)</Text>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '16px', background: 'white', borderTop: '1px solid #e8e8e8' }}>
          {/* Quick Questions */}
          <div style={{ marginBottom: '12px' }}>
            <Text strong style={{ marginRight: '12px' }}>💡 Quick questions:</Text>
            <Space wrap>
              {quickQuestions.map((question, index) => (
                <Button 
                  key={index}
                  size="small" 
                  type="dashed"
                  icon={<QuestionCircleOutlined />}
                  onClick={() => handleQuickQuestion(question)}
                  disabled={isProcessingQuery}
                >
                  {question}
                </Button>
              ))}
              <Button 
                size="small" 
                type="primary"
                ghost
                onClick={handleTestConnection}
                disabled={isProcessingQuery}
              >
                🔧 Test API
              </Button>
            </Space>
          </div>

          {/* Message Input */}
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask your Rails question here... (Ctrl+Enter to send)"
              autoSize={{ minRows: 2, maxRows: 4 }}
              disabled={isProcessingQuery}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              loading={isProcessingQuery}
              disabled={!inputValue.trim()}
              style={{ height: 'auto' }}
            >
              Send
            </Button>
          </Space.Compact>
          
          <Text type="secondary" style={{ fontSize: '11px', display: 'block', marginTop: '4px' }}>
            Press Ctrl+Enter to send quickly
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default QueryMode;
