import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import AppHeader from './components/AppHeader';
import WelcomePage from './pages/WelcomePage';
import ProjectMode from './pages/ProjectMode';
import QueryMode from './pages/QueryMode';
import useAppStore from './stores/appStore';

const { Content } = Layout;

function App() {
  const { currentPage } = useAppStore();

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'project':
        return <ProjectMode />;
      case 'query':
        return <QueryMode />;
      default:
        return <WelcomePage />;
    }
  };

  return (
    <Layout className="app-layout">
      <AppHeader />
      <Content>
        <div className="page-container">
          {renderCurrentPage()}
        </div>
      </Content>
    </Layout>
  );
}

export default App;
