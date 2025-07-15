import React, { useState } from 'react';
import { 
  Card, 
  Typography, 
  Collapse, 
  Tag, 
  Space, 
  Divider,
  Alert,
  List,
  Anchor
} from 'antd';
import { 
  QuestionCircleOutlined,
  InfoCircleOutlined,
  BookOutlined,
  FileTextOutlined,
  DatabaseOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const KnowledgeBase = () => {
  const [activeKey, setActiveKey] = useState(['1']);

  const faqData = [
    {
      key: '1',
      header: 'Data Related',
      items: [
        {
          question: 'What is IRS Form 990?',
          answer: 'IRS Form 990 is an annual information return that most tax-exempt organizations are required to file with the IRS. It contains detailed information about the organization\'s finances, governance structure, and program activities.'
        },
        {
          question: 'How frequently is the data updated?',
          answer: 'Data is sourced from IRS public data and is typically updated annually. The current version contains 2023 data.'
        },
        {
          question: 'What organizations are covered in the data?',
          answer: 'The data covers nonprofit organizations within the United States, including 501(c)(3) charitable organizations, hospitals, educational institutions, etc.'
        }
      ]
    },
    {
      key: '2',
      header: 'Query Functions',
      items: [
        {
          question: 'How to precisely find a specific organization?',
          answer: 'You can use the organization name or EIN number for precise searches. EIN is a unique employer identification number that ensures you find the correct organization.'
        },
        {
          question: 'What query conditions are supported?',
          answer: 'Supports queries by organization name, EIN, state, city, and other conditions. Also supports fuzzy search and field filtering.'
        },
        {
          question: 'Can query results be exported?',
          answer: 'Yes, query results can be exported in CSV format for further analysis.'
        }
      ]
    },
    {
      key: '3',
      header: 'Technical Issues',
      items: [
        {
          question: 'Which browsers does the system support?',
          answer: 'We recommend using modern browsers such as Chrome, Firefox, Safari, Edge for the best experience.'
        },
        {
          question: 'What to do if queries are slow?',
          answer: 'We recommend setting more specific query conditions to avoid returning too much data. You can also reduce the result quantity limit.'
        },
        {
          question: 'Data format explanation',
          answer: 'All monetary data is in US dollars, _cy indicates current year, _py indicates previous year.'
        }
      ]
    }
  ];

  const dataFields = [
    {
      category: 'Basic Information',
      fields: [
        'organization_name - Organization Name',
        'ein - Employer Identification Number',
        'state - State',
        'city - City'
      ]
    },
    {
      category: 'Financial Information',
      fields: [
        'total_revenue_cy - Current Year Total Revenue',
        'total_assets_cy - Current Year Total Assets',
        'total_expenses_cy - Current Year Total Expenses',
        'grants_paid_cy - Current Year Grants Paid'
      ]
    },
    {
      category: 'Operational Information',
      fields: [
        'number_of_individuals_employed_cy - Current Year Number of Employees',
        'salaries_other_comp_cy - Current Year Salaries and Other Compensation',
        'total_fundraising_expenses_cy - Current Year Total Fundraising Expenses'
      ]
    }
  ];

  return (
    <div>
      <Title level={2}>
        <QuestionCircleOutlined /> Knowledge Base
      </Title>
      <Text type="secondary">
        Frequently asked questions and detailed usage guides
      </Text>

      <Divider />

      {/* 快速导航 */}
      <Card style={{ marginBottom: 24 }}>
        <Anchor
          items={[
            {
              key: 'faq',
              href: '#faq',
              title: 'FAQ',
            },
            {
              key: 'data-guide',
              href: '#data-guide',
              title: 'Data Guide',
            },
            {
              key: 'best-practices',
              href: '#best-practices',
              title: 'Best Practices',
            }
          ]}
        />
      </Card>

      {/* 常见问题 */}
      <Card id="faq" title="Frequently Asked Questions" style={{ marginBottom: 24 }}>
        <Collapse 
          activeKey={activeKey} 
          onChange={setActiveKey}
          expandIconPosition="end"
        >
          {faqData.map((section) => (
            <Panel 
              header={
                <Space>
                  <InfoCircleOutlined />
                  {section.header}
                </Space>
              } 
              key={section.key}
            >
              <List
                itemLayout="vertical"
                dataSource={section.items}
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
            </Panel>
          ))}
        </Collapse>
      </Card>

      {/* 数据指南 */}
      <Card id="data-guide" title="Data Guide" style={{ marginBottom: 24 }}>
        <Alert
          message="Data Source Description"
          description="The platform's data is sourced from publicly available IRS Form 990 filings, cleaned and standardized to ensure data accuracy and consistency."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Title level={4}>Main Field Descriptions</Title>
        {dataFields.map((category, index) => (
          <div key={index} style={{ marginBottom: 16 }}>
            <Text strong>{category.category}：</Text>
            <List
              size="small"
              dataSource={category.fields}
              renderItem={(field) => (
                <List.Item>
                  <Text code>{field}</Text>
                </List.Item>
              )}
            />
          </div>
        ))}

        <Divider />

        <Title level={4}>Data Quality Description</Title>
        <List
          size="small"
          dataSource={[
            'Data sourced from official IRS files, ensuring authority',
            'Standardized processing to ensure format consistency',
            'Includes data integrity checks',
            'Regular updates and maintenance'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>

      {/* 最佳实践 */}
      <Card id="best-practices" title="Best Practices" style={{ marginBottom: 24 }}>
        <Title level={4}>Query Tips</Title>
        <List
          itemLayout="vertical"
          dataSource={[
            {
              title: 'Use Precise Keywords',
              content: 'Using accurate spelling of organization names or EIN numbers can yield the most precise results.'
            },
            {
              title: 'Combine Query Conditions',
              content: 'Combining multiple query conditions can narrow down results and improve query efficiency.'
            },
            {
              title: 'Utilize Fuzzy Search',
              content: 'If you\'re unsure of the complete name, you can use partial keywords for fuzzy search.'
            },
            {
              title: 'Set Reasonable Result Quantities',
              content: 'Set appropriate result quantities based on analysis needs to avoid too much data affecting processing speed.'
            }
          ]}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={item.title}
                description={item.content}
              />
            </List.Item>
          )}
        />

        <Divider />

        <Title level={4}>Data Analysis Recommendations</Title>
        <List
          size="small"
          dataSource={[
            'Compare data from different years to understand trend changes',
            'Analyze financial performance of organizations in the same industry',
            'Focus on key financial indicators such as revenue structure and expense ratios',
            'Combine geographic location analysis for regional differences'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>

      {/* 联系支持 */}
      <Card title="Get Help">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="Need More Help?"
            description="If you encounter problems during use, you can check the user manual or contact the technical support team."
            type="success"
            showIcon
          />
          
          <List
            size="small"
            dataSource={[
              'Check the user manual for detailed operation steps',
              'Verify network connection and browser settings',
              'Confirm that query conditions are set correctly',
              'Contact technical support for professional assistance'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </Space>
      </Card>
    </div>
  );
};

export default KnowledgeBase; 