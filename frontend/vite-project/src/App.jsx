import React from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet, useNavigate } from 'react-router-dom';
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

// Import page components
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

// Main application layout component
function MainAppLayout() {
  const navigate = useNavigate();
  
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
      navigate('/');
    } else {
      navigate(key);
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
            <Outlet />
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
        {/* Public pages */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected pages - wrapped in main application layout */}
        <Route path="/dashboard" element={<MainAppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="query" element={<QueryForm />} />
          <Route path="data-preview" element={<DataPreview />} />
          <Route path="variable-descriptions" element={<VariableDescriptions />} />
          <Route path="manuals" element={<ManualsPage />} />
          <Route path="knowledge-base" element={<KnowledgeBase />} />
        </Route>
        
        {/* Redirect root path to home page */}
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
