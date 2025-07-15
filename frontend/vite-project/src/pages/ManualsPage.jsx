import React from 'react';
import { 
  Card, 
  Typography, 
  Steps, 
  Divider, 
  Alert,
  Space,
  Tag,
  List
} from 'antd';
import { 
  BookOutlined,
  SearchOutlined,
  EyeOutlined,
  DownloadOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const ManualsPage = () => {
  const steps = [
    {
      title: 'Data Preview',
      description: 'Understand dataset structure',
      icon: <EyeOutlined />,
      content: (
        <div>
          <Paragraph>
            Before starting your query, it's recommended to view the data preview page to understand:
          </Paragraph>
          <List
            size="small"
            dataSource={[
              'Number of organizations and coverage scope in the dataset',
              'Data types and meanings of various fields',
              'Data completeness and quality',
              'State distribution and revenue distribution'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: 'Select Query Conditions',
      description: 'Set filtering criteria',
      icon: <SearchOutlined />,
      content: (
        <div>
          <Paragraph>
            In the query form, you can set the following filtering conditions:
          </Paragraph>
          <List
            size="small"
            dataSource={[
              'Organization name: Supports fuzzy search',
              'EIN number: Exact or fuzzy matching',
              'Geographic location: Filter by state and city',
              'Specific fields: Select fields you need to view',
              'Result quantity: Control the number of returned records'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: 'Execute Query',
      description: 'Get query results',
      icon: <SearchOutlined />,
      content: (
        <div>
          <Paragraph>
            After clicking the query button, the system will:
          </Paragraph>
          <List
            size="small"
            dataSource={[
              'Filter data based on conditions',
              'Return matching records',
              'Display pagination information',
              'Provide export functionality'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: 'Result Processing',
      description: 'Analyze and export data',
      icon: <DownloadOutlined />,
      content: (
        <div>
          <Paragraph>
            Query results can be:
          </Paragraph>
          <List
            size="small"
            dataSource={[
              'View detailed information in tables',
              'Sort and filter by columns',
              'Export to CSV format',
              'Further analyze data'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
  ];

  const tips = [
    {
      title: 'Query Tips',
      content: 'Using partial keywords from organization names can yield more matching results. For example, searching for "hospital" will find all organizations containing that word.'
    },
    {
      title: 'Data Description',
      content: 'All monetary data is in US dollars, _cy indicates current year, _py indicates previous year.'
    },
    {
      title: 'Performance Optimization',
      content: 'It is recommended to set reasonable query conditions to avoid returning too much data that affects query speed.'
    },
    {
      title: 'Data Updates',
      content: 'Data is sourced from IRS public data and updated regularly. The current version contains 2023 data.'
    }
  ];

  return (
    <div>
      <Title level={2}>
        <BookOutlined /> User Manual
      </Title>
      <Text type="secondary">
        Learn how to use the IRS nonprofit data platform for data querying and analysis
      </Text>

      <Divider />

      {/* 快速开始 */}
      <Card title="Quick Start" style={{ marginBottom: 24 }}>
        <Alert
          message="Welcome to the IRS Nonprofit Data Platform"
          description="This platform provides query and analysis functions for IRS Form 990 data, helping you quickly obtain financial and operational information of nonprofit organizations."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Paragraph>
          <Text strong>Main Features:</Text>
        </Paragraph>
        <Space wrap>
          <Tag color="blue" icon={<SearchOutlined />}>Data Query</Tag>
          <Tag color="green" icon={<EyeOutlined />}>Data Preview</Tag>
          <Tag color="orange" icon={<BookOutlined />}>Variable Descriptions</Tag>
          <Tag color="purple" icon={<DownloadOutlined />}>Data Export</Tag>
        </Space>
      </Card>

      {/* 使用步骤 */}
      <Card title="Usage Steps" style={{ marginBottom: 24 }}>
        <Steps
          direction="vertical"
          current={-1}
          items={steps}
        />
      </Card>

      {/* 详细说明 */}
      <Card title="Detailed Instructions" style={{ marginBottom: 24 }}>
        {steps.map((step, index) => (
          <div key={index}>
            <Title level={4}>
              {index + 1}. {step.title}
            </Title>
            {step.content}
            {index < steps.length - 1 && <Divider />}
          </div>
        ))}
      </Card>

      {/* 使用技巧 */}
      <Card title="Usage Tips" style={{ marginBottom: 24 }}>
        <List
          itemLayout="vertical"
          dataSource={tips}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={item.title}
                description={item.content}
              />
            </List.Item>
          )}
        />
      </Card>

      {/* 常见问题 */}
      <Card title="Frequently Asked Questions" style={{ marginBottom: 24 }}>
        <List
          itemLayout="vertical"
          dataSource={[
            {
              question: 'How to find financial information for a specific organization?',
              answer: 'Enter the organization name or EIN number in the query form, and the system will return matching records.'
            },
            {
              question: 'What is the data source?',
              answer: 'Data is sourced from publicly available IRS Form 990 filings, containing financial and operational information of nonprofit organizations.'
            },
            {
              question: 'How to export query results?',
              answer: 'Click the "Export" button on the query results page to download data in CSV format.'
            },
            {
              question: 'What is the data update frequency?',
              answer: 'Data is updated regularly. The current version contains 2023 data.'
            }
          ]}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space>
                    <QuestionCircleOutlined />
                    {item.question}
                  </Space>
                }
                description={item.answer}
              />
            </List.Item>
          )}
        />
      </Card>

      {/* 联系支持 */}
      <Card title="Technical Support">
        <Paragraph>
          If you encounter problems during use, you can:
        </Paragraph>
        <List
          size="small"
          dataSource={[
            'Check the knowledge base page for more help',
            'Verify that your network connection is working properly',
            'Confirm that query conditions are set correctly',
            'Contact the technical support team'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>
    </div>
  );
};

export default ManualsPage; 