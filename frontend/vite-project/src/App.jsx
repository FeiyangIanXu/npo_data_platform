import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { 
  SearchOutlined, 
  BarChartOutlined, 
  BookOutlined, 
  QuestionCircleOutlined,
  EyeOutlined 
} from '@ant-design/icons';
import './App.css';

// 导入页面组件
import QueryForm from './pages/QueryForm';
import DataPreview from './pages/DataPreview';
import VariableDescriptions from './pages/VariableDescriptions';
import ManualsPage from './pages/ManualsPage';
import KnowledgeBase from './pages/KnowledgeBase';

const { Header, Content, Sider } = Layout;

function App() {
  const menuItems = [
    {
      key: '/',
      icon: <SearchOutlined />,
      label: '数据查询',
    },
    {
      key: '/data-preview',
      icon: <EyeOutlined />,
      label: '数据预览',
    },
    {
      key: '/variable-descriptions',
      icon: <BookOutlined />,
      label: '变量描述',
    },
    {
      key: '/manuals',
      icon: <BookOutlined />,
      label: '使用手册',
    },
    {
      key: '/knowledge-base',
      icon: <QuestionCircleOutlined />,
      label: '知识库',
    },
  ];

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ 
          background: '#001529', 
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center'
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
            IRS非营利组织数据平台
          </div>
        </Header>
        
        <Layout>
          <Sider width={250} style={{ background: '#fff' }}>
            <Menu
              mode="inline"
              defaultSelectedKeys={['/']}
              style={{ height: '100%', borderRight: 0 }}
              items={menuItems}
              onClick={({ key }) => {
                window.location.href = key;
              }}
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
                <Route path="/" element={<QueryForm />} />
                <Route path="/data-preview" element={<DataPreview />} />
                <Route path="/variable-descriptions" element={<VariableDescriptions />} />
                <Route path="/manuals" element={<ManualsPage />} />
                <Route path="/knowledge-base" element={<KnowledgeBase />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
