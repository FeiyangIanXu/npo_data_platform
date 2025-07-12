import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { 
  SearchOutlined, 
  BarChartOutlined, 
  BookOutlined, 
  QuestionCircleOutlined,
  EyeOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import './App.css';

// 导入页面组件
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import QueryForm from './pages/QueryForm';
import DataPreview from './pages/DataPreview';
import VariableDescriptions from './pages/VariableDescriptions';
import ManualsPage from './pages/ManualsPage';
import KnowledgeBase from './pages/KnowledgeBase';

const { Header, Content, Sider } = Layout;

// 主应用布局组件
function MainAppLayout() {
  const menuItems = [
    {
      key: '/dashboard',
      icon: <SearchOutlined />,
      label: 'Home',
    },
    {
      key: '/dashboard/query',
      icon: <SearchOutlined />,
      label: 'Data Query',
    },
    {
      key: '/dashboard/data-preview',
      icon: <EyeOutlined />,
      label: 'Data Preview',
    },
    {
      key: '/dashboard/variable-descriptions',
      icon: <BookOutlined />,
      label: 'Variable Descriptions',
    },
    {
      key: '/dashboard/manuals',
      icon: <BookOutlined />,
      label: 'User Manuals',
    },
    {
      key: '/dashboard/knowledge-base',
      icon: <QuestionCircleOutlined />,
      label: 'Knowledge Base',
    },
    {
      key: '/logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
    },
  ];

  const handleMenuClick = ({ key }) => {
    if (key === '/logout') {
      localStorage.removeItem('access_token');
      window.location.href = '/';
    } else {
      window.location.href = key;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#001529', 
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <BarChartOutlined />
          Financial Benchmarking Platform
        </div>
        <div style={{ color: 'white', fontSize: '14px' }}>
          Welcome to the Data Platform
        </div>
      </Header>
      
      <Layout>
        <Sider width={250} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            defaultSelectedKeys={['/dashboard']}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        
        <Layout style={{ padding: '24px' }}>
          <Content style={{ 
            background: '#fff', 
            padding: 24, 
            margin: 0, 
            minHeight: 280,
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <Routes>
              <Route path="/dashboard" element={<HomePage />} />
              <Route path="/dashboard/query" element={<QueryForm />} />
              <Route path="/dashboard/data-preview" element={<DataPreview />} />
              <Route path="/dashboard/variable-descriptions" element={<VariableDescriptions />} />
              <Route path="/dashboard/manuals" element={<ManualsPage />} />
              <Route path="/dashboard/knowledge-base" element={<KnowledgeBase />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        {/* 公共页面 */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* 需要认证的页面 - 包装在主应用布局中 */}
        <Route path="/dashboard/*" element={<MainAppLayout />} />
        
        {/* 重定向根路径到首页 */}
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
