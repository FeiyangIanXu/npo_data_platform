import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Typography, 
  Input, 
  Space, 
  Tag,
  Descriptions,
  Divider
} from 'antd';
import { 
  BookOutlined, 
  SearchOutlined 
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;

const API_BASE_URL = 'http://localhost:8001/api';

const VariableDescriptions = () => {
  const [fields, setFields] = useState([]);
  const [filteredFields, setFilteredFields] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFields();
  }, []);

  const fetchFields = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/fields`);
      const fieldsData = response.data.fields;
      setFields(fieldsData);
      setFilteredFields(fieldsData);
    } catch (error) {
      console.error('Failed to fetch field information:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    if (!value) {
      setFilteredFields(fields);
      return;
    }
    
    const filtered = fields.filter(field => 
      field.name.toLowerCase().includes(value.toLowerCase())
    );
    setFilteredFields(filtered);
  };

  const getFieldCategory = (fieldName) => {
    if (fieldName.includes('revenue')) return 'Revenue';
    if (fieldName.includes('asset')) return 'Assets';
    if (fieldName.includes('expense')) return 'Expenses';
    if (fieldName.includes('employee') || fieldName.includes('employed')) return 'Employees';
    if (fieldName.includes('compensation')) return 'Compensation';
    if (fieldName.includes('grant')) return 'Grants';
    if (fieldName.includes('program')) return 'Programs';
    if (fieldName.includes('cy')) return 'Current Year';
    if (fieldName.includes('py')) return 'Previous Year';
    return 'Other';
  };

  const getFieldDescription = (fieldName) => {
    const descriptions = {
      'organization_name': 'Organization Name',
      'ein': 'Employer Identification Number',
      'state': 'State',
      'city': 'City',
      'total_revenue_cy': 'Current Year Total Revenue',
      'total_revenue_py': 'Previous Year Total Revenue',
      'total_assets_cy': 'Current Year Total Assets',
      'total_assets_py': 'Previous Year Total Assets',
      'total_expenses_cy': 'Current Year Total Expenses',
      'total_expenses_py': 'Previous Year Total Expenses',
      'number_of_individuals_employed_cy': 'Current Year Number of Employees',
      'number_of_individuals_employed_py': 'Previous Year Number of Employees',
      'contributions_and_grants_cy': 'Current Year Contributions and Grants',
      'contributions_and_grants_py': 'Previous Year Contributions and Grants',
      'program_revenue_cy': 'Current Year Program Revenue',
      'program_revenue_py': 'Previous Year Program Revenue',
      'investment_income_cy': 'Current Year Investment Income',
      'investment_income_py': 'Previous Year Investment Income',
      'other_revenue_cy': 'Current Year Other Revenue',
      'other_revenue_py': 'Previous Year Other Revenue',
      'grants_paid_cy': 'Current Year Grants Paid',
      'grants_paid_py': 'Previous Year Grants Paid',
      'salaries_other_comp_cy': 'Current Year Salaries and Other Compensation',
      'salaries_other_comp_py': 'Previous Year Salaries and Other Compensation',
      'total_fundraising_expenses_cy': 'Current Year Total Fundraising Expenses',
      'total_fundraising_expenses_py': 'Previous Year Total Fundraising Expenses',
      'other_expenses_cy': 'Current Year Other Expenses',
      'other_expenses_py': 'Previous Year Other Expenses',
      'revenue_less_expenses_cy': 'Current Year Revenue Less Expenses',
      'revenue_less_expenses_py': 'Previous Year Revenue Less Expenses',
      'total_liabilities_cy': 'Current Year Total Liabilities',
      'total_liabilities_py': 'Previous Year Total Liabilities',
      'net_assets_or_fund_balances_cy': 'Current Year Net Assets or Fund Balances',
      'net_assets_or_fund_balances_py': 'Previous Year Net Assets or Fund Balances',
    };

    return descriptions[fieldName] || 'No description available';
  };

  const columns = [
    {
      title: 'Field Name',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      render: (text) => (
        <Text code>{text}</Text>
      ),
    },
    {
      title: 'Data Type',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (text) => (
        <Tag color="blue">{text}</Tag>
      ),
    },
    {
      title: 'Category',
      key: 'category',
      width: 120,
      render: (_, record) => (
        <Tag color="green">{getFieldCategory(record.name)}</Tag>
      ),
    },
    {
      title: 'Description',
      key: 'description',
      render: (_, record) => (
        <Text>{getFieldDescription(record.name)}</Text>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>
        <BookOutlined /> Variable Descriptions
      </Title>
      <Text type="secondary">
        Understand the meaning and purpose of each field in the IRS Form 990 dataset
      </Text>

      <Divider />

      {/* 搜索框 */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>Search Fields</Text>
          <Search
            placeholder="Enter field name keywords"
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={handleSearch}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </Space>
      </Card>

      {/* 字段统计 */}
      <Card style={{ marginBottom: 24 }}>
        <Descriptions title="Dataset Information" bordered>
          <Descriptions.Item label="Total Fields">{fields.length}</Descriptions.Item>
          <Descriptions.Item label="Currently Displayed">{filteredFields.length}</Descriptions.Item>
          <Descriptions.Item label="Data Source">IRS Form 990</Descriptions.Item>
          <Descriptions.Item label="Data Year">2023</Descriptions.Item>
          <Descriptions.Item label="Data Format">CSV/Excel</Descriptions.Item>
          <Descriptions.Item label="Last Updated">2024</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 字段列表 */}
      <Card title="Field Details">
        <Table
          columns={columns}
          dataSource={filteredFields}
          rowKey="name"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} of ${total} items`,
          }}
          scroll={{ x: 800 }}
          size="middle"
        />
      </Card>

      {/* 使用说明 */}
      <Card title="Usage Instructions" style={{ marginTop: 24 }}>
        <Paragraph>
          <Text strong>Field Naming Rules:</Text>
        </Paragraph>
        <ul>
          <li><Text code>_cy</Text> suffix indicates Current Year data</li>
          <li><Text code>_py</Text> suffix indicates Previous Year data</li>
          <li>Field names use underscore-separated English naming</li>
          <li>All monetary fields are in US dollars</li>
        </ul>
        
        <Paragraph>
          <Text strong>Data Source:</Text>
        </Paragraph>
        <ul>
          <li>Data sourced from publicly available IRS Form 990 filings</li>
          <li>Contains financial and operational information of nonprofit organizations</li>
          <li>Data has been cleaned and standardized</li>
        </ul>
      </Card>
    </div>
  );
};

export default VariableDescriptions; 