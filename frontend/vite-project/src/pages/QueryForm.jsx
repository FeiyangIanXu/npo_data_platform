import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Table, 
  Card, 
  Row, 
  Col, 
  Select, 
  Space, 
  Typography, 
  Divider,
  message,
  Spin,
  Tag,
  Tooltip,
  Statistic
} from 'antd';
import { 
  SearchOutlined, 
  DownloadOutlined, 
  ReloadOutlined,
  InfoCircleOutlined,
  TeamOutlined,
  GlobalOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

const API_BASE_URL = 'http://localhost:8000/api';

const QueryForm = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [fields, setFields] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 获取可用字段
  useEffect(() => {
    fetchFields();
    fetchStatistics();
  }, []);

  const fetchFields = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/fields`);
      setFields(response.data.fields);
    } catch (error) {
      console.error('获取字段失败:', error);
      message.error('获取字段信息失败');
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

  const handleSearch = async (values) => {
    setLoading(true);
    try {
      const params = {
        ...values,
        page: pagination.current,
        pageSize: pagination.pageSize,
      };

      // 移除空值
      Object.keys(params).forEach(key => {
        if (!params[key]) delete params[key];
      });

      // 字段名映射
      if (params.organization_name) {
        params.organization_name = params.organization_name; // 保持原参数名，后端会映射到campus
      }
      if (params.ein) {
        params.ein = params.ein; // 保持原参数名，后端会映射到form_990_top_block_box_d_ein_cy
      }
      if (params.st) {
        params.st = params.st; // 保持原参数名
      }
      if (params.city) {
        params.city = params.city; // 保持原参数名
      }

      const response = await axios.get(`${API_BASE_URL}/query`, { params });
      setData(response.data.data);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
      }));
      
      message.success(`查询成功，共找到 ${response.data.total} 条记录`);
    } catch (error) {
      console.error('查询失败:', error);
      message.error('查询失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (paginationInfo) => {
    setPagination(paginationInfo);
    form.submit();
  };

  const handleReset = () => {
    form.resetFields();
    setData([]);
    setPagination({
      current: 1,
      pageSize: 20,
      total: 0,
    });
  };

  const handleExport = async (format = 'csv') => {
    try {
      const values = form.getFieldsValue();
      const params = {
        ...values,
        format: format
      };

      // 移除空值
      Object.keys(params).forEach(key => {
        if (!params[key]) delete params[key];
      });

      const response = await axios.get(`${API_BASE_URL}/export`, { 
        params,
        responseType: 'blob'
      });

      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `nonprofits_data.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      message.success(`${format.toUpperCase()}文件导出成功`);
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请重试');
    }
  };

  // 表格列配置
  const columns = [
    {
      title: '组织名称',
      dataIndex: 'campus',
      key: 'campus',
      width: 200,
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
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
      title: '总收入 (CY)',
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
      title: '员工数量',
      dataIndex: 'part_i_summary_5_number_of_individuals_employed_cy',
      key: 'employees',
      width: 100,
      render: (text) => text || '-',
    },
  ];

  return (
    <div>
      <Title level={2}>
        <SearchOutlined /> 数据查询
      </Title>
      <Text type="secondary">
        查询IRS非营利组织Form 990数据，支持按组织名称、EIN、地理位置等条件筛选
      </Text>
      
      <Divider />

      {/* 统计信息卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="总记录数"
                value={statistics.total_records}
                prefix={<TeamOutlined />}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="覆盖州数"
                value={statistics.top_states?.length || 0}
                prefix={<GlobalOutlined />}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="数据年份"
                value="2023"
                prefix={<CalendarOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 查询表单 */}
      <Card title="查询条件" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSearch}
          initialValues={{
            limit: 20,
          }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="组织名称" name="organization_name">
                <Input 
                  placeholder="输入组织名称关键词"
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="EIN号码" name="ein">
                <Input 
                  placeholder="输入EIN号码"
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="州" name="st">
                <Select
                  placeholder="选择州"
                  allowClear
                  showSearch
                  optionFilterProp="children"
                >
                  <Option value="CA">California</Option>
                  <Option value="NY">New York</Option>
                  <Option value="TX">Texas</Option>
                  <Option value="FL">Florida</Option>
                  <Option value="PA">Pennsylvania</Option>
                  {/* 可以动态加载更多州 */}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="城市" name="city">
                <Input 
                  placeholder="输入城市名称"
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="查询字段" name="field">
                <Select
                  placeholder="选择特定字段（可选）"
                  allowClear
                  showSearch
                  optionFilterProp="children"
                >
                  {fields.map(field => (
                    <Option key={field.name} value={field.name}>
                      {field.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="结果数量" name="limit">
                <Select>
                  <Option value={10}>10条</Option>
                  <Option value={20}>20条</Option>
                  <Option value={50}>50条</Option>
                  <Option value={100}>100条</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                icon={<SearchOutlined />}
                loading={loading}
              >
                查询
              </Button>
              <Button 
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
              <Button 
                icon={<DownloadOutlined />}
                onClick={() => handleExport('csv')}
              >
                导出CSV
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* 查询结果 */}
      <Card 
        title={
          <Space>
            <span>查询结果</span>
            {data.length > 0 && (
              <Tag color="blue">{data.length} 条记录</Tag>
            )}
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey={(record, index) => index}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          onChange={handleTableChange}
          loading={loading}
          scroll={{ x: 1000 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default QueryForm; 