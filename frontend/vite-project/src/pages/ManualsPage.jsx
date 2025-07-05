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
      title: '数据预览',
      description: '了解数据集结构',
      icon: <EyeOutlined />,
      content: (
        <div>
          <Paragraph>
            在开始查询之前，建议先查看数据预览页面，了解：
          </Paragraph>
          <List
            size="small"
            dataSource={[
              '数据集包含的组织数量和覆盖范围',
              '各个字段的数据类型和含义',
              '数据的完整性和质量',
              '州分布和收入分布情况'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: '选择查询条件',
      description: '设置筛选条件',
      icon: <SearchOutlined />,
      content: (
        <div>
          <Paragraph>
            在查询表单中，您可以设置以下筛选条件：
          </Paragraph>
          <List
            size="small"
            dataSource={[
              '组织名称：支持模糊搜索',
              'EIN号码：精确或模糊匹配',
              '地理位置：按州和城市筛选',
              '特定字段：选择需要查看的字段',
              '结果数量：控制返回的记录数'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: '执行查询',
      description: '获取查询结果',
      icon: <SearchOutlined />,
      content: (
        <div>
          <Paragraph>
            点击查询按钮后，系统将：
          </Paragraph>
          <List
            size="small"
            dataSource={[
              '根据条件筛选数据',
              '返回匹配的记录',
              '显示分页信息',
              '提供导出功能'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
    {
      title: '结果处理',
      description: '分析和导出数据',
      icon: <DownloadOutlined />,
      content: (
        <div>
          <Paragraph>
            查询结果可以：
          </Paragraph>
          <List
            size="small"
            dataSource={[
              '在表格中查看详细信息',
              '按列排序和筛选',
              '导出为CSV格式',
              '进一步分析数据'
            ]}
            renderItem={(item) => <List.Item>• {item}</List.Item>}
          />
        </div>
      ),
    },
  ];

  const tips = [
    {
      title: '查询技巧',
      content: '使用组织名称的部分关键词可以获得更多匹配结果。例如，搜索"hospital"可以找到所有包含该词的组织。'
    },
    {
      title: '数据说明',
      content: '所有金额数据以美元为单位，_cy表示当前年份，_py表示上一年。'
    },
    {
      title: '性能优化',
      content: '建议设置合理的查询条件，避免返回过多数据影响查询速度。'
    },
    {
      title: '数据更新',
      content: '数据来源于IRS公开数据，定期更新。当前版本包含2023年的数据。'
    }
  ];

  return (
    <div>
      <Title level={2}>
        <BookOutlined /> 使用手册
      </Title>
      <Text type="secondary">
        了解如何使用IRS非营利组织数据平台进行数据查询和分析
      </Text>

      <Divider />

      {/* 快速开始 */}
      <Card title="快速开始" style={{ marginBottom: 24 }}>
        <Alert
          message="欢迎使用IRS非营利组织数据平台"
          description="本平台提供IRS Form 990数据的查询和分析功能，帮助您快速获取非营利组织的财务和运营信息。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Paragraph>
          <Text strong>主要功能：</Text>
        </Paragraph>
        <Space wrap>
          <Tag color="blue" icon={<SearchOutlined />}>数据查询</Tag>
          <Tag color="green" icon={<EyeOutlined />}>数据预览</Tag>
          <Tag color="orange" icon={<BookOutlined />}>变量描述</Tag>
          <Tag color="purple" icon={<DownloadOutlined />}>数据导出</Tag>
        </Space>
      </Card>

      {/* 使用步骤 */}
      <Card title="使用步骤" style={{ marginBottom: 24 }}>
        <Steps
          direction="vertical"
          current={-1}
          items={steps}
        />
      </Card>

      {/* 详细说明 */}
      <Card title="详细说明" style={{ marginBottom: 24 }}>
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
      <Card title="使用技巧" style={{ marginBottom: 24 }}>
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
      <Card title="常见问题" style={{ marginBottom: 24 }}>
        <List
          itemLayout="vertical"
          dataSource={[
            {
              question: '如何找到特定组织的财务信息？',
              answer: '在查询表单中输入组织名称或EIN号码，系统会返回匹配的记录。'
            },
            {
              question: '数据来源是什么？',
              answer: '数据来源于IRS公开的Form 990表格，包含非营利组织的财务和运营信息。'
            },
            {
              question: '如何导出查询结果？',
              answer: '在查询结果页面点击"导出"按钮，可以将数据下载为CSV格式。'
            },
            {
              question: '数据更新频率如何？',
              answer: '数据定期更新，当前版本包含2023年的数据。'
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
      <Card title="技术支持">
        <Paragraph>
          如果您在使用过程中遇到问题，可以：
        </Paragraph>
        <List
          size="small"
          dataSource={[
            '查看知识库页面获取更多帮助',
            '检查网络连接是否正常',
            '确认查询条件设置是否正确',
            '联系技术支持团队'
          ]}
          renderItem={(item) => <List.Item>• {item}</List.Item>}
        />
      </Card>
    </div>
  );
};

export default ManualsPage; 