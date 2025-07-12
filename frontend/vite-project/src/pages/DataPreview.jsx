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
      console.error('获取预览数据失败:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error('获取统计信息失败:', error);
    }
  };

  const columns = [
    {
      title: '组织名称',
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
      title: '州',
      dataIndex: 'st',
      key: 'st',
      width: 80,
    },
    {
      title: '城市',
      dataIndex: 'city',
      key: 'city',
      width: 120,
    },
    {
      title: '总收入',
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
      title: '总资产',
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
      title: '员工数',
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
      console.error('查询失败:', error);
      message.error('查询失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={2}>
        <EyeOutlined /> 数据预览
      </Title>
      <Text type="secondary">
        预览IRS非营利组织Form 990数据集，了解数据结构和内容
      </Text>

      {/* 统计信息 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总组织数"
                value={statistics.total_organizations}
                prefix={<BarChartOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="覆盖州数"
                value={statistics.state_distribution?.length || 0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="数据字段数"
                value={statistics.fields?.count || 0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="数据年份"
                value="2023"
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 州分布 */}
      {statistics?.state_distribution && (
        <Card title="州分布" style={{ marginBottom: 24 }}>
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
            <span>数据预览</span>
            <Tag color="green">前50条记录</Tag>
          </Space>
        }
        extra={
          <Button icon={<DownloadOutlined />}>
            导出完整数据
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