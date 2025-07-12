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
      console.error('获取字段信息失败:', error);
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
    if (fieldName.includes('revenue')) return '收入相关';
    if (fieldName.includes('asset')) return '资产相关';
    if (fieldName.includes('expense')) return '支出相关';
    if (fieldName.includes('employee') || fieldName.includes('employed')) return '员工相关';
    if (fieldName.includes('compensation')) return '薪酬相关';
    if (fieldName.includes('grant')) return '资助相关';
    if (fieldName.includes('program')) return '项目相关';
    if (fieldName.includes('cy')) return '当年数据';
    if (fieldName.includes('py')) return '上年数据';
    return '其他';
  };

  const getFieldDescription = (fieldName) => {
    const descriptions = {
      'organization_name': '组织名称',
      'ein': '雇主识别号码 (Employer Identification Number)',
      'state': '所在州',
      'city': '所在城市',
      'total_revenue_cy': '当年总收入 (Current Year Total Revenue)',
      'total_revenue_py': '上年总收入 (Previous Year Total Revenue)',
      'total_assets_cy': '当年总资产 (Current Year Total Assets)',
      'total_assets_py': '上年总资产 (Previous Year Total Assets)',
      'total_expenses_cy': '当年总支出 (Current Year Total Expenses)',
      'total_expenses_py': '上年总支出 (Previous Year Total Expenses)',
      'number_of_individuals_employed_cy': '当年员工数量 (Current Year Number of Employees)',
      'number_of_individuals_employed_py': '上年员工数量 (Previous Year Number of Employees)',
      'contributions_and_grants_cy': '当年捐赠和资助 (Current Year Contributions and Grants)',
      'contributions_and_grants_py': '上年捐赠和资助 (Previous Year Contributions and Grants)',
      'program_revenue_cy': '当年项目收入 (Current Year Program Revenue)',
      'program_revenue_py': '上年项目收入 (Previous Year Program Revenue)',
      'investment_income_cy': '当年投资收益 (Current Year Investment Income)',
      'investment_income_py': '上年投资收益 (Previous Year Investment Income)',
      'other_revenue_cy': '当年其他收入 (Current Year Other Revenue)',
      'other_revenue_py': '上年其他收入 (Previous Year Other Revenue)',
      'grants_paid_cy': '当年支付的资助 (Current Year Grants Paid)',
      'grants_paid_py': '上年支付的资助 (Previous Year Grants Paid)',
      'salaries_other_comp_cy': '当年薪资和其他补偿 (Current Year Salaries and Other Compensation)',
      'salaries_other_comp_py': '上年薪资和其他补偿 (Previous Year Salaries and Other Compensation)',
      'total_fundraising_expenses_cy': '当年总筹款费用 (Current Year Total Fundraising Expenses)',
      'total_fundraising_expenses_py': '上年总筹款费用 (Previous Year Total Fundraising Expenses)',
      'other_expenses_cy': '当年其他费用 (Current Year Other Expenses)',
      'other_expenses_py': '上年其他费用 (Previous Year Other Expenses)',
      'revenue_less_expenses_cy': '当年收入减去支出 (Current Year Revenue Less Expenses)',
      'revenue_less_expenses_py': '上年收入减去支出 (Previous Year Revenue Less Expenses)',
      'total_liabilities_cy': '当年总负债 (Current Year Total Liabilities)',
      'total_liabilities_py': '上年总负债 (Previous Year Total Liabilities)',
      'net_assets_or_fund_balances_cy': '当年净资产或基金余额 (Current Year Net Assets or Fund Balances)',
      'net_assets_or_fund_balances_py': '上年净资产或基金余额 (Previous Year Net Assets or Fund Balances)',
    };

    return descriptions[fieldName] || '暂无描述';
  };

  const columns = [
    {
      title: '字段名称',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      render: (text) => (
        <Text code>{text}</Text>
      ),
    },
    {
      title: '数据类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (text) => (
        <Tag color="blue">{text}</Tag>
      ),
    },
    {
      title: '分类',
      key: 'category',
      width: 120,
      render: (_, record) => (
        <Tag color="green">{getFieldCategory(record.name)}</Tag>
      ),
    },
    {
      title: '描述',
      key: 'description',
      render: (_, record) => (
        <Text>{getFieldDescription(record.name)}</Text>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>
        <BookOutlined /> 变量描述
      </Title>
      <Text type="secondary">
        了解IRS Form 990数据集中各个字段的含义和用途
      </Text>

      <Divider />

      {/* 搜索框 */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>搜索字段</Text>
          <Search
            placeholder="输入字段名称关键词"
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
        <Descriptions title="数据集信息" bordered>
          <Descriptions.Item label="总字段数">{fields.length}</Descriptions.Item>
          <Descriptions.Item label="当前显示">{filteredFields.length}</Descriptions.Item>
          <Descriptions.Item label="数据来源">IRS Form 990</Descriptions.Item>
          <Descriptions.Item label="数据年份">2023</Descriptions.Item>
          <Descriptions.Item label="数据格式">CSV/Excel</Descriptions.Item>
          <Descriptions.Item label="更新时间">2024年</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 字段列表 */}
      <Card title="字段详情">
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
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          scroll={{ x: 800 }}
          size="middle"
        />
      </Card>

      {/* 使用说明 */}
      <Card title="使用说明" style={{ marginTop: 24 }}>
        <Paragraph>
          <Text strong>字段命名规则：</Text>
        </Paragraph>
        <ul>
          <li><Text code>_cy</Text> 后缀表示当前年份 (Current Year) 数据</li>
          <li><Text code>_py</Text> 后缀表示上一年 (Previous Year) 数据</li>
          <li>字段名称采用下划线分隔的英文命名</li>
          <li>所有金额字段以美元为单位</li>
        </ul>
        
        <Paragraph>
          <Text strong>数据来源：</Text>
        </Paragraph>
        <ul>
          <li>数据来源于IRS公开的Form 990表格</li>
          <li>包含非营利组织的财务和运营信息</li>
          <li>数据经过清洗和标准化处理</li>
        </ul>
      </Card>
    </div>
  );
};

export default VariableDescriptions; 