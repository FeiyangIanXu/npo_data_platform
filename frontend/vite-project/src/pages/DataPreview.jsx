import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Typography, 
  Row, 
  Col, 
  Statistic, 
  Tag,
  Space,
  Button,
  message
} from 'antd';
import { 
  EyeOutlined, 
  BarChartOutlined, 
  DownloadOutlined 
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const API_BASE_URL = '/api';

const DataPreview = () => {
  const [data, setData] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPreviewData();
  }, []);

  const fetchPreviewData = async () => {
    try {
      setLoading(true);
      // Use the search endpoint with empty query to get preview data
      const response = await axios.get(`${API_BASE_URL}/search`, { 
        params: { 
          q: '', 
          limit: 50 
        } 
      });
      
      if (response.data.success && response.data.results) {
        setData(response.data.results);
      } else {
        message.error('No data received from server');
      }
    } catch (error) {
      console.error('Failed to fetch preview data:', error);
      message.error('Failed to fetch data. Please check if the backend service is running.');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Organization Name',
      dataIndex: 'campus',
      key: 'campus',
      width: 250,
      ellipsis: true,
      render: (text) => text || '-',
    },
    {
      title: 'EIN',
      dataIndex: 'ein',
      key: 'ein',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: 'State',
      dataIndex: 'st',
      key: 'st',
      width: 80,
      render: (text) => text || '-',
    },
    {
      title: 'City',
      dataIndex: 'city',
      key: 'city',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: 'Total Revenue',
      dataIndex: 'part_i_summary_12_total_revenue_cy',
      key: 'total_revenue',
      width: 150,
      render: (text) => {
        if (!text) return '-';
        const num = parseFloat(text);
        if (isNaN(num)) return text;
        return `$${(num / 1000000).toFixed(1)}M`;
      },
    },
    {
      title: 'Employees',
      dataIndex: 'employees',
      key: 'employees',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: 'Fiscal Year',
      dataIndex: 'fiscal_year',
      key: 'fiscal_year',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: 'Fiscal Month',
      dataIndex: 'fiscal_month',
      key: 'fiscal_month',
      width: 120,
      render: (text) => text || '-',
    },
  ];

  return (
    <div>
      <Title level={2}>
        <EyeOutlined /> Data Preview
      </Title>
      <Text type="secondary">
        Preview IRS nonprofit Form 990 dataset to understand data structure and content
      </Text>

      {/* Data Table */}
      <Card 
        title={
          <Space>
            <span>Data Preview</span>
            <Tag color="green">First 50 Records</Tag>
          </Space>
        }
        extra={
          <Button 
            icon={<DownloadOutlined />}
            onClick={() => message.info('Export functionality will be available soon')}
          >
            Export Full Data
          </Button>
        }
        style={{ marginTop: 24 }}
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey={(record, index) => record.ein || index}
          loading={loading}
          pagination={{
            pageSize: 50,
            showSizeChanger: false,
            showQuickJumper: false,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`
          }}
          scroll={{ x: 1000 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default DataPreview; 