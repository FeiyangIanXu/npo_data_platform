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

const API_BASE_URL = 'http://localhost:8001/api';

const DataPreview = () => {
  const [data, setData] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPreviewData();
    fetchStatistics();
  }, []);

  const fetchPreviewData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/query?limit=50`);
      setData(response.data.data);
    } catch (error) {
      console.error('Failed to fetch preview data:', error);
      message.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const columns = [
    {
      title: 'Organization Name',
      dataIndex: 'campus',
      key: 'campus',
      width: 250,
      ellipsis: true,
    },
    {
      title: 'EIN',
      dataIndex: 'form_990_top_block_box_d_ein_cy',
      key: 'ein',
      width: 120,
    },
    {
      title: 'State',
      dataIndex: 'st',
      key: 'st',
      width: 80,
    },
    {
      title: 'City',
      dataIndex: 'city',
      key: 'city',
      width: 120,
    },
    {
      title: 'Total Revenue',
      dataIndex: 'part_i_summary_12_total_revenue_cy',
      key: 'total_revenue',
      width: 150,
      render: (text) => {
        if (!text) return '-';
        const value = text.replace(/[$,]/g, '');
        const num = parseFloat(value);
        if (isNaN(num)) return text;
        return `$${(num / 1000000).toFixed(1)}M`;
      },
    },
    {
      title: 'Total Assets',
      dataIndex: 'part_i_summary_22_total_assets_cy',
      key: 'total_assets',
      width: 150,
      render: (text) => {
        if (!text) return '-';
        const value = text.replace(/[$,]/g, '');
        const num = parseFloat(value);
        if (isNaN(num)) return text;
        return `$${(num / 1000000).toFixed(1)}M`;
      },
    },
    {
      title: 'Employees',
      dataIndex: 'part_i_summary_5_number_of_individuals_employed_cy',
      key: 'employees',
      width: 100,
      render: (text) => text || '-',
    },
  ];

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      if (searchForm.organization_name) {
        params.append('organization_name', searchForm.organization_name);
      }
      if (searchForm.ein) {
        params.append('ein', searchForm.ein);
      }
      if (searchForm.state) {
        params.append('st', searchForm.state);
      }
      if (searchForm.city) {
        params.append('city', searchForm.city);
      }
      
      params.append('page', currentPage.toString());
      params.append('pageSize', pageSize.toString());
      
      const response = await axios.get(`${API_BASE_URL}/api/query?${params}`);
      setData(response.data.data);
      setTotal(response.data.total);
      setCurrentPage(response.data.page);
    } catch (error) {
      console.error('Query failed:', error);
      message.error('Query failed, please try again');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={2}>
        <EyeOutlined /> Data Preview
      </Title>
      <Text type="secondary">
        Preview IRS nonprofit Form 990 dataset to understand data structure and content
      </Text>

      {/* 统计信息 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Organizations"
                value={statistics.total_organizations}
                prefix={<BarChartOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="States Covered"
                value={statistics.state_distribution?.length || 0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Data Fields"
                value={statistics.fields?.count || 0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Data Year"
                value="2023"
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 州分布 */}
      {statistics?.state_distribution && (
        <Card title="State Distribution" style={{ marginBottom: 24 }}>
          <Row gutter={[8, 8]}>
            {statistics.state_distribution.map((item, index) => (
              <Col key={index}>
                <Tag color="blue">
                  {item.state}: {item.count}
                </Tag>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 数据表格 */}
      <Card 
        title={
          <Space>
            <span>Data Preview</span>
            <Tag color="green">First 50 Records</Tag>
          </Space>
        }
        extra={
          <Button icon={<DownloadOutlined />}>
            Export Full Data
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey={(record, index) => index}
          loading={loading}
          pagination={false}
          scroll={{ x: 1000 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default DataPreview; 