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
      header: '数据相关',
      items: [
        {
          question: '什么是IRS Form 990？',
          answer: 'IRS Form 990是美国国税局要求大多数免税组织提交的年度信息申报表。它包含组织的财务信息、治理结构、项目活动等详细信息。'
        },
        {
          question: '数据更新频率如何？',
          answer: '数据来源于IRS公开数据，通常每年更新一次。当前版本包含2023年的数据。'
        },
        {
          question: '数据覆盖范围包括哪些组织？',
          answer: '数据覆盖美国境内的非营利组织，包括501(c)(3)慈善组织、医院、教育机构等。'
        }
      ]
    },
    {
      key: '2',
      header: '查询功能',
      items: [
        {
          question: '如何精确查找特定组织？',
          answer: '可以使用组织名称或EIN号码进行精确查找。EIN是唯一的雇主识别号码，可以确保找到正确的组织。'
        },
        {
          question: '支持哪些查询条件？',
          answer: '支持按组织名称、EIN、州、城市等条件查询，还支持模糊搜索和字段筛选。'
        },
        {
          question: '查询结果可以导出吗？',
          answer: '是的，查询结果可以导出为CSV格式，方便进一步分析。'
        }
      ]
    },
    {
      key: '3',
      header: '技术问题',
      items: [
        {
          question: '系统支持哪些浏览器？',
          answer: '建议使用Chrome、Firefox、Safari、Edge等现代浏览器，确保最佳体验。'
        },
        {
          question: '查询速度慢怎么办？',
          answer: '建议设置更具体的查询条件，避免返回过多数据。也可以减少结果数量限制。'
        },
        {
          question: '数据格式说明',
          answer: '所有金额数据以美元为单位，_cy表示当前年份，_py表示上一年。'
        }
      ]
    }
  ];

  const dataFields = [
    {
      category: '基本信息',
      fields: [
        'organization_name - 组织名称',
        'ein - 雇主识别号码',
        'state - 所在州',
        'city - 所在城市'
      ]
    },
    {
      category: '财务信息',
      fields: [
        'total_revenue_cy - 当年总收入',
        'total_assets_cy - 当年总资产',
        'total_expenses_cy - 当年总支出',
        'grants_paid_cy - 当年支付的资助'
      ]
    },
    {
      category: '运营信息',
      fields: [
        'number_of_individuals_employed_cy - 当年员工数量',
        'salaries_other_comp_cy - 当年薪资和其他补偿',
        'total_fundraising_expenses_cy - 当年总筹款费用'
      ]
    }
  ];

  return (
    <div>
      <Title level={2}>
        <QuestionCircleOutlined /> 知识库
      </Title>
      <Text type="secondary">
        常见问题解答和详细的使用指南
      </Text>

      <Divider />

      {/* 快速导航 */}
      <Card style={{ marginBottom: 24 }}>
        <Anchor
          items={[
            {
              key: 'faq',
              href: '#faq',
              title: '常见问题',
            },
            {
              key: 'data-guide',
              href: '#data-guide',
              title: '数据指南',
            },
            {
              key: 'best-practices',
              href: '#best-practices',
              title: '最佳实践',
            }
          ]}
        />
      </Card>

      {/* 常见问题 */}
      <Card id="faq" title="常见问题" style={{ marginBottom: 24 }}>
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
      <Card id="data-guide" title="数据指南" style={{ marginBottom: 24 }}>
        <Alert
          message="数据来源说明"
          description="本平台的数据来源于IRS公开的Form 990表格，经过清洗和标准化处理，确保数据的准确性和一致性。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Title level={4}>主要字段说明</Title>
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

        <Title level={4}>数据质量说明</Title>
        <List
          size="small"
          dataSource={[
            '数据来源于官方IRS文件，具有权威性',
            '经过标准化处理，确保格式一致',
            '包含数据完整性检查',
            '定期更新和维护'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>

      {/* 最佳实践 */}
      <Card id="best-practices" title="最佳实践" style={{ marginBottom: 24 }}>
        <Title level={4}>查询技巧</Title>
        <List
          itemLayout="vertical"
          dataSource={[
            {
              title: '使用精确关键词',
              content: '使用组织名称的准确拼写或EIN号码可以获得最精确的结果。'
            },
            {
              title: '组合查询条件',
              content: '结合多个查询条件可以缩小结果范围，提高查询效率。'
            },
            {
              title: '利用模糊搜索',
              content: '如果不确定完整名称，可以使用部分关键词进行模糊搜索。'
            },
            {
              title: '合理设置结果数量',
              content: '根据分析需求设置合适的结果数量，避免数据过多影响处理速度。'
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

        <Title level={4}>数据分析建议</Title>
        <List
          size="small"
          dataSource={[
            '对比不同年份的数据了解趋势变化',
            '分析同行业组织的财务表现',
            '关注关键财务指标如收入结构、支出比例',
            '结合地理位置分析区域差异'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>

      {/* 联系支持 */}
      <Card title="获取帮助">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="需要更多帮助？"
            description="如果您在使用过程中遇到问题，可以查看使用手册或联系技术支持团队。"
            type="success"
            showIcon
          />
          
          <List
            size="small"
            dataSource={[
              '查看使用手册了解详细操作步骤',
              '检查网络连接和浏览器设置',
              '确认查询条件是否正确设置',
              '联系技术支持获取专业帮助'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </Space>
      </Card>
    </div>
  );
};

export default KnowledgeBase; 